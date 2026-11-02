#!/usr/bin/env bash
# ============================================================================
# apply-mods.sh — Aplica os mods PT-BR + Balanced-Optimized num clone do OPL
#
# Uso:
#   ./scripts/apply-mods.sh [diretório-do-opl]
#
# Pipeline interno (todas as etapas falham RUIDOSAMENTE em caso de problema):
#   1. mods/apply_mods.py   — edições por âncoras de conteúdo (Makefile + opl.c)
#   2. download_lng.sh      — fontes de tradução do OPL-lang (se ausentes)
#   3. merge_ptbr.py        — mescla PT-BR no _base.yml -> _base_ptbr.yml
# ============================================================================
set -euo pipefail

TARGET="${1:-opl}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODS_DIR="$(cd "${SCRIPT_DIR}/../mods" && pwd)"

if [ ! -f "${TARGET}/Makefile" ] || [ ! -f "${TARGET}/src/opl.c" ]; then
    echo "ERRO: '${TARGET}' não parece ser um clone do OPL." >&2
    echo "       Clone o upstream primeiro:" >&2
    echo "       git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git ${TARGET}" >&2
    exit 1
fi

echo "==> Aplicando mods em ${TARGET}..."

echo "   [1/3] Edições por âncoras (Makefile + src/opl.c)..."
python3 "${MODS_DIR}/apply_mods.py" "${TARGET}"

echo "   [2/3] Copiando merge_ptbr.py..."
cp "${MODS_DIR}/merge_ptbr.py" "${TARGET}/merge_ptbr.py"
chmod +x "${TARGET}/merge_ptbr.py"

if [ ! -d "${TARGET}/lng_src" ]; then
    echo "   [2/3] Baixando fontes de tradução (lng_src)..."
    (cd "${TARGET}" && bash download_lng.sh)
fi

# lwNBD é opcional: o build continua sem ele.
if [ ! -d "${TARGET}/thirdparty/lwNBD" ] && [ -f "${TARGET}/download_lwNBD.sh" ]; then
    echo "   [opcional] Baixando lwNBD..."
    (cd "${TARGET}" && bash download_lwNBD.sh) || echo "     (lwNBD falhou — build continua sem ele)"
fi

echo "   [3/3] Gerando lng_tmpl/_base_ptbr.yml..."
(cd "${TARGET}" && python3 merge_ptbr.py)

if [ ! -f "${TARGET}/lng_tmpl/_base_ptbr.yml" ]; then
    echo "ERRO: _base_ptbr.yml não foi gerado." >&2
    exit 1
fi

echo
echo "===================================================="
echo "  MODS APLICADOS COM SUCESSO"
echo "===================================================="
echo
echo "Para compilar:"
echo "  cd ${TARGET}"
echo "  make -j\$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0"
