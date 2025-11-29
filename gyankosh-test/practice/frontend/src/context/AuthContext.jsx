import { useState, createContext, useContext, useEffect } from 'react';
import api from '../services/api';

// Create context to share auth data across the app
const AuthContext = createContext();

// AuthProvider component - wraps the entire app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');

      if (token && savedUser) {
        try {
          // Verify token is still valid by fetching user data
          const response = await api.get('/auth/me');
          if (response.data.success) {
            setUser(response.data.data.user);
          } else {
            // Token invalid, clear storage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
          }
        } catch (error) {
          console.error('Auth initialization error:', error);
          // Token invalid, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  // Login function - calls backend API
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      
      if (response.data.success) {
        const { user, token } = response.data.data;
        
        // Save token and user to localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        // Update state
        setUser(user);
        
        return { success: true };
      }
      
      return { success: false, error: response.data.error };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed. Please try again.'
      };
    }
  };

  // Register function - calls backend API
  const register = async (name, email, password) => {
    try {
      const response = await api.post('/auth/register', { name, email, password });
      
      if (response.data.success) {
        return { success: true };
      }
      
      return { success: false, error: response.data.error };
    } catch (error) {
      console.error('Register error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.response?.data?.details?.[0]?.message || 'Registration failed. Please try again.'
      };
    }
  };

  // Logout function - clears everything
  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth anywhere in the app
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};