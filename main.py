import time
import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
# Import the FindexAuth SDK
from findexauth import api as FindexAuth

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
# App config - MATCH THESE WITH YOUR FINDEXAUTH DASHBOARD!
APP_NAME   = "Findex Internal"
OWNER_ID   = "8EPQ5RC4KK3AFC6" #Account owner id, found on the dashboard
APP_SECRET = "5715b39369d3a6a763992813c037bf335a368f94f9d82287be12389f4d0ba4de"#APPLICATION SECRET
APP_VER    = "1.0"
SERVER_URL = "https://findexauth.online"

# [SECURITY UPGRADE] Add your RSA Public Key here to prevent DNS spoofing (Found in your server console)
RSA_PUB_KEY = ""
# ─────────────────────────────────────────────────────────────────────────────

# ANSI Color Codes
class Colors:
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    WHITE   = '\033[97m'
    GRAY    = '\033[90m'
    RESET   = '\033[0m'

def format_expiry(exp_str):
    if not exp_str or exp_str == "Lifetime":
        return "Lifetime"
    try:
        from datetime import datetime
        if exp_str.endswith('Z'):
            exp_str = exp_str[:-1] + '+00:00'
        d = datetime.fromisoformat(exp_str)
        return d.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(exp_str).replace('T', ' ').split('.')[0]

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.MAGENTA}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║  ███████╗██╗███╗   ██╗██████╗ ███████╗██╗  ██╗               ║")
    print("║  ██╔════╝██║████╗  ██║██╔══██╗██╔════╝╚██╗██╔╝               ║")
    print("║  █████╗  ██║██╔██╗ ██║██║  ██║█████╗   ╚███╔╝                ║")
    print("║  ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝   ██╔██╗                ║")
    print("║  ██║     ██║██║ ╚████║██████╔╝███████╗██╔╝ ██╗               ║")
    print("║  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝               ║")
    print("║                                                              ║")
    print("║           █████╗ ██╗   ██╗████████╗██╗  ██╗                  ║")
    print("║          ██╔══██╗██║   ██║╚══██╔══╝██║  ██║                  ║")
    print("║          ███████║██║   ██║   ██║   ███████║                  ║")
    print("║          ██╔══██║██║   ██║   ██║   ██╔══██║                  ║")
    print("║          ██║  ██║╚██████╔╝   ██║   ██║  ██║                  ║")
    print("║          ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝                  ║")
    print("║                                                              ║")
    print("║           License Verification System v1.0.0                 ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def read_password(prompt):
    import getpass
    return getpass.getpass(prompt)

def run_protected_app(auth, username):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.GREEN}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║                    ✓ ACCESS GRANTED ✓                        ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}🎉 Welcome to the protected application, {username}!{Colors.RESET}")
    print("\n" + "-" * 60)
    print(f"{Colors.WHITE}This is your protected application area.")
    print(f"Only users with valid licenses can access this section.{Colors.RESET}")
    print("-" * 60)

    # Start the heartbeat to ensure session remains valid
    auth.start_heartbeat(30)
    
    while True:
        print(f"\n{Colors.YELLOW}Available Commands:{Colors.WHITE}")
        print("  1. Show User Info")
        print("  2. Check License Status")
        print("  3. View Application Info")
        print("  4. Logout")
        
        choice = input(f"\n{Colors.CYAN}Enter command (1-4): {Colors.YELLOW}").strip()
        print(f"{Colors.RESET}", end="")
        
        if choice == "1":
            print(f"\n{Colors.CYAN}[User Info]{Colors.RESET}")
            print(f"  Username: {auth.user_data.username}")
            print(f"  License Key: {auth.user_data.license_key}")
            print(f"  Expires: {format_expiry(auth.user_data.expiry)}")
            print(f"{Colors.GREEN}  Status: Active")
            print(f"  Access Level: {auth.user_data.level}{Colors.RESET}")
            
        elif choice == "2":
            print(f"\n{Colors.CYAN}[License Status]{Colors.RESET}")
            print(f"  Expires: {format_expiry(auth.user_data.expiry)}")
            print(f"{Colors.GREEN}  ✓ License: Valid")
            print("  ✓ Hardware Binding: Active")
            print(f"  ✓ Connection: Secure{Colors.RESET}")
            
        elif choice == "3":
            print(f"\n{Colors.CYAN}[Application Info]{Colors.RESET}")
            print(f"  App Name: {APP_NAME}")
            print(f"  Version: {APP_VER}")
            print("  Protected By: FindexAuth")
            
        elif choice == "4":
            print(f"\n{Colors.YELLOW}[*] Logging out...{Colors.RESET}")
            sys.exit(0)
            
        else:
            print(f"\n{Colors.RED}[ERROR] Invalid command. Please enter 1-4.{Colors.RESET}")

def login_flow(auth):
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗")
    print("║                        LOGIN                               ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    username = input(f"\n{Colors.WHITE}Username: {Colors.YELLOW}").strip()
    print(f"{Colors.RESET}", end="")
    if not username:
        print(f"{Colors.RED}[ERROR] Username cannot be empty!{Colors.RESET}")
        return False
        
    password = read_password(f"{Colors.WHITE}Password: {Colors.RESET}")
    if not password:
        print(f"{Colors.RED}[ERROR] Password cannot be empty!{Colors.RESET}")
        return False
        
    print(f"\n{Colors.YELLOW}[*] Logging in...{Colors.RESET}")
    
    auth.login(username, password)
    
    if auth.response.success:
        print(f"\n{Colors.GREEN}╔════════════════════════════════════════════════════════════╗")
        print("║                  ✓ LOGIN SUCCESSFUL ✓                      ║")
        print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Welcome, {auth.user_data.username}!{Colors.RESET}")
        print(f"License Key: {auth.user_data.license_key}")
        print(f"Expires: {format_expiry(auth.user_data.expiry)}")
        
        run_protected_app(auth, auth.user_data.username)
        return True
    else:
        print(f"\n{Colors.RED}✗ LOGIN FAILED: {auth.response.message}{Colors.RESET}")
        return False

def register_flow(auth):
    print(f"\n{Colors.MAGENTA}╔════════════════════════════════════════════════════════════╗")
    print("║                  REGISTER NEW ACCOUNT                      ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    license_key = input(f"\n{Colors.WHITE}License Key: {Colors.YELLOW}").strip()
    print(f"{Colors.RESET}", end="")
    if not license_key:
        print(f"{Colors.RED}[ERROR] License key cannot be empty!{Colors.RESET}")
        return False
        
    username = input(f"{Colors.WHITE}Username: {Colors.YELLOW}").strip()
    print(f"{Colors.RESET}", end="")
    if not username:
        print(f"{Colors.RED}[ERROR] Username cannot be empty!{Colors.RESET}")
        return False
        
    password = read_password(f"{Colors.WHITE}Password (min 6 chars): {Colors.RESET}")
    confirm_password = read_password(f"{Colors.WHITE}Confirm Password: {Colors.RESET}")
    
    if password != confirm_password:
        print(f"\n{Colors.RED}[ERROR] Passwords do not match!{Colors.RESET}")
        return False
        
    print(f"\n{Colors.YELLOW}[*] Verifying license and registering account...{Colors.RESET}")
    
    auth.license(license_key)
    if auth.response.success and auth.response.needs_registration:
        auth.register_key(auth.response.validated_key, username, password)
        
        if auth.response.success:
            print(f"\n{Colors.GREEN}╔════════════════════════════════════════════════════════════╗")
            print("║            ✓ REGISTRATION SUCCESSFUL ✓                     ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
            print(f"\n{Colors.CYAN}Username: {auth.user_data.username}{Colors.RESET}")
            print(f"License Key: {auth.user_data.license_key}")
            print(f"Expires: {format_expiry(auth.user_data.expiry)}")
            print(f"\n{Colors.GREEN}✓ You can now login with your credentials!{Colors.RESET}")
            return True
        else:
            print(f"\n{Colors.RED}✗ REGISTRATION FAILED: {auth.response.message}{Colors.RESET}")
            return False
    else:
        msg = auth.response.message if not auth.response.success else "License key is already registered to an account."
        print(f"\n{Colors.RED}✗ REGISTRATION FAILED: {msg}{Colors.RESET}")
        return False

def main():
    if os.name == 'nt':
        os.system('color') # Enable ANSI colors in Windows cmd
        
    print_header()
    
    print(f"\n{Colors.CYAN}[INFO] Initializing FindexAuth Client...{Colors.RESET}")
    auth = FindexAuth(APP_NAME, OWNER_ID, APP_SECRET, APP_VER, SERVER_URL, RSA_PUB_KEY)
    
    print(f"\n{Colors.GRAY}[HWID] Your Hardware ID: {auth._hwid()[:16]}...{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}[*] Connecting to FindexAuth Server...{Colors.RESET}")
    auth.init()
    
    if not auth.response.success:
        print(f"\n{Colors.RED}[ERROR] Failed to connect: {auth.response.message}{Colors.RESET}")
        input("\nPress ENTER to exit...")
        sys.exit(1)
        
    print(f"{Colors.GREEN}[SUCCESS] Connected to FindexAuth!")
    print(f"[INFO] App: {APP_NAME}{Colors.RESET}")
    print(f"{Colors.GREEN}[INFO] Version: {APP_VER} ✓{Colors.RESET}")
    
    while True:
        print(f"\n{Colors.WHITE}" + "="*60)
        print("Choose an option:")
        print("  1. Login with Username & Password")
        print("  2. Register New Account (with License Key)")
        print("  3. Exit")
        
        choice = input(f"\n> {Colors.YELLOW}").strip()
        print(f"{Colors.RESET}", end="")
        
        if choice == "1":
            if login_flow(auth):
                break
        elif choice == "2":
            register_flow(auth)
        elif choice == "3":
            print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}")
            break
        else:
            print(f"\n{Colors.RED}[ERROR] Invalid choice. Please enter 1-3.{Colors.RESET}")

if __name__ == "__main__":
    main()