"""
Test script for AutoNova ERP API
Tests the complete workflow: auth → create customer → create vehicle → retrieve data
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000'
session = requests.Session()


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_response(response, show_body=True):
    """Print formatted response"""
    status_color = '\033[92m' if response.status_code < 400 else '\033[91m'
    print(f"Status: {status_color}{response.status_code}\033[0m")
    if show_body:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    response = session.get(f'{BASE_URL}/health')
    print_response(response)
    return response.status_code == 200


def test_login():
    """Test login with admin credentials"""
    print_section("2. Login with Admin Credentials")
    response = session.post(f'{BASE_URL}/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        session.headers.update({'Authorization': f'Bearer {access_token}'})
        print("\n✓ Access token saved for subsequent requests")
        return True
    return False


def test_get_current_user():
    """Test getting current user info"""
    print_section("3. Get Current User Info")
    response = session.get(f'{BASE_URL}/api/auth/me')
    print_response(response)
    return response.status_code == 200


def test_create_customer():
    """Test creating a customer"""
    print_section("4. Create Customer (John Doe)")
    response = session.post(f'{BASE_URL}/api/customers', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '555-0123',
        'address': '123 Main St, Springfield'
    })
    print_response(response)
    
    if response.status_code == 201:
        customer_id = response.json()['customer']['id']
        print(f"\n✓ Customer created with ID: {customer_id}")
        return customer_id
    return None


def test_create_vehicle(customer_id):
    """Test creating a vehicle for a customer"""
    print_section("5. Create Vehicle (Toyota Camry)")
    response = session.post(f'{BASE_URL}/api/vehicles', json={
        'customer_id': customer_id,
        'make': 'Toyota',
        'model': 'Camry',
        'year': 2020,
        'vin': '1HGCM82633A123456',
        'license_plate': 'ABC-1234',
        'color': 'Silver',
        'mileage': 15000
    })
    print_response(response)
    
    if response.status_code == 201:
        vehicle_id = response.json()['vehicle']['id']
        print(f"\n✓ Vehicle created with ID: {vehicle_id}")
        return vehicle_id
    return None


def test_get_customer_with_vehicles(customer_id):
    """Test retrieving customer with vehicles"""
    print_section("6. Retrieve Customer with Vehicles")
    response = session.get(f'{BASE_URL}/api/customers/{customer_id}?include_vehicles=true')
    print_response(response)
    return response.status_code == 200


def test_list_customers():
    """Test listing all customers"""
    print_section("7. List All Customers")
    response = session.get(f'{BASE_URL}/api/customers')
    print_response(response)
    return response.status_code == 200


def test_get_vehicle_with_owner(vehicle_id):
    """Test retrieving vehicle with owner info"""
    print_section("8. Retrieve Vehicle with Owner Info")
    response = session.get(f'{BASE_URL}/api/vehicles/{vehicle_id}?include_owner=true')
    print_response(response)
    return response.status_code == 200


def test_role_based_access():
    """Test role-based access control"""
    print_section("9. Test Role-Based Access Control")
    
    # Try to access an endpoint that requires specific roles
    print("\nTesting access with admin role (should succeed):")
    response = session.get(f'{BASE_URL}/api/customers')
    print_response(response, show_body=False)
    
    success = response.status_code == 200
    if success:
        print("✓ Admin role has appropriate access")
    
    return success


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AutoNova ERP API Test Suite")
    print("="*60)
    print("\nMake sure the Flask server is running at http://localhost:5000")
    print("Run 'python app.py' in another terminal before running tests\n")
    
    results = []
    customer_id = None
    vehicle_id = None
    
    # Run tests in sequence
    try:
        results.append(("Health Check", test_health_check()))
        results.append(("Login", test_login()))
        results.append(("Get Current User", test_get_current_user()))
        
        customer_id = test_create_customer()
        results.append(("Create Customer", customer_id is not None))
        
        if customer_id:
            vehicle_id = test_create_vehicle(customer_id)
            results.append(("Create Vehicle", vehicle_id is not None))
            
            results.append(("Get Customer with Vehicles", test_get_customer_with_vehicles(customer_id)))
            results.append(("List Customers", test_list_customers()))
            
            if vehicle_id:
                results.append(("Get Vehicle with Owner", test_get_vehicle_with_owner(vehicle_id)))
        
        results.append(("Role-Based Access Control", test_role_based_access()))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server at http://localhost:5000")
        print("Please make sure the Flask server is running:")
        print("  python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
    
    # Print summary
    print_section("Test Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} tests passed")
    print('='*60)
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    run_tests()
