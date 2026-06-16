"""
findexauth.py — FindexAuth Python SDK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Drop-in module. Same structure as FindexAuth.cs.

INSTALL:  pip install requests rsa

USAGE:
    from findexauth import api

    auth = api("AppName", "OWNERID15CHARS", "SECRET64CHARS", "1.0", "https://yourserver.com", "RSA_PUB_KEY")
    auth.init()
    auth.license("YOUR-LICENSE-KEY")

    if auth.response.success and auth.response.needs_registration:
        auth.register_key(auth.response.validated_key, "myusername", "mypassword")

    if not auth.response.success:
        print(auth.response.message)
        exit()

    print(f"Welcome, {auth.user_data.username}!")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import requests
import platform
import time
import os

# ─────────────────────────────────────────────────────────────────────────────
#  DATA CLASSES (mirror FindexAuth.cs naming)
# ─────────────────────────────────────────────────────────────────────────────

class user_data_class:
    """Populated after successful license() or login() call."""
    def __init__(self):
        self.username:    str = ""
        self.hwid:        str = ""
        self.ip:          str = ""
        self.expiry:      str = "Lifetime"
        self.level:       str = "1"
        self.license_key: str = ""
        self.createdate:  str = ""
        self.lastlogin:   str = ""

class app_data_class:
    """Populated after init()."""
    def __init__(self):
        self.version:       str = ""
        self.status:        str = ""
        self.numUsers:      str = ""
        self.downloadLink:  str = ""   # auto-update download URL
        self.webloaderLink: str = ""   # webloader download URL
        self.hash:          str = ""   # executable hash
        self.updateVersion: str = ""   # latest version on server

class response_class:
    """Always populated after any API call."""
    def __init__(self):
        self.success:            bool = False
        self.message:            str  = ""
        self.needs_registration: bool = False   # True = fresh key, call register_key() next
        self.username_taken:     bool = False   # True = chosen username already exists
        self.validated_key:      str  = ""      # Key echoed back for registration step


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN API CLASS
# ─────────────────────────────────────────────────────────────────────────────

class api:
    """
    FindexAuth Python SDK
    Mirrors the C# FindexAuth.api class interface.
    """

    responseTime: int = 0  # ms of last API call

    def __init__(self, name: str, ownerid: str, secret: str,
                 version: str, apiUrl: str = "http://localhost:5001", rsa_pub_key: str = ""):
        self.name:    str = name
        self.ownerid: str = ownerid
        self.secret:  str = secret
        self.version: str = version
        self.apiUrl:  str = apiUrl.rstrip("/")

        self.user_data = user_data_class()
        self.app_data  = app_data_class()
        self.response  = response_class()

        self._initialized = False
        self._pub_key:    str = rsa_pub_key

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _hwid(self) -> str:
        try:
            import subprocess
            out = subprocess.check_output('whoami /user', shell=True, stderr=subprocess.DEVNULL).decode()
            return out.strip().split('\n')[-1].split()[-1]
        except Exception:
            return platform.node()

    def _verify_signature(self, raw_json: str, signature: str) -> bool:
        if not self._pub_key:
            return True # Not configured/enforced
        try:
            import rsa
            import base64
            sig_idx = raw_json.find(',"__sig"')
            if sig_idx == -1: return False
            payload = raw_json[:sig_idx] + "}"
            
            key_str = f"-----BEGIN PUBLIC KEY-----\n{self._pub_key}\n-----END PUBLIC KEY-----"
            pub = rsa.PublicKey.load_pkcs1_openssl_pem(key_str.encode())
            
            rsa.verify(payload.encode('utf-8'), base64.b64decode(signature), 'SHA-256')
            return True
        except ImportError:
            self.error("rsa module missing! pip install rsa")
            return False
        except Exception:
            return False

    def _post(self, endpoint: str, payload: dict) -> dict:
        try:
            start = time.monotonic()
            r = requests.post(self.apiUrl + endpoint, json=payload, timeout=15)
            api.responseTime = int((time.monotonic() - start) * 1000)
            data = r.json()
            
            # Security: Verify RSA Signature
            if "__sig" in data:
                if not self._verify_signature(r.text, data["__sig"]):
                    return {"success": False, "message": "Security Error: Signature verification failed. Possible server spoofing detected."}

            return data
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _get(self, endpoint: str) -> dict:
        try:
            r = requests.get(self.apiUrl + endpoint, timeout=10)
            return r.json()
        except Exception:
            return {"success": False}

    def _load_user(self, data: dict):
        d = data.get("data") or data.get("info") or {}
        self.user_data.username    = d.get("username",    "")
        self.user_data.hwid        = d.get("hwid",        "")
        self.user_data.ip          = d.get("ip",          "")
        self.user_data.expiry      = d.get("expiry",      "Lifetime")
        self.user_data.level       = str(d.get("level",   "1"))
        self.user_data.license_key = d.get("license_key", "")
        self.user_data.createdate  = d.get("created_at",  "")
        self.user_data.lastlogin   = d.get("last_login",  "")

    def _set_response(self, data: dict):
        self.response.success            = data.get("success",            False)
        self.response.message            = data.get("message",            "Unknown error")
        self.response.needs_registration = data.get("needs_registration", False)
        self.response.username_taken     = data.get("username_taken",     False)
        self.response.validated_key      = data.get("key",                "")

    # ── init() ────────────────────────────────────────────────────────────────

    def init(self):
        """
        Connect to server, verify app credentials, check version.
        Must be called before license() or login().
        """
        data = self._post("/api/1.3/app-info", {
            "app_name": self.name, "app_secret": self.secret
        })

        self._set_response(data)
        if not self.response.success:
            return

        ai = data.get("data") or data.get("appinfo") or {}
        self.app_data.version       = ai.get("version",        self.version)
        self.app_data.status        = ai.get("status",         "enabled")
        self.app_data.downloadLink  = ai.get("downloadLink",   ai.get("download_link", ""))
        self.app_data.webloaderLink = ai.get("webloaderLink",  "")
        self.app_data.hash          = ai.get("hash",           "")
        self.app_data.updateVersion = ai.get("version",        ai.get("latest_version", ""))

        # Auto-update check
        srv_ver = self.app_data.updateVersion or self.app_data.version
        if srv_ver and srv_ver != self.version:
            self.response.success = False
            link = self.app_data.downloadLink or f"{self.apiUrl}/update"
            self.response.message = f"Update available! v{srv_ver}\nDownload: {link}"
            return

        self.response.success = True
        self.response.message = "Initialized."
        self._initialized = True

    # ── license(key) ─────────────────────────────────────────────────────────

    def license(self, key: str):
        if not self._initialized:
            self.response.success = False
            self.response.message = "Call init() first."
            return

        data = self._post("/api/1.3/login-key", {
            "app_name":   self.name,
            "app_secret": self.secret,
            "key":        key,
            "hwid":       self._hwid(),
            "version":    self.version
        })

        self._set_response(data)
        if not self.response.validated_key:
            self.response.validated_key = key

        if self.response.success and not self.response.needs_registration:
            self._load_user(data)

    # ── register_key(key, username, password) ─────────────────────────────────

    def register_key(self, key: str, username: str, password: str):
        if not self._initialized:
            self.response.success = False
            self.response.message = "Call init() first."
            return

        data = self._post("/api/1.3/register-key", {
            "app_name":   self.name,
            "app_secret": self.secret,
            "key":        key,
            "username":   username,
            "password":   password,
            "hwid":       self._hwid(),
            "version":    self.version
        })

        self._set_response(data)
        if self.response.success:
            self._load_user(data)

    # ── login(username, password) ─────────────────────────────────────────────

    def login(self, username: str, password: str):
        if not self._initialized:
            self.response.success = False
            self.response.message = "Call init() first."
            return

        data = self._post("/api/1.3/login", {
            "app_name":   self.name,
            "app_secret": self.secret,
            "username":   username,
            "password":   password,
            "hwid":       self._hwid(),
            "version":    self.version
        })

        self._set_response(data)
        if self.response.success:
            self._load_user(data)

    # ── checkblack() ─────────────────────────────────────────────────────────

    def checkblack(self) -> bool:
        data = self._post("/api/1.3/check-blacklist", {
            "app_name": self.name, "app_secret": self.secret, "hwid": self._hwid()
        })
        return data.get("success", False)

    # ── var(varid) ────────────────────────────────────────────────────────────

    def var(self, varid: str) -> str:
        data = self._post("/api/1.3/var", {
            "app_name": self.name, "app_secret": self.secret, "var_name": varid
        })
        return data.get("data", "") if data.get("success") else ""
        
    # ── webhook(webid, params) ────────────────────────────────────────────────
        
    def webhook(self, webid: str, params: str = ""):
        data = self._post("/api/1.3/webhook", {
            "app_name": self.name, "app_secret": self.secret, "webid": webid, "params": params
        })
        self._set_response(data)
        
    # ── download_file(fileid) ─────────────────────────────────────────────────
        
    def download_file(self, fileid: str) -> bytes:
        data = self._post("/api/1.3/file", {
            "app_name": self.name, "app_secret": self.secret, "fileid": fileid
        })
        self._set_response(data)
        if not data.get("success"):
            return None
            
        hex_data = data.get("contents", "")
        if not hex_data: return None
        try:
            return bytes.fromhex(hex_data)
        except Exception:
            return None

    # ── log(msg) ──────────────────────────────────────────────────────────────

    def log(self, msg: str):
        self._post("/api/1.3/log", {
            "app_name": self.name, "app_secret": self.secret,
            "username": self.user_data.username, "message": msg
        })

    # ── change_username(new_username, password) ────────────────────────────────

    def change_username(self, new_username: str, password: str):
        data = self._post("/api/1.3/change-username", {
            "app_name":    self.name,
            "app_secret":  self.secret,
            "username":    self.user_data.username,
            "password":    password,
            "new_username": new_username
        })
        self._set_response(data)
        if self.response.success:
            self.user_data.username = new_username

    # ── change_password(old_pass, new_pass) ───────────────────────────────────

    def change_password(self, old_password: str, new_password: str):
        data = self._post("/api/1.3/change-password", {
            "app_name":    self.name,
            "app_secret":  self.secret,
            "username":    self.user_data.username,
            "old_password": old_password,
            "new_password": new_password
        })
        self._set_response(data)

    # ── heartbeat() ───────────────────────────────────────────────────────────

    def heartbeat(self) -> bool:
        if not self.user_data.username:
            return True
        data = self._post("/api/1.3/heartbeat", {
            "app_name":   self.name,
            "app_secret": self.secret,
            "username":   self.user_data.username,
            "hwid":       self._hwid()
        })
        if not isinstance(data, dict):
            return True
        ok = data.get("success", True)
        self.response.message = data.get("message", "")
        return ok

    def start_heartbeat(self, interval_seconds: int = 30, on_kick=None):
        import threading, sys

        def _loop():
            while True:
                time.sleep(interval_seconds)
                if not self.user_data.username:
                    continue
                try:
                    data = self._post("/api/1.3/heartbeat", {
                        "app_name":   self.name,
                        "app_secret": self.secret,
                        "username":   self.user_data.username,
                        "hwid":       self._hwid()
                    })
                    if not data.get("success") and data.get("message"):
                        reason  = data.get("reason",  "terminated")
                        message = data.get("message", "Session terminated by server.")

                        if on_kick:
                            try: on_kick(reason, message)
                            except: pass

                        print(f"\n[FindexAuth] {message}")
                        sys.exit(1)
                except:
                    pass

        t = threading.Thread(target=_loop, daemon=True, name="FindexAuth-Heartbeat")
        t.start()

    # ── error(message) ────────────────────────────────────────────────────────

    @staticmethod
    def error(message: str):
        os.makedirs("Logs", exist_ok=True)
        with open("Logs/ErrorLogs.txt", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} > {message}\n")
        print(f"[FindexAuth ERROR] {message}")
