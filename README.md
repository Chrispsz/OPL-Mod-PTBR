# OPL Mod PT-BR

[![Build](https://github.com/Chrispsz/OPL-Mod-PTBR/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/Chrispsz/OPL-Mod-PTBR/actions/workflows/build.yml)
[![Release](https://github.com/Chrispsz/OPL-Mod-PTBR/actions/workflows/release.yml/badge.svg)](https://github.com/Chrispsz/OPL-Mod-PTBR/releases)
[![Pipeline Semanal](https://github.com/Chrispsz/OPL-Mod-PTBR/actions/workflows/weekly-pipeline.yml/badge.svg)](https://github.com/Chrispsz/OPL-Mod-PTBR/actions/workflows/weekly-pipeline.yml)

Build customizada do [Open PS2 Loader (OPL)](https://github.com/ps2homebrew/Open-PS2-Loader) com:

- 🇧🇷 **PT-BR embutido no ELF** — idioma padrão sem precisar de `.lng` externo
- ⚖️ **Perfil Balanced-Optimized** — caches no default oficial (melhor p/ ZSO), UX melhorada
- 🔌 **USB-default** — Universal, funciona em qualquer PS2 (Fat ou Slim)
- ⚡ **IGR + VMC** ativos por padrão
- 🪶 **Build enxuta** — sem PADEMU, GSM, IGS, ILINK, MX4SIO, RTL (ELF menor)
- 🤖 **CI/CD à prova de falhas** — build validada antes de qualquer release, sync semanal automático

## O que mudou vs OPL oficial

| Aspecto | OPL Oficial | Este Mod |
|---------|-------------|----------|
| Idioma interno | Inglês | **PT-BR embutido no ELF** |
| Idiomas `.lng` gerados | 29 idiomas | Apenas `Portuguese_BR.lng` |
| PADEMU | Compilado | **Removido do build** (~120KB economizado) |
| USB (BDM) | Desativado por default | **AUTO no boot** |
| HDD interno | Desativado por default | Desativado (reativável via Settings) |
| ETH/SMB | Desativado por default | Desativado (reativável via Settings) |
| Device default | APP_MODE | **BDM_MODE** (USB) |
| Caches CDVD | 16 / 8 / 16 | Oficiais (16 / 8 / 16 — melhores p/ ZSO) |
| gEnableWrite | 0 | **1** |
| gAutoRefresh | 0 | **1** |
| gHDDGameListCache | 0 | **1** |
| gEnableArt (capas) | 0 | **1** |
| gEnableNotifications | 0 | **1** |
| gWideScreen | 0 | **1** |
| gEnableSFX | 0 | **1** (sons de menu) |
| gEnableBootSND | 0 | **1** |
| gRememberLastPlayed | 0 | **1** |
| gScrollSpeed | 1 | 1 (oficial) |
| IGR | Compilado (default ON per-game) | Mantido (combo L1+R1+L2+R2+Start+Select) |
| GSM / IGS | Desativados | **Não compilados** (economiza ~180KB) |
| RTL | Compilado | **Não compilado** (~20KB economizado) |

## 🚀 Como usar (download do ELF pronto)

Se você só quer o ELF compilado, sem compilar nada:

1. Vá em **[Releases](../../releases)**
2. Baixe o ZIP do kit mais recente
3. Descompacte e copie para o cartão de memória do PS2:
   - `mc0:/OPL/OPNPS2LD.ELF` (obrigatório)
   - `mc0:/OPL/lang_Portuguese_BR.lng` (opcional — já tem PT-BR embutido)
4. Inicie via **FreeMcBoot**, **FreeHDBoot** ou **uLaunchELF**

O kit de release também traz `BOOT.ELF` (uLaunchELF), `MCA.ELF`, `HDLGameInstaller.ELF` e `MFU.ELF` — utilitários prontos para `mc0:/BOOT/` e `mc0:/APPS/`.

## 🛠️ Como compilar localmente

### Opção A — Docker (mais simples)

```bash
git clone https://github.com/Chrispsz/OPL-Mod-PTBR.git
cd OPL-Mod-PTBR

docker run --rm -v "$PWD:/work" -w /work ps2dev/ps2dev:latest bash -c '
  apk add --no-cache python3 py3-yaml git bash make >/dev/null
  git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git opl
  bash scripts/apply-mods.sh opl
  cd opl && make -j$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0
'
# ELF em opl/OPNPS2LD.ELF
```

### Opção B — Linux nativo

Se você já tem PS2SDK + gsKit instalados ([ps2dev/ps2dev](https://github.com/ps2dev/ps2dev)):

```bash
git clone https://github.com/Chrispsz/OPL-Mod-PTBR.git
cd OPL-Mod-PTBR
git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git opl
bash scripts/apply-mods.sh opl
cd opl && make -j$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0
```

## 🤖 Como o CI/CD funciona

3 workflows em `.github/workflows/`, todos só com o `GITHUB_TOKEN` embutido
(sem PAT, sem secrets para configurar):

### `build.yml` — Build validada em cada push/PR

- Compila o OPL com os mods aplicados
- **Valida antes de publicar**: ELF MIPS válido (magic + tamanho 2–8 MB) e
  PT-BR realmente embutido (`lang_internal.c` com acentuação)
- Publica artifact `OPNPS2LD-<sha>` (90 dias) na aba Actions

### `release.yml` — Release em cada tag

- Aciona em `git push origin v1.2.0-Beta-ptbr.N` (ou via Pipeline Semanal)
- Compila, valida e cria a Release com 2 assets:
  - **Kit PS2** (ZIP): `OPNPS2LD.ELF` + `BOOT.ELF` + `MCA.ELF` + `HDLGameInstaller.ELF` + `MFU.ELF`
  - **Ferramentas Linux** (tar.gz): `ps2client` + `OPL-PC-Tools` + `HDL-Batch-Installer`
- Se a build falhar, **nenhuma release é criada**

### `weekly-pipeline.yml` — Sync + release semanal automática

- Roda todo domingo às 23:00 UTC (20:00 BRT)
- Compara SHAs do upstream (OPL + uLaunchELF) com os gravados em `upstream.sha`/`ule.sha`
- Se mudou: **dispara e ESPERA a build de validação**; só depois grava os SHAs,
  cria a próxima tag `v*-Beta-ptbr.N` e dispara a release
- Se a build de validação falhar: abre/atualiza issue `upstream-sync` e
  **não cria tag nenhuma** (impossível gerar "tag morta")

Para rodar manualmente: aba Actions → Pipeline Semanal → Run workflow
(`force=true` para release imediata mesmo sem mudanças upstream).

## 📁 Estrutura do repo

```
OPL-Mod-PTBR/
├── .github/workflows/
│   ├── build.yml              # Build validada em push/PR
│   ├── release.yml            # Release em tag
│   └── weekly-pipeline.yml    # Sync semanal + auto-release (validado)
├── mods/
│   ├── apply_mods.py          # Edições por âncoras de conteúdo (Makefile + opl.c)
│   └── merge_ptbr.py          # Mescla PT-BR no _base.yml
├── scripts/
│   ├── apply-mods.sh          # Aplica mods num clone upstream
│   └── sync-upstream.sh       # Validador local (debug)
├── upstream.sha               # SHA do OPL upstream registrado
├── ule.sha                    # SHA do uLaunchELF registrado
├── .gitignore
├── LICENSE                    # AFL-3.0
└── README.md
```

### Por que âncoras em vez de patches?

Os mods são aplicados por **âncoras de conteúdo** (`mods/apply_mods.py`), não
por patches de linha. Patches quebram a cada mudança do upstream (linhas
deslocam); âncoras só quebram se o upstream mudar o **código em si** — e, se
quebrar, o erro aponta **exatamente qual âncora** precisa de revisão. O script
só grava os arquivos se TODAS as âncoras + pós-validação passarem (nunca aplica
pela metade).

## 🎨 Personalizando o mod

Edite `mods/apply_mods.py` — cada modificação é uma âncora + substituição:

```python
# Mudar device default (USB -> HDD):
text = replace_exact(
    text,
    "    gDefaultDevice = BDM_MODE; // Mod: USB default (universal em todo PS2)",
    "    gDefaultDevice = HDD_MODE;",
    "opl.c: default device = HDD",
)

# Reativar PADEMU: remova a substituição "PADEMU ?= 1 -> 0" e use PADEMU=1 no make.
```

Depois rode o validador local antes de subir:

```bash
./scripts/sync-upstream.sh   # valida as âncoras contra o upstream atual
```

### Mudar tema

Por padrão o tema é o default do OPL (azul). Baixe um tema de
[ps2homebrew/OPL-Themes](https://github.com/ps2homebrew/OPL-Themes), extraia
para `mc0:/OPL/th_<nome-do-tema>/` e selecione em Settings → Themes.
Não é necessário recompilar — temas são carregados em runtime.

## 🐛 Troubleshooting

### O pipeline criou uma issue "Sync upstream falhou"

A build de validação não passou contra o novo upstream. Abra o run linkado na
issue: se for âncora quebrada, o log aponta qual (`Âncora 'X' encontrada 0x`);
se for quebra de código, ajuste o mod. Depois rode o pipeline com `force=true`.

### O build falha com "mods não aplicam"

Veja o erro exato no log: cada âncora falha com a mensagem e o trecho de
referência. Atualize a âncora em `mods/apply_mods.py` para o novo conteúdo do
upstream. Nada é aplicado pela metade — ou tudo aplica, ou nada.

### Alguns jogos travam

~5% dos jogos mais pesados podem sofrer com periféricos/caches. Nas Settings
per-game (engrenagem no jogo), aba "Advanced", ajuste o `Read Cache` ou
desative hooks extras.

### Como ver a versão do build

```bash
cd opl && make oplversion
# Exemplo: v1.2.0-Beta-3-b3a2199
```

## 🤝 Integração com PS2 Manager (Linux nativo)

O [PS2 Manager](https://github.com/Chrispsz/ps2-manager) — gerenciador nativo Linux em Rust — consome este repositório automaticamente:

```bash
ps2-manager deploy /media/$USER/PS2_SD
```

Baixa o `OPL-PTBR-Mod-Kit-*.zip` da release mais recente e monta `BOOT_MC/` pronto para copiar ao memory card via uLaunchELF (`mc0:/OPL/`, `mc0:/BOOT/`, `mc0:/APPS/`). O contrato completo está em [`MANIFEST.json`](MANIFEST.json) e a documentação em [`docs/PS2-MANAGER.md`](docs/PS2-MANAGER.md).

O mesmo tool ainda faz: instalação com naming `GAMEID.Título.iso`, ZSO multithread, Smart ISO Shrink (LBA-preserving), ul.cfg bit-exact, capas 140×200 e cheats PNACH→`.cht`.

## 🙏 Créditos

- **OPL original:** [ps2homebrew/Open-PS2-Loader](https://github.com/ps2homebrew/Open-PS2-Loader)
- **Tradução PT-BR:** [Open-PS2-Loader-lang](https://github.com/ps2homebrew/Open-PS2-Loader-lang)
- **PS2SDK toolchain:** [ps2dev/ps2dev](https://github.com/ps2dev/ps2dev)

## 📜 Licença

AFL-3.0 — herdada do OPL original. Veja [LICENSE](LICENSE).
