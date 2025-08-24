#!/usr/bin/env python3
"""
Additional test for profile deletion functionality
"""

import requests
import json

BASE_URL = "https://watchflix-449.preview.emergentagent.com/api"

def test_profile_deletion():
    print("🗑️ Testing Profile Deletion...")
    
    # Login as test user
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Failed to login")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create two profiles
    profile1_data = {"name": "Profile 1", "avatar": "default"}
    profile2_data = {"name": "Profile 2", "avatar": "default"}
    
    response1 = requests.post(f"{BASE_URL}/profiles", json=profile1_data, headers=headers)
    response2 = requests.post(f"{BASE_URL}/profiles", json=profile2_data, headers=headers)
    
    if response1.status_code != 200 or response2.status_code != 200:
        print("❌ Failed to create profiles")
        return False
    
    profile1_id = response1.json()["id"]
    profile2_id = response2.json()["id"]
    
    print(f"✅ Created profiles: {profile1_id}, {profile2_id}")
    
    # Delete one profile
    response = requests.delete(f"{BASE_URL}/profiles/{profile1_id}", headers=headers)
    
    if response.status_code == 200:
        print("✅ Profile deleted successfully")
        
        # Verify profile list
        response = requests.get(f"{BASE_URL}/profiles", headers=headers)
        if response.status_code == 200:
            profiles = response.json()
            if len(profiles) == 2:  # Should have 2 profiles (1 from main test + 1 remaining)
                print(f"✅ Profile count correct: {len(profiles)} profiles remaining")
                return True
            else:
                print(f"❌ Expected 2 profiles, found {len(profiles)}")
        else:
            print("❌ Failed to get profiles list")
    else:
        print(f"❌ Failed to delete profile: {response.status_code}")
    
    return False

if __name__ == "__main__":
    test_profile_deletion()