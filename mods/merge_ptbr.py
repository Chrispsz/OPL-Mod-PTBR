#!/usr/bin/env python3
"""
Cria `lng_tmpl/_base_ptbr.yml` mesclando as strings em inglês de `_base.yml`
com as traduções PT-BR de `lng_src/Portuguese_BR.yml`.

O resultado é um arquivo _base.yml equivalente, porém com todas as strings
`gui_strings[].string` trocadas pelas traduções PT-BR. Isso faz com que o
`lang_compiler.py --make_source` gere `src/lang_internal.c` com PT-BR embutido
no ELF (idioma padrão, sem precisar de arquivo .lng externo).
"""
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BASE_YML = REPO_ROOT / "lng_tmpl" / "_base.yml"
PTBR_YML = REPO_ROOT / "lng_src" / "Portuguese_BR.yml"
OUT_YML = REPO_ROOT / "lng_tmpl" / "_base_ptbr.yml"

# Mantém strings multi-linha com bloco literal
def _represent_str(self, data):
    style = '|' if '\n' in data else ''
    return self.represent_scalar('tag:yaml.org,2002:str', data, style=style)

yaml.add_representer(str, _represent_str)

DUMP_ARGS = dict(encoding='utf-8', allow_unicode=True, sort_keys=False, default_flow_style=False)


def main():
    if not BASE_YML.exists():
        print(f"ERRO: {BASE_YML} não encontrado.", file=sys.stderr)
        return 1
    if not PTBR_YML.exists():
        print(f"ERRO: {PTBR_YML} não encontrado.", file=sys.stderr)
        print("       Rode `bash download_lng.sh` antes.", file=sys.stderr)
        return 1

    with BASE_YML.open('r', encoding='utf-8') as f:
        base = yaml.safe_load(f)
    with PTBR_YML.open('r', encoding='utf-8') as f:
        ptbr = yaml.safe_load(f)

    translations = ptbr.get('translations', {}) or {}
    substituted = 0
    untranslated = 0

    for sdef in base.get('gui_strings', []):
        label = sdef['label']
        if label not in translations:
            # Mantém o inglês original se não houver tradução
            untranslated += 1
            continue
        tr = translations[label]
        if isinstance(tr, str):
            sdef['string'] = tr
            substituted += 1
        elif isinstance(tr, list):
            # Format: [status, {original: ...}] ou [status, {original: ...}, {comment: ...}]
            if 'same' in tr or 'untranslated' in tr:
                # Mantém inglês original (já está em sdef['string'])
                untranslated += 1
                continue
            # Caso raro: tradução direta como lista
            if len(tr) >= 1 and isinstance(tr[0], str) and tr[0] not in ('same', 'untranslated'):
                sdef['string'] = tr[0]
                substituted += 1
        elif isinstance(tr, dict) and 'original' in tr:
            # Mesma estrutura aninhada
            untranslated += 1

    # Mantemos o nome do array como `internalEnglish` para compatibilidade com
    # include/lang.h (`extern char *internalEnglish[LANG_STR_COUNT];`). O nome
    # é apenas um símbolo — o conteúdo passa a ser PT-BR.
    base['string_array_name'] = 'internalEnglish'
    base['comment_for_template_header'] = (
        "Versão interna PT-BR gerada automaticamente pelo merge_ptbr.py.\n"
        "NÃO EDITAR — regerar a partir de lng_tmpl/_base.yml + lng_src/Portuguese_BR.yml."
    )

    # Remove comentários específicos de template (não usados para make_source)
    base.pop('comments_for_template_labels', None)

    with OUT_YML.open('w', encoding='utf-8') as f:
        yaml.dump(base, f, **DUMP_ARGS)

    total = substituted + untranslated
    print(f"OK: gerado {OUT_YML.relative_to(REPO_ROOT)}")
    print(f"    {substituted}/{total} strings substituídas por PT-BR")
    if untranslated:
        print(f"    {untranslated} strings mantidas em inglês (sem tradução disponível)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
