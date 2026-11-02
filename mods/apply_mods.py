#!/usr/bin/env python3
"""
apply_mods.py — Aplica os mods PT-BR + Balanced-Optimized no clone upstream do OPL.

Estratégia: edição por ÂNCORAS DE CONTEÚDO (não por patches de linha).

Cada modificação declara uma âncora de texto exata e a contagem esperada de
ocorrências. Se qualquer âncora não bater (0 ou mais de 1), o script aborta
com erro claro apontando a âncora quebrada — sinal de que o upstream mudou e
o mod precisa de revisão manual.

Garantias:
  - Nunca aplica "pela metade": ou todas as âncoras batem, ou nada é salvo.
  - Nunca aplica errado em silêncio: contagens verificadas uma a uma.
  - NÃO é idempotente por design: rode SEMPRE em um clone fresco do upstream
    (scripts/apply-mods.sh e o CI garantem isso).

Uso:
    python3 mods/apply_mods.py [diretório-do-opl]
"""
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class ModError(Exception):
    pass


def replace_exact(text: str, anchor: str, replacement: str, label: str,
                  expected: int = 1) -> str:
    """Substitui `anchor` por `replacement` verificando a contagem exata."""
    count = text.count(anchor)
    if count != expected:
        raise ModError(
            f"Âncora '{label}' encontrada {count}x (esperado {expected}).\n"
            f"  >>> O upstream mudou. Revise a âncora:\n"
            f"  >>> {anchor.splitlines()[0][:100]}"
        )
    return text.replace(anchor, replacement)


def replace_translations_block(text: str) -> str:
    """Substitui o bloco multi-linha TRANSLATIONS por 'TRANSLATIONS = Portuguese_BR'.

    O upstream mantém a lista em 2-3 linhas com continuação '\\'. Achamos a
    linha inicial, consumimos as continuações e trocamos o bloco inteiro.
    """
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.startswith("TRANSLATIONS = "):
            start = i
            break
    if start is None:
        raise ModError(
            "Âncora 'TRANSLATIONS = ' não encontrada no Makefile.\n"
            "  >>> O upstream mudou a seção de idiomas."
        )
    end = start
    while lines[end].rstrip().endswith("\\"):
        end += 1
        if end >= len(lines):
            raise ModError("Bloco TRANSLATIONS malformado (continuação infinita).")
    block = "TRANSLATIONS = Portuguese_BR  # Mod: idioma único PT-BR embutido"
    lines[start:end + 1] = [block]
    return "\n".join(lines)


def apply_makefile(source: str) -> str:
    text = source

    # 1. PADEMU desativado (build enxuta, ~120KB economizados)
    text = replace_exact(
        text,
        "PADEMU ?= 1",
        "# Desativado nesta build customizada (não escolhido pelo usuário)\nPADEMU ?= 0",
        "Makefile: PADEMU off",
    )

    # 2. Idioma único PT-BR
    text = replace_translations_block(text)

    # 3. Variável da base PT-BR (declaração, junto das outras)
    text = replace_exact(
        text,
        "BASE_LANGUAGE = $(LNG_TMPL_DIR)_base.yml\nINTERNAL_LANGUAGE_C = src/lang_internal.c",
        "BASE_LANGUAGE = $(LNG_TMPL_DIR)_base.yml\n"
        "# Versão PT-BR do _base.yml: gera lang_internal.c com PT-BR embutido no ELF\n"
        "INTERNAL_BASE_LANGUAGE = $(LNG_TMPL_DIR)_base_ptbr.yml\n"
        "INTERNAL_LANGUAGE_C = src/lang_internal.c",
        "Makefile: declaração INTERNAL_BASE_LANGUAGE",
    )

    # 4. Cadeia de regras: _base_ptbr.yml -> lang_internal.c
    text = replace_exact(
        text,
        "$(INTERNAL_LANGUAGE_C): $(BASE_LANGUAGE) $(LANG_COMPILER)\n"
        "\tpython3 $(LANG_COMPILER) --make_source --base $< $@",
        "$(INTERNAL_BASE_LANGUAGE): $(BASE_LANGUAGE) $(LNG_SRC_DIR)Portuguese_BR.yml merge_ptbr.py\n"
        "\tpython3 merge_ptbr.py\n"
        "\n"
        "# Gera lang_internal.c com strings PT-BR embutidas (em vez de inglês)\n"
        "$(INTERNAL_LANGUAGE_C): $(INTERNAL_BASE_LANGUAGE) $(LANG_COMPILER)\n"
        "\tpython3 $(LANG_COMPILER) --make_source --base $< $@",
        "Makefile: regra lang_internal.c",
    )

    return text


def apply_opl_c(source: str) -> str:
    text = source

    # Perfil Balanced-Optimized: defaults de cache oficiais (pesquisa PSX-Place:
    # caches maiores deixam ZSO mais lento). Apenas documentado.
    text = replace_exact(
        text,
        "    bdmCacheSize = 16;\n    hddCacheSize = 8;\n    smbCacheSize = 16;",
        "    // Mod (Balanced-Optimized): caches no default oficial.\n"
        "    // Pesquisa PSX-Place confirma: valores maiores deixam ZSO mais lento.\n"
        "    bdmCacheSize = 16;\n    hddCacheSize = 8;\n    smbCacheSize = 16;",
        "opl.c: caches oficiais documentados",
    )

    # Device default = USB (BDM). Par com gAutosort desambigua da outra
    # ocorrência de 'gDefaultDevice = APP_MODE;' (em applyConfig).
    text = replace_exact(
        text,
        "    gDefaultDevice = APP_MODE;\n    gAutosort = 1;",
        "    gDefaultDevice = BDM_MODE; // Mod: USB default (universal em todo PS2)\n"
        "    gAutosort = 1;",
        "opl.c: default device = USB",
    )

    # UX melhorada (defaults on)
    for var in ("gAutoRefresh", "gHDDGameListCache", "gEnableWrite",
                "gRememberLastPlayed", "gEnableNotifications", "gEnableArt",
                "gWideScreen", "gEnableSFX", "gEnableBootSND"):
        text = replace_exact(text, f"    {var} = 0;", f"    {var} = 1;",
                             f"opl.c: {var} = 1")

    # USB ativo no boot; HDD/ETH/APP permanecem desativados (reativáveis via Settings)
    text = replace_exact(
        text,
        "    gBDMStartMode = START_MODE_DISABLED;",
        "    gBDMStartMode = START_MODE_AUTO; // Mod: USB ativo no boot",
        "opl.c: BDM start mode = AUTO",
    )

    return text


def sanity_check(makefile: str, opl_c: str) -> None:
    """Valida o RESULTADO final — o que não pode faltar depois dos mods."""
    required_makefile = [
        "PADEMU ?= 0",
        "TRANSLATIONS = Portuguese_BR",
        "INTERNAL_BASE_LANGUAGE = $(LNG_TMPL_DIR)_base_ptbr.yml",
        "$(INTERNAL_BASE_LANGUAGE): $(BASE_LANGUAGE) $(LNG_SRC_DIR)Portuguese_BR.yml merge_ptbr.py",
        "$(INTERNAL_LANGUAGE_C): $(INTERNAL_BASE_LANGUAGE) $(LANG_COMPILER)",
    ]
    required_opl_c = [
        "gDefaultDevice = BDM_MODE;",
        "gBDMStartMode = START_MODE_AUTO;",
        "gAutoRefresh = 1;",
        "gEnableWrite = 1;",
        "gRememberLastPlayed = 1;",
        "gEnableNotifications = 1;",
        "gEnableArt = 1;",
        "gWideScreen = 1;",
        "gEnableSFX = 1;",
        "gEnableBootSND = 1;",
    ]
    forbidden_makefile = ["PADEMU ?= 1"]
    forbidden_opl_c = [
        "gDefaultDevice = APP_MODE;\n    gAutosort = 1;",
        "gBDMStartMode = START_MODE_DISABLED;",
    ]

    for req in required_makefile:
        if req not in makefile:
            raise ModError(f"Pós-validação Makefile falhou: ausente '{req}'")
    for req in required_opl_c:
        if req not in opl_c:
            raise ModError(f"Pós-validação opl.c falhou: ausente '{req}'")
    for bad in forbidden_makefile:
        if bad in makefile:
            raise ModError(f"Pós-validação Makefile falhou: ainda presente '{bad}'")
    for bad in forbidden_opl_c:
        if bad in opl_c:
            raise ModError(f"Pós-validação opl.c falhou: ainda presente '{bad}'")


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "opl")
    makefile_path = target / "Makefile"
    opl_c_path = target / "src" / "opl.c"

    if not makefile_path.is_file() or not opl_c_path.is_file():
        print(f"ERRO: '{target}' não parece ser um clone do OPL "
              f"(Makefile/src/opl.c ausentes).", file=sys.stderr)
        return 1

    try:
        mk = apply_makefile(makefile_path.read_text(encoding="utf-8"))
        oc = apply_opl_c(opl_c_path.read_text(encoding="utf-8"))
        sanity_check(mk, oc)
    except ModError as e:
        print(f"ERRO ao aplicar mods: {e}", file=sys.stderr)
        return 1

    # Só grava depois de TODAS as âncoras + pós-validação passarem.
    makefile_path.write_text(mk, encoding="utf-8")
    opl_c_path.write_text(oc, encoding="utf-8")

    print("Mods aplicados com sucesso:")
    print("  - Makefile: PADEMU off, idioma único PT-BR, cadeia _base_ptbr.yml")
    print("  - src/opl.c: USB default/auto, UX defaults on (Balanced-Optimized)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
