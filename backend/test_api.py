"""
Complete API test script for AutoNova ERP backend
Tests the full workflow: login → create customer → create vehicle → retrieve data
"""
import requests
import json

# Configuration
BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

# Test credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(message):
    """Print test message"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {message}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}→ {message}{RESET}")


def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")
    
    response = requests.get(f'{BASE_URL}/health')
    
    if response.status_code == 200:
        print_success(f"Health check passed: {response.json()}")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False


def test_login():
    """Test login with admin credentials"""
    print_test("Admin Login")
    
    response = requests.post(
        f'{API_URL}/auth/login',
        json={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Login successful")
        print_info(f"User: {data['user']['username']} ({data['user']['role']['name']})")
        return data['access_token']
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None


def test_get_current_user(token):
    """Test getting current user info"""
    print_test("Get Current User Info")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/auth/me', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Current user: {data['user']['username']}")
        return True
    else:
        print_error(f"Get user failed: {response.status_code}")
        return False


def test_create_customer(token):
    """Test creating a customer"""
    print_test("Create Customer")
    
    headers = {'Authorization': f'Bearer {token}'}
    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '555-1234',
        'address': '123 Main St',
        'city': 'Springfield',
        'state': 'IL',
        'zip_code': '62701'
    }
    
    response = requests.post(
        f'{API_URL}/customers',
        json=customer_data,
        headers=headers
    )
    
    if response.status_code == 201:
        data = response.json()
        customer = data['customer']
        print_success(f"Customer created: {customer['first_name']} {customer['last_name']} (ID: {customer['id']})")
        return customer['id']
    else:
        print_error(f"Create customer failed: {response.status_code} - {response.text}")
        return None


def test_create_vehicle(token, customer_id):
    """Test creating a vehicle"""
    print_test("Create Vehicle")
    
    headers = {'Authorization': f'Bearer {token}'}
    vehicle_data = {
        'customer_id': customer_id,
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2020,
        'vin': 'JT2BF18K3X0123456',
        'license_plate': 'ABC-1234',
        'color': 'Silver',
        'mileage': 45000
    }
    
    response = requests.post(
        f'{API_URL}/vehicles',
        json=vehicle_data,
        headers=headers
    )
    
    if response.status_code == 201:
        data = response.json()
        vehicle = data['vehicle']
        print_success(f"Vehicle created: {vehicle['year']} {vehicle['make']} {vehicle['model']} (ID: {vehicle['id']})")
        return vehicle['id']
    else:
        print_error(f"Create vehicle failed: {response.status_code} - {response.text}")
        return None


def test_get_customer_with_vehicles(token, customer_id):
    """Test retrieving customer with vehicles"""
    print_test("Get Customer with Vehicles")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{API_URL}/customers/{customer_id}?include_vehicles=true',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        customer = data['customer']
        print_success(f"Customer retrieved: {customer['first_name']} {customer['last_name']}")
        print_info(f"Number of vehicles: {len(customer.get('vehicles', []))}")
        
        if customer.get('vehicles'):
            for vehicle in customer['vehicles']:
                print_info(f"  - {vehicle['year']} {vehicle['make']} {vehicle['model']}")
        
        return True
    else:
        print_error(f"Get customer failed: {response.status_code}")
        return False


def test_get_all_customers(token):
    """Test retrieving all customers"""
    print_test("Get All Customers (List)")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/customers', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['customers'])} customers")
        print_info(f"Total customers: {data['total']}")
        print_info(f"Page: {data['page']}/{data['pages']}")
        return True
    else:
        print_error(f"Get customers failed: {response.status_code}")
        return False


def test_get_vehicle_with_owner(token, vehicle_id):
    """Test retrieving vehicle with owner info"""
    print_test("Get Vehicle with Owner Info")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{API_URL}/vehicles/{vehicle_id}?include_owner=true',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        vehicle = data['vehicle']
        print_success(f"Vehicle retrieved: {vehicle['year']} {vehicle['make']} {vehicle['model']}")
        
        if vehicle.get('owner'):
            owner = vehicle['owner']
            print_info(f"Owner: {owner['first_name']} {owner['last_name']}")
        
        return True
    else:
        print_error(f"Get vehicle failed: {response.status_code}")
        return False


def test_role_based_access_control(token):
    """Test role-based access control"""
    print_test("Role-Based Access Control (Create Customer as Admin)")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Admin should be able to create customer
    customer_data = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'phone': '555-5678'
    }
    
    response = requests.post(
        f'{API_URL}/customers',
        json=customer_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print_success("Admin can create customer (RBAC working)")
        return True
    else:
        print_error(f"RBAC test failed: {response.status_code}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{GREEN}{'='*60}")
    print("AutoNova ERP Backend API Test Suite")
    print(f"{'='*60}{RESET}\n")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Login
    token = test_login()
    if not token:
        print_error("\nCannot continue without authentication token")
        return
    results.append(("Login", True))
    
    # Test 3: Get current user
    results.append(("Get Current User", test_get_current_user(token)))
    
    # Test 4: Create customer
    customer_id = test_create_customer(token)
    if not customer_id:
        print_error("\nCannot continue without customer")
        return
    results.append(("Create Customer", True))
    
    # Test 5: Create vehicle
    vehicle_id = test_create_vehicle(token, customer_id)
    if not vehicle_id:
        print_error("\nCannot continue without vehicle")
        return
    results.append(("Create Vehicle", True))
    
    # Test 6: Get customer with vehicles
    results.append(("Get Customer with Vehicles", test_get_customer_with_vehicles(token, customer_id)))
    
    # Test 7: Get all customers
    results.append(("Get All Customers", test_get_all_customers(token)))
    
    # Test 8: Get vehicle with owner
    results.append(("Get Vehicle with Owner", test_get_vehicle_with_owner(token, vehicle_id)))
    
    # Test 9: Role-based access control
    results.append(("Role-Based Access Control", test_role_based_access_control(token)))
    
    # Print summary
    print(f"\n{BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}ALL TESTS PASSED ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}SOME TESTS FAILED ({passed}/{total}){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


if __name__ == '__main__':
    try:
        run_all_tests()
    except Exception as e:
        print_error(f"\nTest suite error: {str(e)}")
        import traceback
        traceback.print_exc()
