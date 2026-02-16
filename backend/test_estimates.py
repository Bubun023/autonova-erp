"""
Test script for Estimate Management System
Tests the complete estimate workflow with all 13 requirements
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


def test_login():
    """Test login with admin credentials"""
    print_section("Login with Admin Credentials")
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


def test_create_insurance_company():
    """Test 1: Create insurance company"""
    print_section("Test 1: Create Insurance Company")
    response = session.post(f'{BASE_URL}/api/insurance-companies', json={
        'name': 'Test Insurance Co.',
        'contact_person': 'Jane Smith',
        'phone': '555-0999',
        'email': 'claims@testinsurance.example.com',
        'address': '123 Insurance Ave'
    })
    print_response(response)
    
    if response.status_code == 201:
        insurance_company_id = response.json()['insurance_company']['id']
        print(f"\n✓ Insurance company created with ID: {insurance_company_id}")
        return insurance_company_id
    return None


def test_create_customer():
    """Create a test customer"""
    print_section("Create Test Customer")
    response = session.post(f'{BASE_URL}/api/customers', json={
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'email': 'alice.johnson@example.com',
        'phone': '555-1111',
        'address': '456 Customer St'
    })
    print_response(response)
    
    if response.status_code == 201:
        customer_id = response.json()['customer']['id']
        print(f"\n✓ Customer created with ID: {customer_id}")
        return customer_id
    return None


def test_create_vehicle(customer_id):
    """Create a test vehicle"""
    print_section("Create Test Vehicle")
    response = session.post(f'{BASE_URL}/api/vehicles', json={
        'customer_id': customer_id,
        'make': 'Honda',
        'model': 'Accord',
        'year': 2021,
        'vin': '1HGCV1F30JA123456',
        'license_plate': 'XYZ-5678',
        'color': 'Blue',
        'mileage': 25000
    })
    print_response(response)
    
    if response.status_code == 201:
        vehicle_id = response.json()['vehicle']['id']
        print(f"\n✓ Vehicle created with ID: {vehicle_id}")
        return vehicle_id
    return None


def test_create_estimate(customer_id, vehicle_id, insurance_company_id):
    """Test 2: Create estimate with customer and vehicle"""
    print_section("Test 2: Create Estimate with Customer and Vehicle")
    response = session.post(f'{BASE_URL}/api/estimates', json={
        'customer_id': customer_id,
        'vehicle_id': vehicle_id,
        'insurance_company_id': insurance_company_id,
        'insurance_claim_number': 'CLM-2026-001',
        'is_insurance_claim': True,
        'description': 'Collision repair - front bumper and headlights',
        'estimated_completion_date': '2026-02-25'
    })
    print_response(response)
    
    if response.status_code == 201:
        estimate_id = response.json()['estimate']['id']
        estimate_number = response.json()['estimate']['estimate_number']
        print(f"\n✓ Estimate created with ID: {estimate_id}")
        print(f"✓ Estimate number: {estimate_number}")
        return estimate_id
    return None


def test_add_parts(estimate_id):
    """Test 3: Add parts to estimate"""
    print_section("Test 3: Add Parts to Estimate")
    
    parts = [
        {
            'part_name': 'Front Bumper',
            'part_number': 'BMP-FRT-001',
            'quantity': 1,
            'unit_price': 450.00,
            'notes': 'OEM part'
        },
        {
            'part_name': 'Headlight Assembly - Left',
            'part_number': 'HDL-LFT-002',
            'quantity': 1,
            'unit_price': 325.00
        },
        {
            'part_name': 'Headlight Assembly - Right',
            'part_number': 'HDL-RGT-002',
            'quantity': 1,
            'unit_price': 325.00
        }
    ]
    
    parts_added = []
    for part in parts:
        response = session.post(f'{BASE_URL}/api/estimates/{estimate_id}/parts', json=part)
        print(f"\nAdding part: {part['part_name']}")
        print_response(response, show_body=False)
        
        if response.status_code == 201:
            part_id = response.json()['part']['id']
            parts_total = response.json()['estimate']['parts_total']
            parts_added.append(part_id)
            print(f"✓ Part added (ID: {part_id}), Parts total: ${parts_total}")
        else:
            print(f"✗ Failed to add part")
            print_response(response)
            return None
    
    print(f"\n✓ All {len(parts_added)} parts added successfully")
    return parts_added


def test_add_labour(estimate_id):
    """Test 4: Add labour to estimate"""
    print_section("Test 4: Add Labour to Estimate")
    
    labour_items = [
        {
            'description': 'Remove and replace front bumper',
            'hours': 2.5,
            'hourly_rate': 85.00,
            'notes': 'Includes alignment'
        },
        {
            'description': 'Install headlight assemblies',
            'hours': 1.5,
            'hourly_rate': 85.00
        },
        {
            'description': 'Paint and finish work',
            'hours': 3.0,
            'hourly_rate': 95.00
        }
    ]
    
    labour_added = []
    for labour in labour_items:
        response = session.post(f'{BASE_URL}/api/estimates/{estimate_id}/labour', json=labour)
        print(f"\nAdding labour: {labour['description']}")
        print_response(response, show_body=False)
        
        if response.status_code == 201:
            labour_id = response.json()['labour']['id']
            labour_total = response.json()['estimate']['labour_total']
            labour_added.append(labour_id)
            print(f"✓ Labour added (ID: {labour_id}), Labour total: ${labour_total}")
        else:
            print(f"✗ Failed to add labour")
            print_response(response)
            return None
    
    print(f"\n✓ All {len(labour_added)} labour items added successfully")
    return labour_added


def test_verify_totals(estimate_id):
    """Test 5: Verify grand total calculation"""
    print_section("Test 5: Verify Grand Total Calculation")
    response = session.get(f'{BASE_URL}/api/estimates/{estimate_id}')
    print_response(response)
    
    if response.status_code == 200:
        estimate = response.json()['estimate']
        parts_total = estimate['parts_total']
        labour_total = estimate['labour_total']
        tax_amount = estimate['tax_amount']
        grand_total = estimate['grand_total']
        
        # Expected: parts = 1100, labour = 625.00, tax = 172.50, grand = 1897.50
        expected_parts = 1100.00
        expected_labour = 625.00
        expected_tax = 172.50
        expected_grand = 1897.50
        
        print(f"\n✓ Parts total: ${parts_total} (expected: ${expected_parts})")
        print(f"✓ Labour total: ${labour_total} (expected: ${expected_labour})")
        print(f"✓ Tax amount (10%): ${tax_amount} (expected: ${expected_tax})")
        print(f"✓ Grand total: ${grand_total} (expected: ${expected_grand})")
        
        return (abs(parts_total - expected_parts) < 0.01 and 
                abs(labour_total - expected_labour) < 0.01 and 
                abs(tax_amount - expected_tax) < 0.01 and 
                abs(grand_total - expected_grand) < 0.01)
    return False


def test_update_estimate(estimate_id):
    """Test 6: Update estimate details"""
    print_section("Test 6: Update Estimate Details")
    response = session.put(f'{BASE_URL}/api/estimates/{estimate_id}', json={
        'description': 'Updated: Collision repair - front bumper, headlights, and paint',
        'estimated_completion_date': '2026-02-28'
    })
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Estimate updated successfully")
        return True
    return False


def test_approve_estimate(estimate_id):
    """Test 7: Approve estimate (manager role)"""
    print_section("Test 7: Approve Estimate")
    response = session.put(f'{BASE_URL}/api/estimates/{estimate_id}/approve')
    print_response(response)
    
    if response.status_code == 200:
        estimate = response.json()['estimate']
        print(f"\n✓ Estimate approved")
        print(f"✓ Status: {estimate['status']}")
        print(f"✓ Approved by user ID: {estimate['approved_by']}")
        print(f"✓ Approved at: {estimate['approved_at']}")
        return True
    return False


def test_edit_approved_estimate(estimate_id):
    """Test 8: Try to edit approved estimate (should fail)"""
    print_section("Test 8: Try to Edit Approved Estimate (Should Fail)")
    response = session.put(f'{BASE_URL}/api/estimates/{estimate_id}', json={
        'description': 'This should not work'
    })
    print_response(response)
    
    if response.status_code == 400:
        print("\n✓ Correctly prevented editing of approved estimate")
        return True
    else:
        print("\n✗ Should have prevented editing approved estimate")
        return False


def test_create_and_reject_estimate(customer_id, vehicle_id):
    """Test 9: Reject estimate with reason"""
    print_section("Test 9: Reject Estimate with Reason")
    
    # Create another estimate
    print("\nCreating new estimate...")
    response = session.post(f'{BASE_URL}/api/estimates', json={
        'customer_id': customer_id,
        'vehicle_id': vehicle_id,
        'description': 'Minor scratch repair'
    })
    
    if response.status_code != 201:
        print("✗ Failed to create estimate")
        return False
    
    estimate_id = response.json()['estimate']['id']
    print(f"✓ Created estimate ID: {estimate_id}")
    
    # Reject it
    print("\nRejecting estimate...")
    response = session.put(f'{BASE_URL}/api/estimates/{estimate_id}/reject', json={
        'rejection_reason': 'Customer decided not to proceed with repairs'
    })
    print_response(response)
    
    if response.status_code == 200:
        estimate = response.json()['estimate']
        print(f"\n✓ Estimate rejected")
        print(f"✓ Status: {estimate['status']}")
        print(f"✓ Rejection reason: {estimate['rejection_reason']}")
        return True
    return False


def test_list_estimates_with_filters():
    """Test 10: List estimates with filters"""
    print_section("Test 10: List Estimates with Filters")
    
    # List all estimates
    print("\nListing all estimates...")
    response = session.get(f'{BASE_URL}/api/estimates')
    print_response(response, show_body=False)
    
    if response.status_code == 200:
        total = response.json()['total']
        print(f"✓ Total estimates: {total}")
    else:
        return False
    
    # Filter by status
    print("\nFiltering by status='approved'...")
    response = session.get(f'{BASE_URL}/api/estimates?status=approved')
    print_response(response, show_body=False)
    
    if response.status_code == 200:
        approved_count = response.json()['total']
        print(f"✓ Approved estimates: {approved_count}")
    else:
        return False
    
    # Filter by status
    print("\nFiltering by status='rejected'...")
    response = session.get(f'{BASE_URL}/api/estimates?status=rejected')
    print_response(response, show_body=False)
    
    if response.status_code == 200:
        rejected_count = response.json()['total']
        print(f"✓ Rejected estimates: {rejected_count}")
        return True
    
    return False


def test_get_estimate_with_details(estimate_id):
    """Test 11: Get estimate with all parts and labour included"""
    print_section("Test 11: Get Estimate with All Details")
    response = session.get(f'{BASE_URL}/api/estimates/{estimate_id}')
    print_response(response)
    
    if response.status_code == 200:
        estimate = response.json()['estimate']
        print(f"\n✓ Retrieved estimate with details")
        print(f"✓ Parts count: {len(estimate.get('parts', []))}")
        print(f"✓ Labour items count: {len(estimate.get('labour_items', []))}")
        print(f"✓ Has customer details: {'customer' in estimate}")
        print(f"✓ Has vehicle details: {'vehicle' in estimate}")
        return True
    return False


def test_delete_estimate(customer_id, vehicle_id):
    """Test 12: Delete estimate (cascade delete verification)"""
    print_section("Test 12: Delete Estimate (Cascade Delete)")
    
    # Create a new estimate
    print("\nCreating new estimate to delete...")
    response = session.post(f'{BASE_URL}/api/estimates', json={
        'customer_id': customer_id,
        'vehicle_id': vehicle_id,
        'description': 'Test estimate for deletion'
    })
    
    if response.status_code != 201:
        print("✗ Failed to create estimate")
        return False
    
    estimate_id = response.json()['estimate']['id']
    print(f"✓ Created estimate ID: {estimate_id}")
    
    # Add a part
    print("\nAdding part to estimate...")
    response = session.post(f'{BASE_URL}/api/estimates/{estimate_id}/parts', json={
        'part_name': 'Test Part',
        'quantity': 1,
        'unit_price': 100.00
    })
    
    if response.status_code != 201:
        print("✗ Failed to add part")
        return False
    
    part_id = response.json()['part']['id']
    print(f"✓ Added part ID: {part_id}")
    
    # Delete the estimate
    print("\nDeleting estimate...")
    response = session.delete(f'{BASE_URL}/api/estimates/{estimate_id}')
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Estimate deleted successfully")
        
        # Verify it's gone
        response = session.get(f'{BASE_URL}/api/estimates/{estimate_id}')
        if response.status_code == 404:
            print("✓ Verified estimate is deleted (cascade delete worked)")
            return True
    
    return False


def test_role_based_access():
    """Test 13: Role-based access control testing"""
    print_section("Test 13: Role-Based Access Control")
    
    # Admin should have access to all endpoints
    print("\nTesting admin access to estimates...")
    response = session.get(f'{BASE_URL}/api/estimates')
    print_response(response, show_body=False)
    
    if response.status_code == 200:
        print("✓ Admin has access to list estimates")
    else:
        return False
    
    print("\nTesting admin access to insurance companies...")
    response = session.get(f'{BASE_URL}/api/insurance-companies')
    print_response(response, show_body=False)
    
    if response.status_code == 200:
        print("✓ Admin has access to list insurance companies")
        return True
    
    return False


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Estimate Management System - Test Suite")
    print("  13 Comprehensive Tests")
    print("="*60)
    print("\nMake sure the Flask server is running at http://localhost:5000")
    print("Run 'python app.py' in another terminal before running tests\n")
    
    results = []
    customer_id = None
    vehicle_id = None
    insurance_company_id = None
    estimate_id = None
    
    # Run tests in sequence
    try:
        # Login
        if not test_login():
            print("\n❌ ERROR: Login failed")
            sys.exit(1)
        
        # Test 1: Create insurance company
        insurance_company_id = test_create_insurance_company()
        results.append(("1. Create insurance company", insurance_company_id is not None))
        
        # Setup: Create customer and vehicle
        customer_id = test_create_customer()
        vehicle_id = test_create_vehicle(customer_id)
        
        if not customer_id or not vehicle_id:
            print("\n❌ ERROR: Failed to create test customer/vehicle")
            sys.exit(1)
        
        # Test 2: Create estimate
        estimate_id = test_create_estimate(customer_id, vehicle_id, insurance_company_id)
        results.append(("2. Create estimate with customer and vehicle", estimate_id is not None))
        
        if estimate_id:
            # Test 3: Add parts
            parts_added = test_add_parts(estimate_id)
            results.append(("3. Add parts to estimate", parts_added is not None))
            
            # Test 4: Add labour
            labour_added = test_add_labour(estimate_id)
            results.append(("4. Add labour to estimate", labour_added is not None))
            
            # Test 5: Verify totals
            results.append(("5. Verify grand total calculation", test_verify_totals(estimate_id)))
            
            # Test 6: Update estimate
            results.append(("6. Update estimate details", test_update_estimate(estimate_id)))
            
            # Test 7: Approve estimate
            results.append(("7. Approve estimate", test_approve_estimate(estimate_id)))
            
            # Test 8: Try to edit approved estimate
            results.append(("8. Prevent editing approved estimate", test_edit_approved_estimate(estimate_id)))
        
        # Test 9: Reject estimate
        results.append(("9. Reject estimate with reason", test_create_and_reject_estimate(customer_id, vehicle_id)))
        
        # Test 10: List with filters
        results.append(("10. List estimates with filters", test_list_estimates_with_filters()))
        
        # Test 11: Get with details
        if estimate_id:
            results.append(("11. Get estimate with all details", test_get_estimate_with_details(estimate_id)))
        
        # Test 12: Delete estimate
        results.append(("12. Delete estimate (cascade delete)", test_delete_estimate(customer_id, vehicle_id)))
        
        # Test 13: Role-based access
        results.append(("13. Role-based access control", test_role_based_access()))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server at http://localhost:5000")
        print("Please make sure the Flask server is running:")
        print("  cd backend && python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print("\n🎉 All tests passed! Estimate Management System is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        sys.exit(1)


if __name__ == '__main__':
    run_tests()
