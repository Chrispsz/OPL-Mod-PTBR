# DEVLOG — OPL Mod PT-BR

## 2026-11-02 — Revivificação completa (projeto funcional e inquebrável)

### Diagnóstico (por que estava morto)

1. **Patch 001 quebrado**: upstream adicionou Galician/Serbian à lista
   TRANSLATIONS; o patch de linha não aplicava mais → release.yml falhava
   em "Apply mods" desde 19/10.
2. **Tag morta v1.2.0-Beta-ptbr.7**: auto-release criava tag SEM validar
   que os mods aplicavam/buildavam.
3. **build.yml nunca tinha executado** (0 runs) — badge de build mentia.
4. **Race**: sync-upstream.yml e auto-release.yml no mesmo cron, ambos
   gravando upstream.sha.
5. **Branch upstream errada**: workflows monitoravam `commits/main` do
   upstream (congelada em 2025-02, c8cad1b) em vez de `master` (default
   real, ativa) — detecção de sync nunca via mudanças reais.
6. **README desatualizado**: perfil "Performance" (era Balanced), patches
   antigos, conf_opl.cfg inexistente, estimativa de tamanho errada.

### Correções

- **mods/apply_mods.py** (novo): mods por âncoras de conteúdo com fail-loud
  e pós-validação — substitui os patches .patch. Nunca aplica pela metade;
  se o upstream muda o código, o erro aponta a âncora exata que quebrou.
- **fix cwd**: apply-mods.sh rodava download_lng.sh/merge fora do TARGET.
- **weekly-pipeline.yml** (novo): único fluxo sync+release. NUNCA cria tag
  antes de validar a build real (dispatch build.yml + `gh run watch`).
  Falha → issue `upstream-sync` com link do run. Sem mais tags mortas.
- **build.yml**: validação pós-build (ELF MIPS magic, tamanho 0.5–5 MB,
  PT-BR embutido: 200+ escapes \u00XX vs 0 do inglês — calibrado localmente).
- **release.yml**: shell bash por-step (ps2dev/ps2dev é Alpine SEM bash —
  o primeiro step roda em sh e instala o bash), `set -euo pipefail`,
  URLs dos 7 assets externos verificadas (todas 200 OK).
- **Branch master**: commits/master + `clone -b master` explícito em todos.
- **jq no lugar de python inline** no YAML (indentação quebrava o -c).

### Verificação (tudo no GitHub Actions, real)

- Build em push: **VERDE** (pela 1ª vez na história do repo)
- Pipeline force=true: validação → SHAs → tag ptbr.7 → **release publicada**
  (Kit PS2 3.1 MB + Linux Tools 44.7 MB)
- Pipeline force=false: **auto-detecção** da correção de branch (c8cad1b →
  b3a2199) → validação → tag ptbr.8 → release — self-healing provado
- Merge PT-BR: 301/329 strings substituídas (28 sem tradução no lang repo)

### Estado final

- main verde, 2 releases vivas (ptbr.7, ptbr.8), SHAs corretos gravados
- Domingo 23:00 UTC: pipeline roda sozinho; se o upstream não mudar, sai
  sem trabalho; se mudar, valida → release; se quebrar, issue automática
