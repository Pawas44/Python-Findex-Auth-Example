# FindexAuth - Python CLI Example

Welcome to the **FindexAuth Python SDK Example**. This project demonstrates how to integrate the FindexAuth authentication and licensing platform into any Python application using an elegant, colorful Command Line Interface (CLI) similar to CloudAuth.

FindexAuth provides military-grade security, hardware binding (HWID), and a robust session management system.

## Features
- **Plug & Play:** Drop `findexauth.py` into your project and you're ready to go.
- **Beautiful Console UI:** Clean ASCII art, colors, and interactive menus out-of-the-box.
- **Hardware Binding:** Automatically grabs HWID using native Python techniques.
- **Background Heartbeat:** The SDK spins up a daemon thread to ping the server every 30 seconds, automatically terminating the app if the user is banned or the subscription expires.
- **Secure Transport:** Uses Python's `requests` library to securely communicate with the FindexAuth REST API.

## Project Structure
```text
├── python/
│   ├── findexauth.py          <-- The core Python SDK. Do not modify.
│   ├── main.py                <-- The interactive CLI application.
│   ├── requirements.txt       <-- Python dependencies.
│   └── README.md
```

## Getting Started

### 1. Install Requirements
FindexAuth relies on the standard `requests` library for HTTP communication.

```bash
pip install -r requirements.txt
# or simply:
pip install requests
```

### 2. Configure Your App Credentials
Open `main.py` in your favorite editor and edit the `CREDENTIALS` section at the top of the file:

```python
APP_NAME   = "Appliction Name"
OWNER_ID   = "Your-Owner-ID" 
APP_SECRET = "Your-App-Secret"
APP_VER    = "1.0.0"
SERVER_URL = "https://findexauth.online"
```

### 3. Run the Example
Run the script using Python:

```bash
python main.py
```

### 4. Integration Guide
To add this to your own project, simply copy `findexauth.py` and implement the basic flow:

```python
from findexauth import api as FindexAuth

auth = FindexAuth("MyApp", "OwnerID", "AppSecret", "1.0", "https://findexauth.online")
auth.init()

if auth.response.success:
    auth.login("username", "password")
    
    if auth.response.success:
        print("Welcome", auth.user_data.username)
        auth.start_heartbeat(30)
```

## Troubleshooting
- **Failed to connect:** Ensure `SERVER_URL` points directly to your API (e.g. `https://findexauth.online`) without trailing slashes.
- **Colors not showing in Windows:** The script automatically attempts to enable ANSI escape codes by calling `os.system('color')`, which is standard for modern Windows command prompts.

---
*Built with ❤️ for FindexAuth.*
