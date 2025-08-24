#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for StreamFlix Platform
Tests all authentication, profile management, movie API, and core functionality
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://watchflix-449.preview.emergentagent.com/api"
TIMEOUT = 30

class StreamFlixTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        self.test_profile_id = None
        self.test_movie_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, error_message)"""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                params=params
            )
            return True, response, None
        except Exception as e:
            return False, None, str(e)
    
    def test_health_check(self):
        """Test health endpoint"""
        print("\n🏥 Testing Health Check...")
        success, response, error = self.make_request("GET", "/health")
        
        if not success:
            self.log_result("Health Check - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "healthy":
                self.log_result("Health Check", True, "API is healthy")
                return True
            else:
                self.log_result("Health Check", False, f"Unexpected response: {data}")
        else:
            self.log_result("Health Check", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration...")
        
        # Test with valid data
        user_data = {
            "email": "test@example.com",
            "password": "test123"
        }
        
        success, response, error = self.make_request("POST", "/auth/register", user_data)
        
        if not success:
            self.log_result("User Registration - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "refresh_token" in data:
                self.user_token = data["access_token"]
                self.log_result("User Registration", True, "User registered successfully with tokens")
                return True
            else:
                self.log_result("User Registration", False, f"Missing tokens in response: {data}")
        else:
            self.log_result("User Registration", False, f"Status code: {response.status_code}, Response: {response.text}")
        
        return False
    
    def test_user_login(self):
        """Test user login"""
        print("\n🔐 Testing User Login...")
        
        login_data = {
            "email": "test@example.com",
            "password": "test123"
        }
        
        success, response, error = self.make_request("POST", "/auth/login", login_data)
        
        if not success:
            self.log_result("User Login - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.user_token = data["access_token"]
                self.log_result("User Login", True, "Login successful")
                return True
            else:
                self.log_result("User Login", False, f"Missing access_token: {data}")
        else:
            self.log_result("User Login", False, f"Status code: {response.status_code}, Response: {response.text}")
        
        return False
    
    def test_admin_login(self):
        """Test admin login"""
        print("\n👑 Testing Admin Login...")
        
        admin_data = {
            "email": "admin@streamflix.com",
            "password": "admin123"
        }
        
        success, response, error = self.make_request("POST", "/auth/login", admin_data)
        
        if not success:
            self.log_result("Admin Login - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.admin_token = data["access_token"]
                self.log_result("Admin Login", True, "Admin login successful")
                return True
            else:
                self.log_result("Admin Login", False, f"Missing access_token: {data}")
        else:
            self.log_result("Admin Login", False, f"Status code: {response.status_code}, Response: {response.text}")
        
        return False
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        print("\n🔒 Testing Protected Endpoint Access (No Token)...")
        
        success, response, error = self.make_request("GET", "/auth/me")
        
        if not success:
            self.log_result("Protected Access (No Token) - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 403 or response.status_code == 401:
            self.log_result("Protected Access (No Token)", True, "Correctly rejected unauthorized access")
            return True
        else:
            self.log_result("Protected Access (No Token)", False, f"Expected 401/403, got {response.status_code}")
        
        return False
    
    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        print("\n🔓 Testing Protected Endpoint Access (With Token)...")
        
        if not self.user_token:
            self.log_result("Protected Access (With Token)", False, "No user token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, error = self.make_request("GET", "/auth/me", headers=headers)
        
        if not success:
            self.log_result("Protected Access (With Token) - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "email" in data and data["email"] == "test@example.com":
                self.test_user_id = data.get("id")
                self.log_result("Protected Access (With Token)", True, "Successfully accessed protected endpoint")
                return True
            else:
                self.log_result("Protected Access (With Token)", False, f"Unexpected user data: {data}")
        else:
            self.log_result("Protected Access (With Token)", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_create_profile(self):
        """Test creating user profile"""
        print("\n👥 Testing Profile Creation...")
        
        if not self.user_token:
            self.log_result("Profile Creation", False, "No user token available")
            return False
        
        profile_data = {
            "name": "Test Profile",
            "avatar": "default",
            "language": "en",
            "maturity_rating": "PG-13"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, error = self.make_request("POST", "/profiles", profile_data, headers)
        
        if not success:
            self.log_result("Profile Creation - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "name" in data and data["name"] == "Test Profile":
                self.test_profile_id = data["id"]
                self.log_result("Profile Creation", True, "Profile created successfully")
                return True
            else:
                self.log_result("Profile Creation", False, f"Unexpected profile data: {data}")
        else:
            self.log_result("Profile Creation", False, f"Status code: {response.status_code}, Response: {response.text}")
        
        return False
    
    def test_list_profiles(self):
        """Test listing user profiles"""
        print("\n📋 Testing Profile Listing...")
        
        if not self.user_token:
            self.log_result("Profile Listing", False, "No user token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, error = self.make_request("GET", "/profiles", headers=headers)
        
        if not success:
            self.log_result("Profile Listing - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.log_result("Profile Listing", True, f"Found {len(data)} profiles")
                return True
            else:
                self.log_result("Profile Listing", False, f"Expected list with profiles, got: {data}")
        else:
            self.log_result("Profile Listing", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_update_profile(self):
        """Test updating profile"""
        print("\n✏️ Testing Profile Update...")
        
        if not self.user_token or not self.test_profile_id:
            self.log_result("Profile Update", False, "No user token or profile ID available")
            return False
        
        update_data = {
            "name": "Updated Test Profile",
            "language": "es"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, error = self.make_request("PUT", f"/profiles/{self.test_profile_id}", update_data, headers)
        
        if not success:
            self.log_result("Profile Update - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if data.get("name") == "Updated Test Profile" and data.get("language") == "es":
                self.log_result("Profile Update", True, "Profile updated successfully")
                return True
            else:
                self.log_result("Profile Update", False, f"Update not reflected: {data}")
        else:
            self.log_result("Profile Update", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_get_movies(self):
        """Test getting movies list"""
        print("\n🎬 Testing Movies List...")
        
        success, response, error = self.make_request("GET", "/movies")
        
        if not success:
            self.log_result("Movies List - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 8:  # Should have 8 seeded movies
                self.test_movie_id = data[0]["id"]  # Store first movie ID for later tests
                self.log_result("Movies List", True, f"Found {len(data)} movies as expected")
                return True
            else:
                self.log_result("Movies List", False, f"Expected 8 movies, got: {len(data) if isinstance(data, list) else 'not a list'}")
        else:
            self.log_result("Movies List", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_get_movie_by_id(self):
        """Test getting specific movie by ID"""
        print("\n🎯 Testing Get Movie by ID...")
        
        if not self.test_movie_id:
            self.log_result("Get Movie by ID", False, "No movie ID available")
            return False
        
        success, response, error = self.make_request("GET", f"/movies/{self.test_movie_id}")
        
        if not success:
            self.log_result("Get Movie by ID - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and data["id"] == self.test_movie_id:
                self.log_result("Get Movie by ID", True, f"Retrieved movie: {data.get('title', 'Unknown')}")
                return True
            else:
                self.log_result("Get Movie by ID", False, f"Movie ID mismatch: {data}")
        else:
            self.log_result("Get Movie by ID", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_movies_with_filters(self):
        """Test movies with various filters"""
        print("\n🔍 Testing Movies with Filters...")
        
        # Test category filter
        success, response, error = self.make_request("GET", "/movies", params={"category": "action"})
        
        if not success:
            self.log_result("Movies Filter (Category) - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                action_movies = [m for m in data if m.get("category") == "action"]
                if len(action_movies) > 0:
                    self.log_result("Movies Filter (Category)", True, f"Found {len(action_movies)} action movies")
                else:
                    self.log_result("Movies Filter (Category)", False, "No action movies found")
            else:
                self.log_result("Movies Filter (Category)", False, "Response is not a list")
        else:
            self.log_result("Movies Filter (Category)", False, f"Status code: {response.status_code}")
        
        # Test search filter
        success, response, error = self.make_request("GET", "/movies", params={"search": "Buck"})
        
        if success and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.log_result("Movies Filter (Search)", True, f"Search found {len(data)} movies")
            else:
                self.log_result("Movies Filter (Search)", False, "Search returned no results")
        else:
            self.log_result("Movies Filter (Search)", False, "Search filter failed")
        
        return True
    
    def test_admin_movie_operations(self):
        """Test admin movie CRUD operations"""
        print("\n👑 Testing Admin Movie Operations...")
        
        if not self.admin_token:
            self.log_result("Admin Movie Operations", False, "No admin token available")
            return False
        
        # Test creating a movie as admin
        movie_data = {
            "slug": "test-movie",
            "title": "Test Movie",
            "description": "A test movie for API testing",
            "category": "comedy",
            "poster_url": "https://example.com/poster.jpg",
            "backdrop_url": "https://example.com/backdrop.jpg",
            "video_url": "https://example.com/video.mp4",
            "release_year": 2024,
            "rating": 7.5,
            "duration_minutes": 120,
            "tags": ["test", "comedy"],
            "languages": ["en"]
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        success, response, error = self.make_request("POST", "/movies", movie_data, headers)
        
        if not success:
            self.log_result("Admin Create Movie - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and data["title"] == "Test Movie":
                created_movie_id = data["id"]
                self.log_result("Admin Create Movie", True, "Movie created successfully")
                
                # Test updating the movie
                update_data = {
                    "title": "Updated Test Movie",
                    "rating": 8.0
                }
                
                success, response, error = self.make_request("PUT", f"/movies/{created_movie_id}", update_data, headers)
                
                if success and response.status_code == 200:
                    updated_data = response.json()
                    if updated_data.get("title") == "Updated Test Movie":
                        self.log_result("Admin Update Movie", True, "Movie updated successfully")
                    else:
                        self.log_result("Admin Update Movie", False, "Update not reflected")
                else:
                    self.log_result("Admin Update Movie", False, f"Update failed: {response.status_code if response else error}")
                
                # Test deleting the movie
                success, response, error = self.make_request("DELETE", f"/movies/{created_movie_id}", headers=headers)
                
                if success and response.status_code == 200:
                    self.log_result("Admin Delete Movie", True, "Movie deleted successfully")
                else:
                    self.log_result("Admin Delete Movie", False, f"Delete failed: {response.status_code if response else error}")
                
                return True
            else:
                self.log_result("Admin Create Movie", False, f"Unexpected response: {data}")
        else:
            self.log_result("Admin Create Movie", False, f"Status code: {response.status_code}, Response: {response.text}")
        
        return False
    
    def test_regular_user_movie_operations(self):
        """Test that regular users cannot perform admin movie operations"""
        print("\n🚫 Testing Regular User Movie Restrictions...")
        
        if not self.user_token:
            self.log_result("Regular User Movie Restrictions", False, "No user token available")
            return False
        
        movie_data = {
            "slug": "unauthorized-movie",
            "title": "Unauthorized Movie",
            "description": "This should not be created",
            "category": "comedy",
            "poster_url": "https://example.com/poster.jpg",
            "backdrop_url": "https://example.com/backdrop.jpg",
            "video_url": "https://example.com/video.mp4",
            "release_year": 2024,
            "rating": 7.5,
            "duration_minutes": 120,
            "tags": ["test"],
            "languages": ["en"]
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        success, response, error = self.make_request("POST", "/movies", movie_data, headers)
        
        if not success:
            self.log_result("Regular User Create Movie - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 403:
            self.log_result("Regular User Movie Restrictions", True, "Correctly blocked regular user from creating movies")
            return True
        else:
            self.log_result("Regular User Movie Restrictions", False, f"Expected 403, got {response.status_code}")
        
        return False
    
    def test_translations(self):
        """Test translations endpoint"""
        print("\n🌍 Testing Translations...")
        
        # Test English translations
        success, response, error = self.make_request("GET", "/translations", params={"lang": "en"})
        
        if not success:
            self.log_result("Translations (EN) - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "home" in data and data["home"] == "Home":
                self.log_result("Translations (EN)", True, "English translations working")
            else:
                self.log_result("Translations (EN)", False, f"Unexpected EN data: {data}")
        else:
            self.log_result("Translations (EN)", False, f"Status code: {response.status_code}")
        
        # Test Spanish translations
        success, response, error = self.make_request("GET", "/translations", params={"lang": "es"})
        
        if success and response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "home" in data and data["home"] == "Inicio":
                self.log_result("Translations (ES)", True, "Spanish translations working")
            else:
                self.log_result("Translations (ES)", False, f"Unexpected ES data: {data}")
        else:
            self.log_result("Translations (ES)", False, "Spanish translations failed")
        
        # Test French translations
        success, response, error = self.make_request("GET", "/translations", params={"lang": "fr"})
        
        if success and response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "home" in data and data["home"] == "Accueil":
                self.log_result("Translations (FR)", True, "French translations working")
            else:
                self.log_result("Translations (FR)", False, f"Unexpected FR data: {data}")
        else:
            self.log_result("Translations (FR)", False, "French translations failed")
        
        return True
    
    def test_view_progress(self):
        """Test view progress tracking"""
        print("\n📺 Testing View Progress...")
        
        if not self.user_token or not self.test_profile_id or not self.test_movie_id:
            self.log_result("View Progress", False, "Missing required tokens/IDs")
            return False
        
        # Test updating view progress
        progress_data = {
            "progress_seconds": 300,
            "completed": False
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        params = {"profile_id": self.test_profile_id}
        
        success, response, error = self.make_request("PUT", f"/views/{self.test_movie_id}", progress_data, headers, params)
        
        if not success:
            self.log_result("Update View Progress - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            self.log_result("Update View Progress", True, "Progress updated successfully")
            
            # Test getting continue watching
            success, response, error = self.make_request("GET", "/views/continue", params=params, headers=headers)
            
            if success and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Continue Watching", True, f"Found {len(data)} items in continue watching")
                else:
                    self.log_result("Get Continue Watching", False, "Response is not a list")
            else:
                self.log_result("Get Continue Watching", False, f"Failed to get continue watching: {response.status_code if response else error}")
            
            return True
        else:
            self.log_result("Update View Progress", False, f"Status code: {response.status_code}")
        
        return False
    
    def test_enhanced_continue_watching(self):
        """Test enhanced continue watching functionality with different progress values"""
        print("\n📺 Testing Enhanced Continue Watching...")
        
        if not self.user_token or not self.test_profile_id or not self.test_movie_id:
            self.log_result("Enhanced Continue Watching", False, "Missing required tokens/IDs")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        params = {"profile_id": self.test_profile_id}
        
        # Test with progress < 30 seconds (should not appear in continue watching)
        progress_data_low = {
            "progress_seconds": 15,
            "completed": False
        }
        
        success, response, error = self.make_request("PUT", f"/views/{self.test_movie_id}", progress_data_low, headers, params)
        
        if not success:
            self.log_result("Enhanced Continue Watching (Low Progress) - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            # Check continue watching - should be empty or not include this movie
            success, response, error = self.make_request("GET", "/views/continue", params=params, headers=headers)
            
            if success and response.status_code == 200:
                data = response.json()
                low_progress_found = any(item.get("movie", {}).get("id") == self.test_movie_id for item in data)
                if not low_progress_found:
                    self.log_result("Enhanced Continue Watching (Low Progress Filter)", True, "Movies with <30s progress correctly excluded")
                else:
                    self.log_result("Enhanced Continue Watching (Low Progress Filter)", False, "Movie with <30s progress incorrectly included")
            else:
                self.log_result("Enhanced Continue Watching (Low Progress Filter)", False, "Failed to get continue watching")
        
        # Test with progress > 30 seconds (should appear in continue watching)
        progress_data_high = {
            "progress_seconds": 450,
            "completed": False
        }
        
        success, response, error = self.make_request("PUT", f"/views/{self.test_movie_id}", progress_data_high, headers, params)
        
        if success and response.status_code == 200:
            # Check continue watching - should include this movie
            success, response, error = self.make_request("GET", "/views/continue", params=params, headers=headers)
            
            if success and response.status_code == 200:
                data = response.json()
                high_progress_found = any(item.get("movie", {}).get("id") == self.test_movie_id for item in data)
                if high_progress_found:
                    self.log_result("Enhanced Continue Watching (High Progress)", True, "Movies with >30s progress correctly included")
                    # Verify progress value
                    for item in data:
                        if item.get("movie", {}).get("id") == self.test_movie_id:
                            if item.get("progress", {}).get("progress_seconds") == 450:
                                self.log_result("Enhanced Continue Watching (Progress Value)", True, "Progress value correctly stored and retrieved")
                            else:
                                self.log_result("Enhanced Continue Watching (Progress Value)", False, f"Progress mismatch: expected 450, got {item.get('progress', {}).get('progress_seconds')}")
                            break
                else:
                    self.log_result("Enhanced Continue Watching (High Progress)", False, "Movie with >30s progress not found in continue watching")
            else:
                self.log_result("Enhanced Continue Watching (High Progress)", False, "Failed to get continue watching")
        
        return True
    
    def test_watchlist_management(self):
        """Test comprehensive watchlist management functionality"""
        print("\n📝 Testing Watchlist Management...")
        
        if not self.user_token or not self.test_profile_id or not self.test_movie_id:
            self.log_result("Watchlist Management", False, "Missing required tokens/IDs")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test 1: Get empty watchlist initially
        success, response, error = self.make_request("GET", f"/profiles/{self.test_profile_id}/watchlist", headers=headers)
        
        if not success:
            self.log_result("Get Empty Watchlist - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                self.log_result("Get Empty Watchlist", True, "Watchlist initially empty as expected")
            else:
                self.log_result("Get Empty Watchlist", False, f"Expected empty list, got: {data}")
        else:
            self.log_result("Get Empty Watchlist", False, f"Status code: {response.status_code}")
        
        # Test 2: Add movie to watchlist
        success, response, error = self.make_request("POST", f"/profiles/{self.test_profile_id}/watchlist/{self.test_movie_id}", headers=headers)
        
        if not success:
            self.log_result("Add to Watchlist - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and ("Added" in data["message"] or "Already" in data["message"]):
                self.log_result("Add to Watchlist", True, f"Movie added to watchlist: {data['message']}")
            else:
                self.log_result("Add to Watchlist", False, f"Unexpected response: {data}")
        else:
            self.log_result("Add to Watchlist", False, f"Status code: {response.status_code}")
        
        # Test 3: Check if movie is in watchlist
        success, response, error = self.make_request("GET", f"/profiles/{self.test_profile_id}/watchlist/check/{self.test_movie_id}", headers=headers)
        
        if not success:
            self.log_result("Check Watchlist Status - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "in_watchlist" in data and data["in_watchlist"] is True:
                self.log_result("Check Watchlist Status", True, "Movie correctly found in watchlist")
            else:
                self.log_result("Check Watchlist Status", False, f"Movie not found in watchlist: {data}")
        else:
            self.log_result("Check Watchlist Status", False, f"Status code: {response.status_code}")
        
        # Test 4: Get watchlist with movie
        success, response, error = self.make_request("GET", f"/profiles/{self.test_profile_id}/watchlist", headers=headers)
        
        if success and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 1:
                movie_in_list = data[0]
                if movie_in_list.get("id") == self.test_movie_id:
                    self.log_result("Get Watchlist with Movie", True, f"Watchlist contains movie: {movie_in_list.get('title', 'Unknown')}")
                else:
                    self.log_result("Get Watchlist with Movie", False, f"Wrong movie in watchlist: {movie_in_list}")
            else:
                self.log_result("Get Watchlist with Movie", False, f"Expected 1 movie in watchlist, got: {len(data) if isinstance(data, list) else 'not a list'}")
        else:
            self.log_result("Get Watchlist with Movie", False, "Failed to get watchlist")
        
        # Test 5: Try to add same movie again (should handle gracefully)
        success, response, error = self.make_request("POST", f"/profiles/{self.test_profile_id}/watchlist/{self.test_movie_id}", headers=headers)
        
        if success and response.status_code == 200:
            data = response.json()
            if "Already" in data.get("message", ""):
                self.log_result("Add Duplicate to Watchlist", True, "Duplicate addition handled correctly")
            else:
                self.log_result("Add Duplicate to Watchlist", False, f"Unexpected response for duplicate: {data}")
        else:
            self.log_result("Add Duplicate to Watchlist", False, "Failed to handle duplicate addition")
        
        # Test 6: Remove movie from watchlist
        success, response, error = self.make_request("DELETE", f"/profiles/{self.test_profile_id}/watchlist/{self.test_movie_id}", headers=headers)
        
        if not success:
            self.log_result("Remove from Watchlist - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "Removed" in data["message"]:
                self.log_result("Remove from Watchlist", True, "Movie removed from watchlist")
            else:
                self.log_result("Remove from Watchlist", False, f"Unexpected response: {data}")
        else:
            self.log_result("Remove from Watchlist", False, f"Status code: {response.status_code}")
        
        # Test 7: Verify watchlist is empty after removal
        success, response, error = self.make_request("GET", f"/profiles/{self.test_profile_id}/watchlist", headers=headers)
        
        if success and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                self.log_result("Verify Empty Watchlist After Removal", True, "Watchlist correctly empty after removal")
            else:
                self.log_result("Verify Empty Watchlist After Removal", False, f"Watchlist not empty: {data}")
        else:
            self.log_result("Verify Empty Watchlist After Removal", False, "Failed to verify empty watchlist")
        
        # Test 8: Check watchlist status after removal
        success, response, error = self.make_request("GET", f"/profiles/{self.test_profile_id}/watchlist/check/{self.test_movie_id}", headers=headers)
        
        if success and response.status_code == 200:
            data = response.json()
            if "in_watchlist" in data and data["in_watchlist"] is False:
                self.log_result("Check Watchlist Status After Removal", True, "Movie correctly not in watchlist after removal")
            else:
                self.log_result("Check Watchlist Status After Removal", False, f"Movie still shows in watchlist: {data}")
        else:
            self.log_result("Check Watchlist Status After Removal", False, "Failed to check watchlist status")
        
        return True
    
    def test_profile_creation_with_avatars(self):
        """Test profile creation with different avatar values"""
        print("\n👤 Testing Profile Creation with Different Avatars...")
        
        if not self.user_token:
            self.log_result("Profile Avatar Creation", False, "No user token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        avatar_colors = ["red", "blue", "green", "yellow", "purple"]
        
        created_profiles = []
        
        for color in avatar_colors:
            profile_data = {
                "name": f"Test Profile {color.title()}",
                "avatar": color,
                "language": "en",
                "maturity_rating": "PG-13"
            }
            
            success, response, error = self.make_request("POST", "/profiles", profile_data, headers)
            
            if not success:
                self.log_result(f"Create Profile with {color} Avatar - Connection", False, f"Connection failed: {error}")
                continue
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("avatar") == color and "watchlist" in data:
                    self.log_result(f"Create Profile with {color} Avatar", True, f"Profile created with {color} avatar and watchlist field")
                    created_profiles.append(data["id"])
                else:
                    self.log_result(f"Create Profile with {color} Avatar", False, f"Profile missing expected fields: {data}")
            else:
                self.log_result(f"Create Profile with {color} Avatar", False, f"Status code: {response.status_code}")
        
        # Clean up created profiles
        for profile_id in created_profiles:
            self.make_request("DELETE", f"/profiles/{profile_id}", headers=headers)
        
        return len(created_profiles) > 0
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        print("\n🌐 Testing CORS Headers...")
        
        success, response, error = self.make_request("GET", "/health")
        
        if not success:
            self.log_result("CORS Headers - Connection", False, f"Connection failed: {error}")
            return False
        
        if response.status_code == 200:
            headers = response.headers
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            ]
            
            found_cors = any(header in headers for header in cors_headers)
            
            if found_cors:
                self.log_result("CORS Headers", True, "CORS headers present")
                return True
            else:
                self.log_result("CORS Headers", False, f"No CORS headers found in: {list(headers.keys())}")
        else:
            self.log_result("CORS Headers", False, f"Status code: {response.status_code}")
        
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting StreamFlix Backend API Tests...")
        print(f"🎯 Testing against: {BASE_URL}")
        
        # Core functionality tests
        self.test_health_check()
        
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        self.test_admin_login()
        self.test_protected_endpoint_without_token()
        self.test_protected_endpoint_with_token()
        
        # Profile management tests
        self.test_create_profile()
        self.test_list_profiles()
        self.test_update_profile()
        self.test_profile_creation_with_avatars()
        
        # Movie API tests
        self.test_get_movies()
        self.test_get_movie_by_id()
        self.test_movies_with_filters()
        self.test_admin_movie_operations()
        self.test_regular_user_movie_operations()
        
        # Enhanced functionality tests
        self.test_view_progress()
        self.test_enhanced_continue_watching()
        self.test_watchlist_management()
        self.test_translations()
        self.test_cors_headers()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print("\n🎉 Testing completed!")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = StreamFlixTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)