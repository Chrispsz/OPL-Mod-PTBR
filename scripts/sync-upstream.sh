#!/usr/bin/env bash
# ============================================================================
# sync-upstream.sh — Sincroniza o mod com a última versão do upstream OPL
#
# Uso local (para debug):
#   ./scripts/sync-upstream.sh
#
# Em CI/CD, o workflow .github/workflows/sync-upstream.yml faz isso
# automaticamente toda semana.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UPSTREAM_SHA_FILE="${ROOT_DIR}/upstream.sha"
TEMP_DIR="$(mktemp -d)"

trap 'rm -rf "${TEMP_DIR}"' EXIT

cd "${ROOT_DIR}"

# 1. Obter SHA mais recente do upstream
echo "==> Obtendo SHA mais recente do upstream..."
UPSTREAM_SHA=$(curl -sf https://api.github.com/repos/ps2homebrew/Open-PS2-Loader/commits/main | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")
UPSTREAM_SHORT="${UPSTREAM_SHA:0:7}"
echo "    Upstream: ${UPSTREAM_SHORT}"

CURRENT_SHA=""
if [ -f "${UPSTREAM_SHA_FILE}" ]; then
    CURRENT_SHA="$(cat "${UPSTREAM_SHA_FILE}")"
    echo "    Atual:    ${CURRENT_SHA:0:7}"
fi

if [ "${CURRENT_SHA}" = "${UPSTREAM_SHA}" ]; then
    echo "    Sem mudanças. Já estamos sincronizados."
    exit 0
fi

echo
echo "==> Clonando upstream para teste de aplicação dos mods..."
git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git "${TEMP_DIR}/opl" 2>&1 | tail -2

echo "==> Aplicando mods no clone fresco..."
bash "${SCRIPT_DIR}/apply-mods.sh" "${TEMP_DIR}/opl"

echo "==> Testando build..."
cd "${TEMP_DIR}/opl"
# Apenas verificar que o build inicia sem erros de Makefile/patch
make -n languages 2>&1 | head -5
make -n oplversion 2>&1 | head -2

echo
echo "==> Validação OK — mods aplicam limpo no novo upstream."
echo "    Atualize upstream.sha e faça commit."
echo "${UPSTREAM_SHA}" > "${UPSTREAM_SHA_FILE}"

cd "${ROOT_DIR}"
echo
echo "Para finalizar:"
echo "  git add upstream.sha"
echo "  git commit -m 'chore: sync upstream to ${UPSTREAM_SHORT}'"
echo "  git push"
