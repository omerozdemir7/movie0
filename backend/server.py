from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI(title="StreamFlix API", description="Netflix-like streaming platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class MaturityRating(str, Enum):
    G = "G"
    PG = "PG" 
    PG13 = "PG-13"
    R = "R"
    NC17 = "NC-17"

class MovieCategory(str, Enum):
    ACTION = "action"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    SCI_FI = "sci-fi"
    ROMANCE = "romance"
    THRILLER = "thriller"
    DOCUMENTARY = "documentary"
    ANIMATION = "animation"
    FAMILY = "family"

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER
    profiles: List[str] = Field(default_factory=list)  # Profile IDs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    avatar: str = "default"
    language: str = "en"
    maturity_rating: MaturityRating = MaturityRating.PG13
    watch_history: List[str] = Field(default_factory=list)  # Movie IDs
    watchlist: List[str] = Field(default_factory=list)  # Movie IDs in "My List"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProfileCreate(BaseModel):
    name: str
    avatar: str = "default"
    language: str = "en"
    maturity_rating: MaturityRating = MaturityRating.PG13

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = None
    maturity_rating: Optional[MaturityRating] = None
    watchlist: Optional[List[str]] = None

class Movie(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    title: str
    description: str
    category: MovieCategory
    poster_url: str
    backdrop_url: str
    video_url: str
    release_year: int
    rating: float = Field(ge=0, le=10)
    duration_minutes: int
    tags: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    i18n: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MovieCreate(BaseModel):
    slug: str
    title: str
    description: str
    category: MovieCategory
    poster_url: str
    backdrop_url: str
    video_url: str
    release_year: int
    rating: float = Field(ge=0, le=10)
    duration_minutes: int
    tags: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    i18n: Dict[str, Dict[str, str]] = Field(default_factory=dict)

class MovieUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MovieCategory] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    video_url: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=10)
    duration_minutes: Optional[int] = None
    tags: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    i18n: Optional[Dict[str, Dict[str, str]]] = None

class ViewProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    movie_id: str
    progress_seconds: int
    completed: bool = False
    last_watched: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ViewProgressUpdate(BaseModel):
    progress_seconds: int
    completed: bool = False

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Authentication Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    await db.users.insert_one(user.dict())
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Profile Routes
@api_router.get("/profiles", response_model=List[Profile])
async def get_profiles(current_user: User = Depends(get_current_user)):
    profiles = await db.profiles.find({"user_id": current_user.id}).to_list(length=None)
    return [Profile(**profile) for profile in profiles]

@api_router.post("/profiles", response_model=Profile)
async def create_profile(profile_data: ProfileCreate, current_user: User = Depends(get_current_user)):
    profile = Profile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    
    await db.profiles.insert_one(profile.dict())
    
    # Add profile ID to user's profiles list
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"profiles": profile.id}}
    )
    
    return profile

@api_router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(profile_id: str, profile_data: ProfileUpdate, current_user: User = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    if update_data:
        await db.profiles.update_one({"id": profile_id}, {"$set": update_data})
    
    updated_profile = await db.profiles.find_one({"id": profile_id})
    return Profile(**updated_profile)

@api_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str, current_user: User = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    await db.profiles.delete_one({"id": profile_id})
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"profiles": profile_id}}
    )
    
    return {"message": "Profile deleted successfully"}

# Movie Routes
@api_router.get("/movies", response_model=List[Movie])
async def get_movies(
    category: Optional[MovieCategory] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 50
):
    query = {}
    
    if category:
        query["category"] = category
    if year:
        query["release_year"] = year
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    movies = await db.movies.find(query).limit(limit).to_list(length=None)
    return [Movie(**movie) for movie in movies]

@api_router.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: str):
    movie = await db.movies.find_one({"$or": [{"id": movie_id}, {"slug": movie_id}]})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return Movie(**movie)

@api_router.post("/movies", response_model=Movie)
async def create_movie(movie_data: MovieCreate, admin_user: User = Depends(get_admin_user)):
    # Check for duplicate slug
    existing_movie = await db.movies.find_one({"slug": movie_data.slug})
    if existing_movie:
        raise HTTPException(status_code=400, detail="Movie with this slug already exists")
    
    movie = Movie(**movie_data.dict())
    await db.movies.insert_one(movie.dict())
    
    return movie

@api_router.put("/movies/{movie_id}", response_model=Movie)
async def update_movie(movie_id: str, movie_data: MovieUpdate, admin_user: User = Depends(get_admin_user)):
    movie = await db.movies.find_one({"id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    update_data = {k: v for k, v in movie_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    if update_data:
        await db.movies.update_one({"id": movie_id}, {"$set": update_data})
    
    updated_movie = await db.movies.find_one({"id": movie_id})
    return Movie(**updated_movie)

@api_router.delete("/movies/{movie_id}")
async def delete_movie(movie_id: str, admin_user: User = Depends(get_admin_user)):
    movie = await db.movies.find_one({"id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    await db.movies.delete_one({"id": movie_id})
    
    return {"message": "Movie deleted successfully"}

# View Progress Routes
@api_router.get("/views/continue")
async def get_continue_watching(profile_id: str, current_user: User = Depends(get_current_user)):
    # Verify profile belongs to user
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    progress_list = await db.view_progress.find({
        "profile_id": profile_id,
        "completed": False,
        "progress_seconds": {"$gt": 30}  # Only show if watched for more than 30 seconds
    }).sort("last_watched", -1).to_list(length=10)
    
    result = []
    for progress in progress_list:
        movie = await db.movies.find_one({"id": progress["movie_id"]})
        if movie:
            result.append({
                "movie": Movie(**movie),
                "progress": ViewProgress(**progress)
            })
    
    return result

@api_router.put("/views/{movie_id}")
async def update_view_progress(
    movie_id: str, 
    profile_id: str, 
    progress_data: ViewProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    # Verify profile belongs to user
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify movie exists
    movie = await db.movies.find_one({"id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Update or create progress
    progress = await db.view_progress.find_one({
        "profile_id": profile_id,
        "movie_id": movie_id
    })
    
    if progress:
        await db.view_progress.update_one(
            {"id": progress["id"]},
            {
                "$set": {
                    "progress_seconds": progress_data.progress_seconds,
                    "completed": progress_data.completed,
                    "last_watched": datetime.now(timezone.utc)
                }
            }
        )
    else:
        new_progress = ViewProgress(
            profile_id=profile_id,
            movie_id=movie_id,
            progress_seconds=progress_data.progress_seconds,
            completed=progress_data.completed
        )
        await db.view_progress.insert_one(new_progress.dict())
    
    # Add to watch history if not already there
    if movie_id not in profile.get("watch_history", []):
        await db.profiles.update_one(
            {"id": profile_id},
            {"$push": {"watch_history": movie_id}}
        )
    
    return {"message": "Progress updated successfully"}

# Watchlist Routes
@api_router.get("/profiles/{profile_id}/watchlist", response_model=List[Movie])
async def get_watchlist(profile_id: str, current_user: User = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    watchlist_ids = profile.get("watchlist", [])
    if not watchlist_ids:
        return []
    
    movies = await db.movies.find({"id": {"$in": watchlist_ids}}).to_list(length=None)
    return [Movie(**movie) for movie in movies]

@api_router.post("/profiles/{profile_id}/watchlist/{movie_id}")
async def add_to_watchlist(profile_id: str, movie_id: str, current_user: User = Depends(get_current_user)):
    # Verify profile belongs to user
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify movie exists
    movie = await db.movies.find_one({"id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Add to watchlist if not already there
    watchlist = profile.get("watchlist", [])
    if movie_id not in watchlist:
        await db.profiles.update_one(
            {"id": profile_id},
            {"$push": {"watchlist": movie_id}}
        )
        return {"message": "Added to watchlist"}
    else:
        return {"message": "Already in watchlist"}

@api_router.delete("/profiles/{profile_id}/watchlist/{movie_id}")
async def remove_from_watchlist(profile_id: str, movie_id: str, current_user: User = Depends(get_current_user)):
    # Verify profile belongs to user
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Remove from watchlist
    await db.profiles.update_one(
        {"id": profile_id},
        {"$pull": {"watchlist": movie_id}}
    )
    
    return {"message": "Removed from watchlist"}

@api_router.get("/profiles/{profile_id}/watchlist/check/{movie_id}")
async def check_watchlist_status(profile_id: str, movie_id: str, current_user: User = Depends(get_current_user)):
    profile = await db.profiles.find_one({"id": profile_id, "user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    watchlist = profile.get("watchlist", [])
    return {"in_watchlist": movie_id in watchlist}

# Translations Route
@api_router.get("/translations")
async def get_translations(lang: str = "en"):
    translations = {
        "en": {
            "home": "Home",
            "movies": "Movies",
            "series": "TV Series",
            "my_list": "My List",
            "search": "Search",
            "play": "Play",
            "more_info": "More Info",
            "continue_watching": "Continue Watching",
            "popular": "Popular",
            "trending": "Trending Now",
            "new_releases": "New Releases",
            "action": "Action",
            "comedy": "Comedy",
            "drama": "Drama",
            "horror": "Horror",
            "sci_fi": "Sci-Fi",
            "romance": "Romance",
            "thriller": "Thriller",
            "documentary": "Documentary",
            "animation": "Animation",
            "family": "Family"
        },
        "es": {
            "home": "Inicio",
            "movies": "Películas",
            "series": "Series de TV",
            "my_list": "Mi Lista",
            "search": "Buscar",
            "play": "Reproducir",
            "more_info": "Más Información",
            "continue_watching": "Continuar Viendo",
            "popular": "Popular",
            "trending": "Tendencias",
            "new_releases": "Nuevos Lanzamientos",
            "action": "Acción",
            "comedy": "Comedia",
            "drama": "Drama",
            "horror": "Terror",
            "sci_fi": "Ciencia Ficción",
            "romance": "Romance",
            "thriller": "Suspenso",
            "documentary": "Documental",
            "animation": "Animación",
            "family": "Familia"
        },
        "fr": {
            "home": "Accueil",
            "movies": "Films",
            "series": "Séries TV",
            "my_list": "Ma Liste",
            "search": "Rechercher",
            "play": "Lire",
            "more_info": "Plus d'Infos",
            "continue_watching": "Continuer à Regarder",
            "popular": "Populaire",
            "trending": "Tendances",
            "new_releases": "Nouvelles Sorties",
            "action": "Action",
            "comedy": "Comédie",
            "drama": "Drame",
            "horror": "Horreur",
            "sci_fi": "Science-Fiction",
            "romance": "Romance",
            "thriller": "Thriller",
            "documentary": "Documentaire",
            "animation": "Animation",
            "family": "Famille"
        }
    }
    
    return translations.get(lang, translations["en"])

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()