# FindexAuth - Python SDK Example

Welcome! This is the official **FindexAuth Python Example**. We made this to show you how easy it is to add FindexAuth to your Python projects. 

This example uses a beautiful command-line interface (CLI) with colors. It includes military-grade security like **RSA-SHA256 Signature Verification**, so nobody can spoof your server.

## 🌟 Features
- **Plug & Play:** Just drop `findexauth.py` into your folder and import it.
- **Uncrackable Security:** We use RSA-SHA256 to verify that every single response actually came from your server. Fake DNS routing or MITM attacks will immediately fail.
- **Hidden Server Webhooks:** You can fire Discord webhooks directly from the server. Crackers will never see your Discord URL.
- **Secure File Delivery:** Download files directly into memory as byte arrays. Never let your secret payloads touch the hard drive!
- **Auto Hardware Binding:** Automatically grabs the user's HWID.

## 🚀 How to Setup

### 1. Install Requirements
We use the standard `requests` library for web calls and `rsa` for verifying server signatures. Open your terminal and run:

```bash
pip install requests rsa
```

### 2. Enter Your Details
Open `main.py` in your code editor and look for the config section at the top. Fill in your details from the FindexAuth Dashboard:

```python
APP_NAME   = "Your App Name"
OWNER_ID   = "Your-Owner-ID" 
APP_SECRET = "Your-App-Secret"
APP_VER    = "1.0.0"
SERVER_URL = "https://findexauth.online"

# Find this in your Server Console (prevents DNS spoofing attacks!)
RSA_PUB_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQ..." 
```

### 3. Run It!
Run the app to see it working:

```bash
python main.py
```

## 💻 Code Examples

Here are some examples of what FindexAuth can do for you:

### Setup & Login
```python
from findexauth import api as FindexAuth

auth = FindexAuth("MyApp", "OwnerID", "AppSecret", "1.0", "https://findexauth.online", "RSA_PUB_KEY")
auth.init()

if auth.response.success:
    auth.login("username", "password")
    if auth.response.success:
        print("Welcome", auth.user_data.username)
        auth.start_heartbeat(30) # Protects session in background
```

### Server-Sided Webhooks
Keep your webhook URLs hidden on the server!
```python
# '123' is your Webhook ID from the dashboard
auth.webhook("123", "User logged in successfully!")
```

### Secure File Download
Download payloads safely without writing to disk.
```python
# '5' is your File ID from the dashboard
file_bytes = auth.download_file("5")

if file_bytes:
    # You can now inject these bytes straight into memory!
    print("Downloaded file safely!")
```

---
*Built with ❤️ by FindexAuth.*
