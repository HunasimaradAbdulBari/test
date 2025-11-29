import { useState, createContext, useContext } from 'react';

// Create context to share auth data across the app
const AuthContext = createContext();

// AuthProvider component - wraps the entire app
export const AuthProvider = ({ children }) => {
  // Check if user is already logged in (from localStorage)
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('currentUser');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // Login function - saves user to state and localStorage
  const login = (email, password) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const foundUser = users.find(u => u.email === email && u.password === password);
    
    if (foundUser) {
      const userData = { email: foundUser.email, name: foundUser.name };
      setUser(userData);
      localStorage.setItem('currentUser', JSON.stringify(userData));
      return true;
    }
    return false;
  };

  // Register function - creates new user account
  const register = (name, email, password) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    
    // Check if user already exists
    if (users.find(u => u.email === email)) {
      return false;
    }
    
    // Add new user to array and save
    users.push({ name, email, password });
    localStorage.setItem('users', JSON.stringify(users));
    return true;
  };

  // Logout function - clears user from state and localStorage
  const logout = () => {
    setUser(null);
    localStorage.removeItem('currentUser');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
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