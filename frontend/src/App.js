import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [currentProfile, setCurrentProfile] = useState(null);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const userResponse = await axios.get(`${API}/auth/me`);
      setUser(userResponse.data);
      
      const profilesResponse = await axios.get(`${API}/profiles`);
      setProfiles(profilesResponse.data);
      
      if (profilesResponse.data.length > 0) {
        setCurrentProfile(profilesResponse.data[0]);
      }
    } catch (error) {
      console.error('Error loading user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await loadUser();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/register`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await loadUser();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setProfiles([]);
    setCurrentProfile(null);
  };

  const switchProfile = (profile) => {
    setCurrentProfile(profile);
  };

  return (
    <AuthContext.Provider value={{
      user,
      currentProfile,
      profiles,
      loading,
      login,
      register,
      logout,
      switchProfile,
      loadUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Components
const LoginForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = isLogin 
      ? await login(email, password)
      : await register(email, password);

    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="bg-black bg-opacity-75 p-16 rounded-lg w-full max-w-md">
        <h1 className="text-3xl font-bold text-white mb-8">
          {isLogin ? 'Sign In' : 'Sign Up'}
        </h1>
        
        {error && (
          <div className="bg-red-600 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full p-4 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-red-500"
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full p-4 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-red-500"
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 text-white py-4 rounded font-semibold hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <p className="text-gray-400 mt-4">
          {isLogin ? "New to StreamFlix? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-white hover:underline"
          >
            {isLogin ? 'Sign up now' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
};

// Profile Avatar Options
const AVATAR_OPTIONS = [
  { id: 'red', name: 'Red', gradient: 'from-red-500 to-red-700' },
  { id: 'blue', name: 'Blue', gradient: 'from-blue-500 to-blue-700' },
  { id: 'green', name: 'Green', gradient: 'from-green-500 to-green-700' },
  { id: 'purple', name: 'Purple', gradient: 'from-purple-500 to-purple-700' },
  { id: 'pink', name: 'Pink', gradient: 'from-pink-500 to-pink-700' },
  { id: 'yellow', name: 'Yellow', gradient: 'from-yellow-500 to-yellow-700' },
  { id: 'indigo', name: 'Indigo', gradient: 'from-indigo-500 to-indigo-700' },
  { id: 'teal', name: 'Teal', gradient: 'from-teal-500 to-teal-700' }
];

const getAvatarGradient = (avatar) => {
  const avatarOption = AVATAR_OPTIONS.find(opt => opt.id === avatar);
  return avatarOption ? avatarOption.gradient : 'from-red-500 to-blue-600';
};

const ProfileSelector = () => {
  const { profiles, switchProfile, currentProfile } = useAuth();
  const [showManage, setShowManage] = useState(false);

  if (showManage) {
    return <ProfileManager onClose={() => setShowManage(false)} />;
  }

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-4">
      <h1 className="text-5xl font-semibold text-white mb-12">Who's watching?</h1>
      
      <div className="flex flex-wrap justify-center gap-8 mb-8">
        {profiles.map((profile) => (
          <div
            key={profile.id}
            onClick={() => switchProfile(profile)}
            className="flex flex-col items-center cursor-pointer group"
          >
            <div className={`w-32 h-32 bg-gradient-to-br ${getAvatarGradient(profile.avatar)} rounded-lg flex items-center justify-center mb-4 group-hover:border-4 group-hover:border-white transition-all`}>
              <span className="text-3xl font-bold text-white">
                {profile.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="text-xl text-gray-300 group-hover:text-white">
              {profile.name}
            </span>
          </div>
        ))}
        
        <div
          onClick={() => setShowManage(true)}
          className="flex flex-col items-center cursor-pointer group"
        >
          <div className="w-32 h-32 bg-gray-600 rounded-lg flex items-center justify-center mb-4 group-hover:bg-gray-500 transition-all">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <span className="text-xl text-gray-300 group-hover:text-white">
            Manage Profiles
          </span>
        </div>
      </div>
    </div>
  );
};

const ProfileManager = ({ onClose }) => {
  const { profiles, loadUser } = useAuth();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState('red');
  const [loading, setLoading] = useState(false);

  const createProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/profiles`, {
        name: newProfileName,
        avatar: selectedAvatar
      });
      
      await loadUser();
      setNewProfileName('');
      setSelectedAvatar('red');
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteProfile = async (profileId) => {
    if (profiles.length <= 1) {
      alert('You must have at least one profile');
      return;
    }
    
    if (window.confirm('Are you sure you want to delete this profile?')) {
      try {
        await axios.delete(`${API}/profiles/${profileId}`);
        await loadUser();
      } catch (error) {
        console.error('Error deleting profile:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center px-4">
      <h1 className="text-5xl font-semibold text-white mb-12">Manage Profiles</h1>
      
      <div className="flex flex-wrap justify-center gap-8 mb-8">
        {profiles.map((profile) => (
          <div key={profile.id} className="flex flex-col items-center group">
            <div className="relative">
              <div className={`w-32 h-32 bg-gradient-to-br ${getAvatarGradient(profile.avatar)} rounded-lg flex items-center justify-center mb-4`}>
                <span className="text-3xl font-bold text-white">
                  {profile.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <button
                onClick={() => deleteProfile(profile.id)}
                className="absolute -top-2 -right-2 w-8 h-8 bg-red-600 rounded-full flex items-center justify-center text-white hover:bg-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                ✕
              </button>
            </div>
            <span className="text-xl text-gray-300">{profile.name}</span>
          </div>
        ))}
        
        {!showCreateForm && profiles.length < 5 && (
          <div
            onClick={() => setShowCreateForm(true)}
            className="flex flex-col items-center cursor-pointer group"
          >
            <div className="w-32 h-32 bg-gray-600 rounded-lg flex items-center justify-center mb-4 group-hover:bg-gray-500 transition-all">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <span className="text-xl text-gray-300 group-hover:text-white">Add Profile</span>
          </div>
        )}
      </div>

      {showCreateForm && (
        <div className="mb-8 p-6 bg-gray-800 rounded-lg">
          <h2 className="text-2xl text-white mb-4">Create New Profile</h2>
          <form onSubmit={createProfile} className="space-y-4">
            <input
              type="text"
              placeholder="Profile name"
              value={newProfileName}
              onChange={(e) => setNewProfileName(e.target.value)}
              required
              maxLength={20}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-red-500"
            />
            
            <div>
              <label className="block text-white mb-2">Choose Avatar Color:</label>
              <div className="flex flex-wrap gap-2">
                {AVATAR_OPTIONS.map((avatar) => (
                  <button
                    key={avatar.id}
                    type="button"
                    onClick={() => setSelectedAvatar(avatar.id)}
                    className={`w-12 h-12 bg-gradient-to-br ${avatar.gradient} rounded-full border-2 ${
                      selectedAvatar === avatar.id ? 'border-white' : 'border-transparent'
                    } hover:border-gray-300 transition-colors`}
                  />
                ))}
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setNewProfileName('');
                  setSelectedAvatar('red');
                }}
                className="px-6 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <button
        onClick={onClose}
        className="px-8 py-3 bg-white text-black font-semibold rounded hover:bg-gray-200 transition-colors"
      >
        Done
      </button>
    </div>
  );
};

const Navbar = () => {
  const { user, currentProfile, logout, switchProfile, profiles } = useAuth();
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  return (
    <nav className="fixed top-0 w-full z-50 bg-gradient-to-b from-black to-transparent px-4 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-8">
          <Link to="/" className="text-red-600 text-2xl font-bold">
            StreamFlix
          </Link>
          
          <div className="hidden md:flex space-x-6">
            <Link to="/" className="text-white hover:text-gray-300 transition-colors">
              Home
            </Link>
            <Link to="/movies" className="text-white hover:text-gray-300 transition-colors">
              Movies
            </Link>
            <Link to="/my-list" className="text-white hover:text-gray-300 transition-colors">
              My List
            </Link>
            <Link to="/search" className="text-white hover:text-gray-300 transition-colors">
              Search
            </Link>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {currentProfile && (
            <div className="relative">
              <button
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                className="flex items-center space-x-2 text-white hover:text-gray-300"
              >
                <div className={`w-8 h-8 bg-gradient-to-br ${getAvatarGradient(currentProfile.avatar)} rounded flex items-center justify-center`}>
                  <span className="text-sm font-bold">
                    {currentProfile.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="hidden md:block">{currentProfile.name}</span>
              </button>

              {showProfileDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-black bg-opacity-90 rounded-lg py-2">
                  {profiles.map((profile) => (
                    <button
                      key={profile.id}
                      onClick={() => {
                        switchProfile(profile);
                        setShowProfileDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 text-white hover:bg-gray-800 flex items-center space-x-2"
                    >
                      <div className={`w-6 h-6 bg-gradient-to-br ${getAvatarGradient(profile.avatar)} rounded flex items-center justify-center`}>
                        <span className="text-xs font-bold">
                          {profile.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span>{profile.name}</span>
                    </button>
                  ))}
                  <hr className="border-gray-600 my-2" />
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-white hover:bg-gray-800"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

const MovieCard = ({ movie, onClick }) => (
  <div
    onClick={onClick}
    className="min-w-[200px] cursor-pointer transition-transform hover:scale-105"
  >
    <img
      src={movie.poster_url}
      alt={movie.title}
      className="w-full h-[300px] object-cover rounded-lg"
      onError={(e) => {
        e.target.src = 'https://via.placeholder.com/200x300/333/fff?text=' + encodeURIComponent(movie.title);
      }}
    />
    <h3 className="text-white mt-2 font-semibold truncate">{movie.title}</h3>
    <p className="text-gray-400 text-sm">{movie.release_year}</p>
  </div>
);

const MovieRow = ({ title, movies, onMovieClick }) => (
  <div className="mb-8">
    <h2 className="text-white text-2xl font-semibold mb-4 px-4">{title}</h2>
    <div className="flex space-x-4 overflow-x-auto scrollbar-hide px-4 pb-4">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          onClick={() => onMovieClick(movie)}
        />
      ))}
    </div>
  </div>
);

const Home = () => {
  const [movies, setMovies] = useState([]);
  const [continueWatching, setContinueWatching] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const { currentProfile } = useAuth();

  useEffect(() => {
    if (currentProfile) {
      loadMovies();
      loadContinueWatching();
    }
  }, [currentProfile]);

  const loadMovies = async () => {
    try {
      const response = await axios.get(`${API}/movies`);
      setMovies(response.data);
    } catch (error) {
      console.error('Error loading movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadContinueWatching = async () => {
    if (!currentProfile) return;
    
    try {
      const response = await axios.get(`${API}/views/continue?profile_id=${currentProfile.id}`);
      setContinueWatching(response.data);
    } catch (error) {
      console.error('Error loading continue watching:', error);
    }
  };

  const handleMovieClick = (movie) => {
    setSelectedMovie(movie);
  };

  const closeMovieModal = () => {
    setSelectedMovie(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  const featuredMovie = movies[0];
  const actionMovies = movies.filter(m => m.category === 'action');
  const comedyMovies = movies.filter(m => m.category === 'comedy');
  const dramaMovies = movies.filter(m => m.category === 'drama');
  const animationMovies = movies.filter(m => m.category === 'animation');

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      
      {/* Featured Movie Hero */}
      {featuredMovie && (
        <div 
          className="relative h-screen bg-cover bg-center"
          style={{
            backgroundImage: `linear-gradient(to bottom, transparent, black), url(${featuredMovie.backdrop_url})`
          }}
        >
          <div className="absolute bottom-0 left-0 p-8 max-w-2xl">
            <h1 className="text-6xl font-bold text-white mb-4">{featuredMovie.title}</h1>
            <p className="text-xl text-gray-300 mb-6">{featuredMovie.description}</p>
            <div className="flex space-x-4">
              <button 
                onClick={() => handleMovieClick(featuredMovie)}
                className="bg-white text-black px-8 py-3 rounded font-semibold hover:bg-gray-200 transition-colors flex items-center space-x-2"
              >
                <span>▶</span>
                <span>Play</span>
              </button>
              <button 
                onClick={() => handleMovieClick(featuredMovie)}
                className="bg-gray-600 bg-opacity-70 text-white px-8 py-3 rounded font-semibold hover:bg-opacity-90 transition-colors"
              >
                More Info
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Movie Rows */}
      <div className="relative z-10 -mt-32">
        {/* Continue Watching Section */}
        {continueWatching.length > 0 && (
          <div className="mb-8">
            <h2 className="text-white text-2xl font-semibold mb-4 px-4">Continue Watching</h2>
            <div className="flex space-x-4 overflow-x-auto scrollbar-hide px-4 pb-4">
              {continueWatching.map(({ movie, progress }) => (
                <ContinueWatchingCard
                  key={movie.id}
                  movie={movie}
                  progress={progress}
                  onClick={() => handleMovieClick(movie)}
                />
              ))}
            </div>
          </div>
        )}
        
        {actionMovies.length > 0 && (
          <MovieRow 
            title="Action Movies" 
            movies={actionMovies} 
            onMovieClick={handleMovieClick}
          />
        )}
        
        {comedyMovies.length > 0 && (
          <MovieRow 
            title="Comedy Movies" 
            movies={comedyMovies} 
            onMovieClick={handleMovieClick}
          />
        )}
        
        {dramaMovies.length > 0 && (
          <MovieRow 
            title="Drama Movies" 
            movies={dramaMovies} 
            onMovieClick={handleMovieClick}
          />
        )}

        {animationMovies.length > 0 && (
          <MovieRow 
            title="Animation Movies" 
            movies={animationMovies} 
            onMovieClick={handleMovieClick}
          />
        )}

        {movies.length > 0 && (
          <MovieRow 
            title="All Movies" 
            movies={movies} 
            onMovieClick={handleMovieClick}
          />
        )}
      </div>

      {/* Movie Modal */}
      {selectedMovie && (
        <MovieModal movie={selectedMovie} onClose={closeMovieModal} onContinueWatchingUpdate={loadContinueWatching} />
      )}
    </div>
  );
};

const ContinueWatchingCard = ({ movie, progress, onClick }) => {
  const progressPercent = Math.min((progress.progress_seconds / (movie.duration_minutes * 60)) * 100, 100);
  
  return (
    <div
      onClick={onClick}
      className="min-w-[300px] cursor-pointer transition-transform hover:scale-105 relative"
    >
      <div className="relative">
        <img
          src={movie.poster_url}
          alt={movie.title}
          className="w-full h-[169px] object-cover rounded-lg"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/300x169/333/fff?text=' + encodeURIComponent(movie.title);
          }}
        />
        
        {/* Progress bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-600 rounded-b-lg">
          <div 
            className="h-full bg-red-600 rounded-b-lg transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        
        {/* Play icon overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity bg-black bg-opacity-50 rounded-lg">
          <div className="w-16 h-16 bg-white bg-opacity-90 rounded-full flex items-center justify-center">
            <span className="text-2xl text-black ml-1">▶</span>
          </div>
        </div>
      </div>
      
      <h3 className="text-white mt-2 font-semibold truncate">{movie.title}</h3>
      <p className="text-gray-400 text-sm">
        {Math.floor(progressPercent)}% watched • {movie.release_year}
      </p>
    </div>
  );
};

const MovieModal = ({ movie, onClose, onContinueWatchingUpdate }) => {
  const { currentProfile } = useAuth();
  const [inWatchlist, setInWatchlist] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkWatchlistStatus();
  }, [movie.id, currentProfile]);

  const checkWatchlistStatus = async () => {
    if (!currentProfile) return;
    
    try {
      const response = await axios.get(`${API}/profiles/${currentProfile.id}/watchlist/check/${movie.id}`);
      setInWatchlist(response.data.in_watchlist);
    } catch (error) {
      console.error('Error checking watchlist status:', error);
    }
  };

  const toggleWatchlist = async () => {
    if (!currentProfile || loading) return;
    
    setLoading(true);
    try {
      if (inWatchlist) {
        await axios.delete(`${API}/profiles/${currentProfile.id}/watchlist/${movie.id}`);
        setInWatchlist(false);
      } else {
        await axios.post(`${API}/profiles/${currentProfile.id}/watchlist/${movie.id}`);
        setInWatchlist(true);
      }
    } catch (error) {
      console.error('Error updating watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="relative">
          <img
            src={movie.backdrop_url}
            alt={movie.title}
            className="w-full h-64 object-cover rounded-t-lg"
            onError={(e) => {
              e.target.src = movie.poster_url;
            }}
          />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white text-2xl hover:text-gray-300"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6">
          <h2 className="text-3xl font-bold text-white mb-4">{movie.title}</h2>
          
          <div className="flex items-center space-x-4 mb-4">
            <span className="bg-green-600 text-white px-2 py-1 rounded text-sm">
              {movie.rating}/10
            </span>
            <span className="text-gray-400">{movie.release_year}</span>
            <span className="text-gray-400">{movie.duration_minutes} min</span>
            <span className="text-gray-400 capitalize">{movie.category}</span>
          </div>
          
          <p className="text-gray-300 mb-6">{movie.description}</p>
          
          <div className="flex space-x-4">
            <Link
              to={`/watch/${movie.id}`}
              onClick={onClose}
              className="bg-white text-black px-8 py-3 rounded font-semibold hover:bg-gray-200 transition-colors flex items-center space-x-2"
            >
              <span>▶</span>
              <span>Play</span>
            </Link>
            
            <button
              onClick={toggleWatchlist}
              disabled={loading}
              className={`px-6 py-3 rounded font-semibold transition-colors flex items-center space-x-2 ${
                inWatchlist 
                  ? 'bg-gray-600 text-white hover:bg-gray-700' 
                  : 'bg-gray-600 text-white hover:bg-gray-700'
              }`}
            >
              <span>{inWatchlist ? '✓' : '+'}</span>
              <span>{loading ? 'Loading...' : (inWatchlist ? 'In My List' : 'Add to My List')}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const WatchPage = () => {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const { currentProfile } = useAuth();
  
  // Get movie ID from URL
  const movieId = window.location.pathname.split('/')[2];

  useEffect(() => {
    if (movieId && currentProfile) {
      loadMovie();
    }
  }, [movieId, currentProfile]);

  const loadMovie = async () => {
    try {
      const response = await axios.get(`${API}/movies/${movieId}`);
      setMovie(response.data);
    } catch (error) {
      console.error('Error loading movie:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (currentTime, duration) => {
    if (!currentProfile || !movie) return;
    
    const progressSeconds = Math.floor(currentTime);
    const completed = currentTime >= duration * 0.9; // Mark as completed if 90% watched
    
    try {
      await axios.put(`${API}/views/${movie.id}?profile_id=${currentProfile.id}`, {
        progress_seconds: progressSeconds,
        completed: completed
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const handleTimeUpdate = (e) => {
    const video = e.target;
    const currentTime = video.currentTime;
    const duration = video.duration;
    
    // Update progress every 10 seconds
    if (Math.floor(currentTime) % 10 === 0) {
      updateProgress(currentTime, duration);
    }
  };

  const handleVideoEnded = (e) => {
    const video = e.target;
    updateProgress(video.duration, video.duration);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-xl">Loading movie...</div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-xl">Movie not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="relative">
        <video
          controls
          autoPlay
          className="w-full h-screen object-cover"
          src={movie.video_url}
          onTimeUpdate={handleTimeUpdate}
          onEnded={handleVideoEnded}
        >
          Your browser does not support the video tag.
        </video>
        
        <Link
          to="/"
          className="absolute top-4 left-4 text-white text-2xl hover:text-gray-300 z-10"
        >
          ← Back
        </Link>
      </div>
    </div>
  );
};

const MoviesPage = () => {
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMovies();
  }, [searchTerm, selectedCategory]);

  const loadMovies = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory) params.append('category', selectedCategory);
      
      const response = await axios.get(`${API}/movies?${params}`);
      setMovies(response.data);
    } catch (error) {
      console.error('Error loading movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['action', 'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'thriller', 'documentary', 'animation', 'family'];

  return (
    <div className="min-h-screen bg-black pt-20">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-white mb-8">Movies</h1>
        
        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <input
            type="text"
            placeholder="Search movies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full md:w-96 px-4 py-3 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-red-500"
          />
          
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('')}
              className={`px-4 py-2 rounded ${!selectedCategory ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'} hover:bg-red-700 transition-colors`}
            >
              All Categories
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded capitalize ${selectedCategory === category ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'} hover:bg-red-700 transition-colors`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Movies Grid */}
        {loading ? (
          <div className="text-white text-center">Loading movies...</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {movies.map((movie) => (
              <MovieCard
                key={movie.id}
                movie={movie}
                onClick={() => setSelectedMovie(movie)}
              />
            ))}
          </div>
        )}

        {movies.length === 0 && !loading && (
          <div className="text-gray-400 text-center py-16">
            No movies found matching your criteria.
          </div>
        )}
      </div>

      {/* Movie Modal */}
      {selectedMovie && (
        <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
      )}
    </div>
  );
};

const MyListPage = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const { currentProfile } = useAuth();

  useEffect(() => {
    if (currentProfile) {
      loadWatchlist();
    }
  }, [currentProfile]);

  const loadWatchlist = async () => {
    if (!currentProfile) return;
    
    try {
      const response = await axios.get(`${API}/profiles/${currentProfile.id}/watchlist`);
      setWatchlist(response.data);
    } catch (error) {
      console.error('Error loading watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMovieClick = (movie) => {
    setSelectedMovie(movie);
  };

  const closeMovieModal = () => {
    setSelectedMovie(null);
    // Reload watchlist to reflect any changes
    loadWatchlist();
  };

  return (
    <div className="min-h-screen bg-black pt-20">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-white mb-8">My List</h1>
        
        {loading ? (
          <div className="text-white text-center">Loading your list...</div>
        ) : watchlist.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {watchlist.map((movie) => (
              <MovieCard
                key={movie.id}
                movie={movie}
                onClick={() => handleMovieClick(movie)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-gray-400 text-xl mb-4">Your list is empty</div>
            <p className="text-gray-500 mb-6">
              Add movies and shows to your list to watch them later.
            </p>
            <Link 
              to="/movies" 
              className="bg-red-600 text-white px-6 py-3 rounded font-semibold hover:bg-red-700 transition-colors"
            >
              Browse Movies
            </Link>
          </div>
        )}
      </div>

      {/* Movie Modal */}
      {selectedMovie && (
        <MovieModal movie={selectedMovie} onClose={closeMovieModal} />
      )}
    </div>
  );
};

const SearchPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/movies?search=${encodeURIComponent(searchTerm)}`);
      setMovies(response.data);
    } catch (error) {
      console.error('Error searching movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-black pt-20">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-white mb-8">Search</h1>
        
        <div className="mb-8">
          <div className="flex gap-4 max-w-2xl">
            <input
              type="text"
              placeholder="Search for movies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 px-4 py-3 bg-gray-800 text-white rounded border border-gray-600 focus:outline-none focus:border-red-500"
            />
            <button
              onClick={handleSearch}
              className="px-8 py-3 bg-red-600 text-white rounded font-semibold hover:bg-red-700 transition-colors"
            >
              Search
            </button>
          </div>
        </div>

        {loading && (
          <div className="text-white text-center">Searching...</div>
        )}

        {movies.length > 0 && !loading && (
          <div>
            <h2 className="text-2xl font-semibold text-white mb-6">
              Search Results ({movies.length})
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {movies.map((movie) => (
                <MovieCard
                  key={movie.id}
                  movie={movie}
                  onClick={() => setSelectedMovie(movie)}
                />
              ))}
            </div>
          </div>
        )}

        {movies.length === 0 && !loading && searchTerm && (
          <div className="text-gray-400 text-center py-16">
            No movies found for "{searchTerm}".
          </div>
        )}
      </div>

      {/* Movie Modal */}
      {selectedMovie && (
        <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
      )}
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AuthProvider>
  );
};

const AppContent = () => {
  const { user, currentProfile, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <LoginForm />;
  }

  if (!currentProfile) {
    return <ProfileSelector />;
  }

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/movies" element={<MoviesPage />} />
      <Route path="/my-list" element={<MyListPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="/watch/:movieId" element={<WatchPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

export default App;