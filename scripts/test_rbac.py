#!/usr/bin/env python3
"""
Test script to demonstrate RBAC functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_rbac_system():
    """Test the RBAC system with different user roles"""
    
    print("🔐 Testing RBAC System")
    print("=" * 50)
    
    # Test users
    users = [
        {"username": "staff", "password": "staff123", "role": "Staff"},
        {"username": "legal", "password": "legal123", "role": "Legal"},
        {"username": "admin", "password": "admin123", "role": "Admin"}
    ]
    
    for user in users:
        print(f"\n👤 Testing as {user['role']} user ({user['username']})")
        print("-" * 30)
        
        # Login
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            if response.status_code != 200:
                print(f"❌ Login failed: {response.text}")
                continue
                
            token_data = response.json()
            token = token_data["access_token"]
            
            # Get user info
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(f"{BASE_URL}/me", headers=headers)
            if user_response.status_code == 200:
                user_info = user_response.json()
                print(f"✅ Logged in as: {user_info['full_name']}")
                print(f"📋 Roles: {', '.join(user_info['roles'])}")
            
            # Test search
            search_data = {
                "query": "الطاقة النووية",
                "topk": 5
            }
            
            search_response = requests.post(f"{BASE_URL}/ask", json=search_data, headers=headers)
            if search_response.status_code == 200:
                search_results = search_response.json()
                print(f"🔍 Search results: {len(search_results['citations'])} accessible")
                print(f"📊 Total found: {search_results.get('total_found', 'N/A')}")
                print(f"🔒 Accessible: {search_results.get('accessible_results', 'N/A')}")
                
                # Show document titles
                if search_results['citations']:
                    print("📄 Accessible documents:")
                    for citation in search_results['citations'][:3]:  # Show first 3
                        restricted_marker = " [RESTRICTED]" if "restricted" in citation['doc_id'].lower() else ""
                        print(f"  • {citation['doc_id']}{restricted_marker}")
                else:
                    print("❌ No accessible documents found")
                    
            else:
                print(f"❌ Search failed: {search_response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def test_file_restrictions():
    """Test specific file restriction functionality"""
    
    print(f"\n🔒 Testing File Restrictions")
    print("=" * 50)
    
    # Test with staff user (should not see restricted files)
    print("\n👤 Testing with Staff user (should NOT see restricted files)")
    
    login_data = {"username": "staff", "password": "staff123"}
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Search for restricted content
            search_data = {"query": "restricted", "topk": 10}
            search_response = requests.post(f"{BASE_URL}/ask", json=search_data, headers=headers)
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"📊 Results: {len(results['citations'])} accessible")
                
                restricted_found = any("restricted" in citation['doc_id'].lower() for citation in results['citations'])
                if restricted_found:
                    print("❌ ERROR: Staff user can see restricted documents!")
                else:
                    print("✅ CORRECT: Staff user cannot see restricted documents")
                    
    except Exception as e:
        print(f"❌ Error testing staff restrictions: {e}")
    
    # Test with legal user (should see restricted files)
    print("\n👤 Testing with Legal user (should see restricted files)")
    
    login_data = {"username": "legal", "password": "legal123"}
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Search for restricted content
            search_data = {"query": "restricted", "topk": 10}
            search_response = requests.post(f"{BASE_URL}/ask", json=search_data, headers=headers)
            
            if search_response.status_code == 200:
                results = search_response.json()
                print(f"📊 Results: {len(results['citations'])} accessible")
                
                restricted_found = any("restricted" in citation['doc_id'].lower() for citation in results['citations'])
                if restricted_found:
                    print("✅ CORRECT: Legal user can see restricted documents")
                else:
                    print("❌ ERROR: Legal user cannot see restricted documents!")
                    
    except Exception as e:
        print(f"❌ Error testing legal access: {e}")

if __name__ == "__main__":
    print("🚀 Starting RBAC System Tests")
    print("Make sure the server is running: uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload")
    print()
    
    test_rbac_system()
    test_file_restrictions()
    
    print(f"\n🎉 RBAC Testing Complete!")
    print("=" * 50)
    print("Summary:")
    print("• Staff users can only access general documents")
    print("• Legal users can access general + restricted documents") 
    print("• Admin users have full access to all documents")
    print("• Documents with 'restricted' in their names are automatically restricted")
