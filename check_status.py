#!/usr/bin/env python3
"""
AutoNova ERP - System Status Checker
This script checks the current state of your application
"""

import os
import sys
import subprocess

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def check_item(name, status, details=""):
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {name:<50} {details}")
    return status

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    print_header("AutoNova ERP - System Status Report")
    
    all_checks_passed = True
    
    # Check 1: Backend directory
    print_header("📁 Project Structure")
    backend_exists = os.path.exists('backend')
    all_checks_passed &= check_item("Backend directory exists", backend_exists)
    
    if backend_exists:
        os.chdir('backend')
        
        # Check important files
        files_to_check = [
            'app.py', 'config.py', 'models.py', 'utils.py',
            'requirements.txt', '.env', 'seed.py', 'test_api.py'
        ]
        
        for file in files_to_check:
            exists = os.path.exists(file)
            all_checks_passed &= check_item(f"{file}", exists)
        
        # Check routes
        routes_exist = os.path.exists('routes')
        all_checks_passed &= check_item("routes/ directory", routes_exist)
        
        if routes_exist:
            route_files = ['__init__.py', 'auth.py', 'customers.py', 'vehicles.py']
            for file in route_files:
                exists = os.path.exists(f'routes/{file}')
                all_checks_passed &= check_item(f"routes/{file}", exists)
    
    # Check 2: Python dependencies
    print_header("📦 Dependencies")
    
    packages = [
        'Flask', 'Flask-SQLAlchemy', 'Flask-Migrate', 'Flask-JWT-Extended',
        'Flask-Bcrypt', 'Flask-CORS', 'python-dotenv'
    ]
    
    for package in packages:
        success, output = run_command(f"pip show {package} > /dev/null 2>&1")
        all_checks_passed &= check_item(package, success)
    
    # Check 3: Database
    print_header("🗄️  Database")
    
    db_exists = os.path.exists('autonova.db')
    check_item("Database file (autonova.db)", db_exists)
    
    if db_exists:
        size = os.path.getsize('autonova.db')
        check_item("Database size", size > 0, f"{size:,} bytes")
    
    migrations_exist = os.path.exists('migrations')
    check_item("Migrations directory", migrations_exist)
    
    # Check 4: Server status
    print_header("🚀 Server Status")
    
    success, output = run_command("curl -s http://localhost:5000/health")
    server_running = success and 'healthy' in output.lower()
    check_item("Server running on port 5000", server_running)
    
    if server_running:
        print(f"\n{GREEN}Server Response:{RESET}")
        print(f"  {output}\n")
    else:
        print(f"\n{YELLOW}Note: Server not running. Start it with: python app.py{RESET}\n")
    
    # Check 5: Environment configuration
    print_header("⚙️  Configuration")
    
    env_exists = os.path.exists('.env')
    check_item(".env file exists", env_exists)
    
    if env_exists:
        with open('.env', 'r') as f:
            content = f.read()
            has_jwt = 'JWT_SECRET_KEY' in content
            has_flask_app = 'FLASK_APP' in content
            check_item("JWT_SECRET_KEY configured", has_jwt)
            check_item("FLASK_APP configured", has_flask_app)
    
    # Check 6: Git status
    print_header("📝 Git Status")
    
    success, branch = run_command("git rev-parse --abbrev-ref HEAD")
    if success:
        check_item("Current branch", True, branch)
    
    success, commits = run_command("git log --oneline -1")
    if success:
        check_item("Latest commit", True, commits[:60])
    
    # Summary
    print_header("Summary")
    
    if server_running:
        print(f"{GREEN}✅ Your application is RUNNING and READY!{RESET}\n")
        print("You can access:")
        print(f"  • API Health Check: {BLUE}http://localhost:5000/health{RESET}")
        print(f"  • Login Endpoint: {BLUE}http://localhost:5000/api/auth/login{RESET}")
        print(f"\nDefault credentials:")
        print(f"  • Username: {GREEN}admin{RESET}")
        print(f"  • Password: {GREEN}admin123{RESET}")
        print(f"\nRun tests with: {YELLOW}python test_api.py{RESET}")
    else:
        print(f"{YELLOW}⚠️  Application files are ready but server is not running.{RESET}\n")
        print("To start the server:")
        print(f"  {YELLOW}cd backend && python app.py{RESET}\n")
        print("To run tests:")
        print(f"  {YELLOW}cd backend && python test_api.py{RESET}")
    
    print(f"\n{BLUE}For detailed information, see: STATUS.md{RESET}\n")
    
    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    try:
        # Try to go to repo root
        if not os.path.exists('backend') and os.path.exists('../backend'):
            os.chdir('..')
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Status check interrupted.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}")
        sys.exit(1)
