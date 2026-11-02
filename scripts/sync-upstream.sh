#!/usr/bin/env bash
# ============================================================================
# sync-upstream.sh — Validador local: os mods ainda aplicam no upstream atual?
#
# Uso (debug local):
#   ./scripts/sync-upstream.sh
#
# Não altera nada no repo: apenas clona o upstream num diretório temporário,
# aplica os mods e roda o smoke test. O fluxo oficial de sync/release é o
# workflow .github/workflows/weekly-pipeline.yml (roda sozinho na Sunday 23h UTC).
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMP_DIR="$(mktemp -d)"

trap 'rm -rf "${TEMP_DIR}"' EXIT

echo "==> SHA mais recente do upstream (branch master — default real):"
UPSTREAM_SHA=$(curl -sf https://api.github.com/repos/ps2homebrew/Open-PS2-Loader/commits/master \
    | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")
echo "    ${UPSTREAM_SHA:0:7}"

if [ -f "${ROOT_DIR}/upstream.sha" ]; then
    echo "    Registrado: $(head -c7 "${ROOT_DIR}/upstream.sha")"
fi

echo
echo "==> Clonando upstream para teste..."
git clone --depth 1 -b master https://github.com/ps2homebrew/Open-PS2-Loader.git "${TEMP_DIR}/opl" 2>&1 | tail -1

echo "==> Aplicando mods (validação rígida por âncoras)..."
bash "${SCRIPT_DIR}/apply-mods.sh" "${TEMP_DIR}/opl" > /tmp/opl-apply-test.log 2>&1 || {
    echo "FALHOU — log completo:"
    tail -30 /tmp/opl-apply-test.log
    echo
    echo ">>> O upstream mudou e quebrou uma âncora dos mods."
    echo ">>> Corrija mods/apply_mods.py apontando para as novas âncoras."
    exit 1
}

echo "==> Smoke test do Makefile..."
(cd "${TEMP_DIR}/opl" && make -n oplversion > /dev/null 2>&1) \
    || { echo "FALHOU — Makefile não faz parse."; exit 1; }

echo
echo "✅ Mods aplicam limpo no upstream ${UPSTREAM_SHA:0:7}."
echo "   Para sincronizar de verdade, rode o workflow 'Pipeline Semanal' na aba Actions"
echo "   (ou aguarde o próximo domingo 23:00 UTC)."
