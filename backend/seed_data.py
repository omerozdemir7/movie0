#!/usr/bin/env python3
"""
Seed script to populate the StreamFlix database with sample data
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
import uuid
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_data():
    print("🌱 Starting to seed StreamFlix database...")
    
    # Clear existing data
    await db.users.delete_many({})
    await db.profiles.delete_many({})
    await db.movies.delete_many({})
    await db.view_progress.delete_many({})
    print("🧹 Cleared existing data")
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_user = {
        "id": admin_id,
        "email": "admin@streamflix.com",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "profiles": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(admin_user)
    print("👑 Created admin user: admin@streamflix.com / admin123")
    
    # Create demo user
    demo_user_id = str(uuid.uuid4())
    demo_user = {
        "id": demo_user_id,
        "email": "demo@streamflix.com",
        "password_hash": hash_password("demo123"),
        "role": "user",
        "profiles": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(demo_user)
    print("👤 Created demo user: demo@streamflix.com / demo123")
    
    # Create demo profiles
    profile1_id = str(uuid.uuid4())
    profile2_id = str(uuid.uuid4())
    
    profiles = [
        {
            "id": profile1_id,
            "user_id": demo_user_id,
            "name": "John",
            "avatar": "default",
            "language": "en",
            "maturity_rating": "PG-13",
            "watch_history": [],
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": profile2_id,
            "user_id": demo_user_id,
            "name": "Sarah",
            "avatar": "default",
            "language": "en",
            "maturity_rating": "R",
            "watch_history": [],
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.profiles.insert_many(profiles)
    
    # Update demo user with profile IDs
    await db.users.update_one(
        {"id": demo_user_id},
        {"$set": {"profiles": [profile1_id, profile2_id]}}
    )
    print("👥 Created demo profiles: John, Sarah")
    
    # Sample movie data with real URLs for testing
    movies = [
        {
            "id": str(uuid.uuid4()),
            "slug": "big-buck-bunny",
            "title": "Big Buck Bunny",
            "description": "A large and lovable rabbit deals with three tiny bullies in this computer-animated short film. This open-source movie showcases stunning animation and a heartwarming story.",
            "category": "animation",
            "poster_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Big_buck_bunny_poster_big.jpg/280px-Big_buck_bunny_poster_big.jpg",
            "backdrop_url": "https://peach.blender.org/wp-content/uploads/bbb-splash.png",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "release_year": 2008,
            "rating": 7.8,
            "duration_minutes": 10,
            "tags": ["animation", "short", "family", "comedy"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "elephant-dream",
            "title": "Elephant's Dream",
            "description": "Two strange characters explore a capricious and seemingly infinite machine. The elder, Proog, acts as a tour-guide and protector, happily showing off the sights and dangers of the machine to his initially curious but increasingly skeptical protege Emo.",
            "category": "sci-fi",
            "poster_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Elephants_dream_poster.png/280px-Elephants_dream_poster.png",
            "backdrop_url": "https://orange.blender.org/wp-content/uploads/2006/05/elephant_dreams_01.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "release_year": 2006,
            "rating": 7.2,
            "duration_minutes": 11,
            "tags": ["sci-fi", "short", "surreal", "blender"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "sintel",
            "title": "Sintel",
            "description": "A lonely young woman, Sintel, helps and befriends a dragon, whom she calls Scales. But when he is kidnapped by an adult dragon, Sintel decides to embark on a dangerous quest to find her lost friend Scales.",
            "category": "drama",
            "poster_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Sintel_poster.jpg/280px-Sintel_poster.jpg",
            "backdrop_url": "https://durian.blender.org/wp-content/uploads/2010/06/sintel_04.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "release_year": 2010,
            "rating": 8.1,
            "duration_minutes": 15,
            "tags": ["drama", "fantasy", "adventure", "short"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "tears-of-steel",
            "title": "Tears of Steel",
            "description": "In an apocalyptic future, a group of soldiers and scientists takes refuge in Amsterdam to try to stop an army of robots that threatens humanity in this live-action short film.",
            "category": "action",
            "poster_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Tears_of_Steel_poster.jpg/280px-Tears_of_Steel_poster.jpg",
            "backdrop_url": "https://mango.blender.org/wp-content/uploads/2012/09/tears_of_steel_03.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "release_year": 2012,
            "rating": 7.9,
            "duration_minutes": 12,
            "tags": ["action", "sci-fi", "short", "live-action"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "for-bigger-blazes",
            "title": "For Bigger Blazes",
            "description": "An action-packed adventure showcasing incredible visual effects and non-stop thrills. Experience the ultimate high-octane entertainment.",
            "category": "action",
            "poster_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg",
            "backdrop_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "release_year": 2019,
            "rating": 8.3,
            "duration_minutes": 15,
            "tags": ["action", "adventure", "thriller"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "for-bigger-escape",
            "title": "For Bigger Escape",
            "description": "An epic thriller about escape and survival against all odds. A heart-pounding journey that will keep you on the edge of your seat.",
            "category": "thriller",
            "poster_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerEscapes.jpg",
            "backdrop_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerEscapes.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "release_year": 2019,
            "rating": 7.8,
            "duration_minutes": 15,
            "tags": ["thriller", "action", "escape"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "for-bigger-fun",
            "title": "For Bigger Fun",
            "description": "A delightful comedy that brings laughter and joy to audiences of all ages. Perfect for family movie nights and feel-good entertainment.",
            "category": "comedy",
            "poster_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerFun.jpg",
            "backdrop_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerFun.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "release_year": 2019,
            "rating": 8.0,
            "duration_minutes": 15,
            "tags": ["comedy", "family", "entertainment"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "for-bigger-joyrides",
            "title": "For Bigger Joyrides",
            "description": "An exhilarating adventure filled with spectacular car chases and breathtaking stunts. Buckle up for the ride of a lifetime.",
            "category": "action",
            "poster_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerJoyrides.jpg",
            "backdrop_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerJoyrides.jpg",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "release_year": 2019,
            "rating": 8.2,
            "duration_minutes": 15,
            "tags": ["action", "cars", "adventure", "stunts"],
            "languages": ["en"],
            "i18n": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.movies.insert_many(movies)
    print(f"🎬 Created {len(movies)} sample movies")
    
    print("✅ Database seeding completed successfully!")
    print("\n📋 Login Credentials:")
    print("Admin: admin@streamflix.com / admin123")
    print("Demo User: demo@streamflix.com / demo123")
    print("\n🎯 Available Movies:")
    for movie in movies:
        print(f"  - {movie['title']} ({movie['category']})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())