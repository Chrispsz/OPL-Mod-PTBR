# Integração: OPL-Mod-PTBR × PS2 Manager

O [**PS2 Manager**](https://github.com/Chrispsz/ps2-manager) é um gerenciador nativo Linux (Rust) para coleções de PS2 — e a partir da v0.1 ele já nasce **conectado a este repositório**: o módulo de deploy consulta as releases daqui, baixa o `OPL-PTBR-Mod-Kit-*.zip` mais recente e monta a estrutura pronta para o memory card.

## O que o PS2 Manager faz

```bash
# Instalação de jogos na estrutura OPL (CD/DVD/ART/CFG/VMC/CHT/APPS/THM/LNG)
ps2-manager install Jogo.iso /media/$USER/PS2_SD --zso

# Capas 140x200 da base xlenore/ps2-covers → ART/<ID>_COV.png
ps2-manager covers /media/$USER/PS2_SD

# Cheats PNACH → CHT/<ID>.cht (formato PS2RD nativo do OPL)
ps2-manager cheats /media/$USER/PS2_SD --pnach-dir ~/pnach

# Smart ISO Shrink (remove dummy sectors preservando LBA) + ZSO multithread
ps2-manager shrink sujo.iso limpo.iso
ps2-manager zso Jogo.iso Jogo.zso

# ul.cfg USBExtreme bit-exact (CRC32 USBA réplica de src/system.c)
ps2-manager ulcfg /media/$USER/PS2_SD
```

## Deploy do mod PT-BR (`BOOT_MC/`)

```bash
ps2-manager deploy /media/$USER/PS2_SD
```

1. Consulta a release mais recente deste repositório (incluindo **prereleases** — todas as nossas releases são marcadas como pre);
2. Baixa o asset `OPL-PTBR-Mod-Kit-*.zip`;
3. Extrai e organiza em `BOOT_MC/` no pendrive/cartão:

```text
BOOT_MC/
├── OPL/OPNPS2LD.ELF        ← OPL PT-BR (mc0:/OPL/)
├── BOOT/BOOT.ELF           ← uLaunchELF (mc0:/BOOT/)
├── APPS/MCA.ELF            ← Memory Card Annihilator (mc0:/APPS/)
├── APPS/HDLGameInstaller.ELF
├── APPS/MFU.ELF
├── SYS-CONF/FREMCB.CNF     ← template de launch keys (ajustável)
└── README-INSTALACAO.txt   ← passo a passo para o PS2
```

4. No PS2: abra o uLaunchELF → `mass:/BOOT_MC` → copie cada pasta para `mc0:` conforme o `README-INSTALACAO.txt`.

## Contrato de integração (`MANIFEST.json`)

O arquivo [`MANIFEST.json`](../MANIFEST.json) na raiz deste repositório declara, de forma legível por máquina, o mapeamento completo do kit:

| Campo | Significado |
|---|---|
| `deploy.kit_asset_pattern` | nome do asset a baixar nas releases |
| `deploy.files[].source` | arquivo dentro do ZIP |
| `deploy.files[].target` | destino em `BOOT_MC/` |
| `deploy.files[].mc_path` | destino final no memory card (`mc0:`) |
| `upstream_sha` | commit do OPL upstream rastreado (igual a `upstream.sha`) |

Se um dia o kit mudar de estrutura, basta atualizar o `MANIFEST.json` — o PS2 Manager passa a respeitá-lo automaticamente (hoje usa heurísticas compatíveis + este contrato como referência).

## Compatibilidade binária garantida

O PS2 Manager implementa os formatos lendo o código-fonte do OPL upstream:

- `ul.cfg` de 64 bytes (`include/supportbase.h`) e CRC32 `USBA_crc32` (`src/system.c`) — **validado bit a bit** contra o C compilado;
- ZSO com header/índice idênticos a `modules/isofs/zso.c` (blocos 2048, bit 31 = plain) — roundtrip testado;
- `.cht` PS2RD exatamente como `src/cheatman.c` espera;
- pastas do dispositivo idênticas a `sbCreateFolders`.

## Build do PS2 Manager

```bash
git clone https://github.com/Chrispsz/ps2-manager
cd ps2-manager && cargo build --release
```
