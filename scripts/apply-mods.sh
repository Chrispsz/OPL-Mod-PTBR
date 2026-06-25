#!/usr/bin/env bash
# ============================================================================
# apply-mods.sh — Aplica os mods PT-BR + Performance no clone upstream do OPL
#
# Uso:
#   ./scripts/apply-mods.sh [diretório-do-opl]
#
# Se o diretório não for passado, usa "opl/" por padrão.
# ============================================================================
set -euo pipefail

TARGET="${1:-opl}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODS_DIR="$(cd "${SCRIPT_DIR}/../mods" && pwd)"

if [ ! -d "${TARGET}" ]; then
    echo "ERRO: diretório '${TARGET}' não existe." >&2
    echo "       Clone o upstream primeiro:" >&2
    echo "       git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git ${TARGET}" >&2
    exit 1
fi

if [ ! -f "${TARGET}/Makefile" ]; then
    echo "ERRO: '${TARGET}' não parece ser um clone do OPL (sem Makefile)." >&2
    exit 1
fi

cd "${TARGET}"

echo "==> Aplicando mods em ${TARGET}..."

# 1. Aplicar patches (.patch)
for patch in "${MODS_DIR}"/*.patch; do
    patch_name="$(basename "${patch}")"
    echo "   - Aplicando ${patch_name}..."
    if git apply --check "${patch}" 2>/dev/null; then
        git apply "${patch}"
    elif patch -p1 --dry-run < "${patch}" >/dev/null 2>&1; then
        patch -p1 < "${patch}"
    else
        echo "ERRO: não foi possível aplicar ${patch_name}." >&2
        echo "       Provável conflito com nova versão do upstream." >&2
        echo "       Edite o patch manualmente em mods/${patch_name}" >&2
        exit 1
    fi
done

# 2. Copiar merge_ptbr.py para a raiz do OPL
echo "   - Copiando merge_ptbr.py..."
cp "${MODS_DIR}/merge_ptbr.py" .
chmod +x merge_ptbr.py

# 3. Baixar fontes de tradução (se ainda não baixadas)
if [ ! -d "lng_src" ]; then
    echo "   - Baixando fontes de tradução (lng_src)..."
    bash download_lng.sh
fi

# 4. Baixar lwNBD (opcional, pode falhar sem rede)
if [ ! -d "thirdparty/lwNBD" ] && [ -f download_lwNBD.sh ]; then
    echo "   - Baixando lwNBD (opcional)..."
    bash download_lwNBD.sh || echo "     (lwNBD falhou — build vai continuar sem ele)"
fi

# 5. Gerar _base_ptbr.yml (mescla PT-BR no _base.yml)
echo "   - Gerando lng_tmpl/_base_ptbr.yml..."
python3 merge_ptbr.py

echo
echo "===================================================="
echo "  MODS APLICADOS COM SUCESSO"
echo "===================================================="
echo
echo "Para compilar:"
echo "  cd ${TARGET}"
echo "  make -j\$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0"
echo
echo "Para gerar o pacote de release:"
echo "  make release NOT_PACKED=0 DEBUG=0 PADEMU=0"
