# OPL Mod PT-BR

[![Build](https://github.com/{{USER}}/OPL-Mod-PTBR/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/{{USER}}/OPL-Mod-PTBR/actions/workflows/build.yml)
[![Release](https://github.com/{{USER}}/OPL-Mod-PTBR/actions/workflows/release.yml/badge.svg)](https://github.com/{{USER}}/OPL-Mod-PTBR/releases)
[![Sync Upstream](https://github.com/{{USER}}/OPL-Mod-PTBR/actions/workflows/sync-upstream.yml/badge.svg)](https://github.com/{{USER}}/OPL-Mod-PTBR/actions/workflows/sync-upstream.yml)

> **Substitua `{{USER}}` pelo seu usuário GitHub em todo este README depois de criar o repo.**

Build customizada do [Open PS2 Loader (OPL)](https://github.com/ps2homebrew/Open-PS2-Loader) com:

- 🇧🇷 **PT-BR embutido no ELF** — idioma padrão sem precisar de `.lng` externo
- 🎮 **Perfil Performance** — caches grandes, write on, art on (capas), SFX on, notificações on
- 🔌 **USB-default** — Universal, funciona em qualquer PS2 (Fat ou Slim)
- ⚡ **IGR + VMC** ativos por padrão
- 🪶 **Build enxuta** — sem PADEMU, GSM, IGS, ILINK, MX4SIO, RTL (ELF ~10% menor)
- 🤖 **CI/CD completo** — build automático em push, release em tag, sync semanal com upstream

## O que mudou vs OPL oficial

| Aspecto | OPL Oficial | Este Mod |
|---------|-------------|----------|
| Idioma interno | Inglês | **PT-BR embutido no ELF** |
| Idiomas `.lng` gerados | 27 idiomas | Apenas `Portuguese_BR.lng` |
| PADEMU | Compilado | **Removido do build** (~120KB economizado) |
| USB (BDM) | Desativado por default | **AUTO no boot** |
| HDD interno | Desativado por default | Desativado (reativável via Settings) |
| ETH/SMB | Desativado por default | Desativado (reativável via Settings) |
| Device default | APP_MODE | **BDM_MODE** (USB) |
| Cache CDVD USB | 16 | **32** |
| Cache CDVD HDD | 8 | **16** |
| gEnableWrite | 0 | **1** |
| gAutoRefresh | 0 | **1** |
| gEnableArt (capas) | 0 | **1** |
| gEnableNotifications | 0 | **1** |
| gWideScreen | 0 | **1** |
| gEnableSFX | 0 | **1** (sons de menu) |
| gScrollSpeed | 1 | **2** (rápida) |
| gRememberLastPlayed | 0 | **1** |
| IGR | Compilado (default ON per-game) | Mantido (combo L1+R1+L2+R2+Start+Select) |
| GSM / IGS | Desativado | **Não compilados** (economiza ~180KB) |
| RTL | Compilado | **Não compilado** (~20KB economizado) |

**Tamanho do ELF estimado:** ~3.2 MB (vs ~4.0 MB do OPL oficial com tudo).

## 🚀 Como usar (download do ELF pronto)

Se você só quer o ELF compilado, sem compilar nada:

1. Vá em **[Releases](../../releases)**
2. Baixe o ZIP mais recente
3. Descompacte
4. Copie para o cartão de memória do PS2:
   - `mc0:/OPL/OPNPS2LD.ELF` (obrigatório)
   - `mc0:/OPL/lang_Portuguese_BR.lng` (opcional)
   - `mc0:/OPL/font_Portuguese_BR.ttf` (opcional)
   - `mc0:/OPL/conf_opl.cfg` (opcional — força settings no primeiro boot)
5. Inicie via **FreeMcBoot**, **FreeHDBoot** ou **uLaunchELF**

## 🛠️ Como compilar localmente

### Pré-requisitos

- Docker (recomendado) **OU** Linux com PS2SDK instalado
- Git

### Opção A — Usando Docker (mais simples)

```bash
# Clonar este repo
git clone https://github.com/{{USER}}/OPL-Mod-PTBR.git
cd OPL-Mod-PTBR

# Build em container Docker
docker run --rm -v "$PWD:/work" -w /work ps2dev/ps2sdk:latest bash -c '
  git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git opl
  bash scripts/apply-mods.sh opl
  cd opl && make -j$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0
'

# ELF estará em opl/OPNPS2LD.ELF
```

### Opção B — Linux nativo

Se você já tem PS2SDK + gsKit instalados:

```bash
git clone https://github.com/{{USER}}/OPL-Mod-PTBR.git
cd OPL-Mod-PTBR
git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git opl
bash scripts/apply-mods.sh opl
cd opl && make -j$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0
```

Se não tem PS2SDK, instale com [ps2dev/ps2dev](https://github.com/ps2dev/ps2dev).

## 🤖 Como o CI/CD funciona

Este repo tem 3 workflows em `.github/workflows/`:

### `build.yml` — Build em cada push

- Aciona em push para `main` ou `ptbr-mod`, e em PRs
- Compila o OPL com os mods aplicados
- Faz upload do ELF + `.lng` + `.ttf` + `conf_opl.cfg` como artifact (90 dias)
- Acessível na aba **Actions** > workflow run > Artifacts

### `release.yml` — Release em cada tag

- Aciona quando você faz `git push origin v1.2.0-ptbr.1`
- Compila o OPL
- Cria um Release público no GitHub com:
  - ZIP contendo ELF + `.lng` + `.ttf` + `conf_opl.cfg` + `INFO.txt`
  - Notas de release automáticas com a configuração do build

Para criar um novo release:

```bash
git tag v1.2.0-ptbr.1
git push origin v1.2.0-ptbr.1
# O workflow cria o release automaticamente em ~10 min
```

### `sync-upstream.yml` — Sync semanal

- Roda todo domingo às 20:00 (horário de Brasília)
- Verifica se o OPL oficial (`ps2homebrew/Open-PS2-Loader`) teve novos commits
- Se sim:
  1. Testa se os mods ainda aplicam limpo no novo upstream
  2. **Se sim:** atualiza `upstream.sha`, faz commit/push → dispara `build.yml` automaticamente
  3. **Se não:** cria uma issue avisando que precisa de intervenção manual (provável conflito de patch)

**Requer o secret `GH_PAT`** configurado (ver seção abaixo).

## 🔑 Configuração inicial (uma vez só)

Depois de criar o repo no GitHub:

1. **Revogue qualquer token vazado** em https://github.com/settings/tokens

2. **Crie um novo PAT** com escopos: `repo` + `workflow`
   - Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
   - Marque: `repo` (todo) + `workflow`
   - Salve o token em local seguro (você não vai ver de novo)

3. **Adicione o PAT como secret no repo:**
   - Repo → Settings → Secrets and variables → Actions → New repository secret
   - Name: `GH_PAT`
   - Value: cole o token
   - Add secret

4. **Atualize este README** substituindo `{{USER}}` pelo seu usuário GitHub:
   ```bash
   sed -i 's|{{USER}}|seu-usuario|g' README.md
   git commit -am "docs: substitui placeholder de usuário"
   git push
   ```

5. **Faça o primeiro push** de qualquer coisa para disparar o `build.yml` e validar que tudo funciona.

## 📦 Como distribuir entre amigos

### Opção A — Release permanente (recomendado)

Crie uma tag quando quiser uma versão estável:

```bash
git tag -a v1.2.0-ptbr.1 -m "Primeira release do mod PT-BR"
git push origin v1.2.0-ptbr.1
```

O workflow `release.yml` vai criar um Release público em `../../releases`. Mande o link pros seus amigos.

### Opção B — Beta build (artifact)

Sempre que você fizer push para `main`, o `build.yml` gera um artifact temporário (90 dias) na aba Actions. Bom pra testar mudanças antes de fazer uma release.

### Opção C — Build local + pendrive

Se não quiser usar CI:

```bash
docker run --rm -v "$PWD:/work" -w /work ps2dev/ps2sdk:latest bash -c '
  git clone --depth 1 https://github.com/ps2homebrew/Open-PS2-Loader.git opl
  bash scripts/apply-mods.sh opl
  cd opl && make -j$(nproc) NOT_PACKED=0 DEBUG=0 PADEMU=0
'
# Copie opl/OPNPS2LD.ELF para o pendrive
```

## 📁 Estrutura do repo

```
OPL-Mod-PTBR/
├── .github/workflows/
│   ├── build.yml              # Build em push/PR
│   ├── release.yml            # Release em tag
│   └── sync-upstream.yml      # Sync semanal
├── mods/
│   ├── 001-Makefile-ptbr-performance.patch   # Patch do Makefile
│   ├── 002-opl-c-performance-usb.patch       # Patch do src/opl.c
│   ├── merge_ptbr.py          # Mescla PT-BR no _base.yml
│   └── conf_opl.cfg           # Config OPL pré-definida (opcional)
├── scripts/
│   ├── apply-mods.sh          # Aplica mods num clone upstream
│   └── sync-upstream.sh       # Sync manual (debug)
├── upstream.sha               # SHA do upstream sincronizado
├── .gitignore
├── LICENSE                    # AFL-3.0
└── README.md                  # Este arquivo
```

## 🎨 Personalizando o mod

### Mudar o device default (USB → HDD)

Edite `mods/002-opl-c-performance-usb.patch`:

```diff
-    gDefaultDevice = BDM_MODE;
+    gDefaultDevice = HDD_MODE;
```

### Reativar HDD/ETH no boot

No mesmo patch:

```diff
-    gHDDStartMode = START_MODE_DISABLED;
-    gETHStartMode = START_MODE_DISABLED;
+    gHDDStartMode = START_MODE_AUTO;
+    gETHStartMode = START_MODE_AUTO;
```

### Reativar PADEMU

Edite `mods/001-Makefile-ptbr-performance.patch`:

```diff
-PADEMU ?= 0
+PADEMU ?= 1
```

E no comando de build (e workflow), troque `PADEMU=0` por `PADEMU=1`.

### Mudar tema

Por padrão o tema é o default do OPL (azul). Para usar outro tema:

1. Baixe um tema de [ps2homebrew/OPL-Themes](https://github.com/ps2homebrew/OPL-Themes)
2. Extraia para `mc0:/OPL/th_<nome-do-tema>/`
3. No OPL: Settings → Themes → escolha o tema

Não é necessário recompilar — temas são carregados em runtime.

## 🐛 Troubleshooting

### O workflow `sync-upstream` falha com `GH_PAT secret not found`

Você não configurou o secret. Vá em Repo → Settings → Secrets and variables → Actions → New repository secret, nome `GH_PAT`, valor = seu PAT.

### O workflow `build.yml` falha com `mods/*.patch não aplicou`

Provável conflito com nova versão do upstream. Veja o log do workflow, identifique qual patch falhou, edite o arquivo em `mods/`, faça commit e push.

### O ELF fica muito grande

Confirme que está usando `NOT_PACKED=0` (default). Verifique também que PADEMU está 0 no Makefile e que você não ativou `EXTRA_FEATURES=1`.

### Como ver a versão do build

```bash
cd opl && make oplversion
# Exemplo: v1.2.0-Beta-1824-3e3f34e
```

### Alguns jogos travam com cache grande

~5% dos jogos mais pesados podem ter conflito de memória com o cache CDVD grande (32). Solução: nas Settings per-game (ícone de engrenagem no jogo), aba "Advanced", reduza `Read Cache` para 8 ou 16.

## 🙏 Créditos

- **OPL original:** [ps2homebrew/Open-PS2-Loader](https://github.com/ps2homebrew/Open-PS2-Loader)
- **Tradução PT-BR:** `gledson999` via [Open-PS2-Loader-lang](https://github.com/ps2homebrew/Open-PS2-Loader-lang)
- **PS2SDK toolchain:** [ps2dev/ps2dev](https://github.com/ps2dev/ps2dev)
- **Docker image:** [ps2dev/ps2sdk-docker](https://github.com/ps2dev/ps2sdk-docker)

## 📜 Licença

AFL-3.0 — herdada do OPL original. Veja [LICENSE](LICENSE).
