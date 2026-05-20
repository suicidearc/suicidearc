# Update via GitHub

## 1. Criar o repo

Crie um repositorio no GitHub e envie estes arquivos do projeto.

Nao envie `config.json`, `settings.json` ou `dist/`; eles ficam ignorados pelo `.gitignore`.

## 2. Configurar o manifest no codigo

Depois de criar o repo, ajuste no `selfbot.py`:

```python
APP_VERSION = "1.0.0"
UPDATE_ENABLED = True
UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/suicidearc/suicidearc/main/version.json"
UPDATE_TIMEOUT = 15
```

## 3. Gerar o exe

Rode o build normalmente. Depois calcule o SHA-256:

```powershell
Get-FileHash .\dist\suicide.exe -Algorithm SHA256
```

## 4. Criar release no GitHub

Crie uma release com tag `v1.0.0` e envie o arquivo:

```text
suicide.exe
```

## 5. Atualizar `version.json`

Edite `version.json`:

```json
{
  "latest_version": "1.0.0",
  "min_supported_version": "1.0.0",
  "download_url": "https://github.com/suicidearc/suicidearc/releases/download/v1.0.0/suicide.exe",
  "sha256": "HASH_SHA256_DO_EXE"
}
```

## Nova versao

Para uma nova versao:

1. Mude `APP_VERSION` no `selfbot.py`, exemplo `1.1.0`.
2. Gere um novo `.exe`.
3. Calcule o SHA-256.
4. Crie uma release `v1.1.0` com o novo `.exe`.
5. Atualize `version.json` com `latest_version`, `min_supported_version`, `download_url` e `sha256`.

Quem abrir uma versao antiga sera bloqueado e obrigado a atualizar.
