import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import './index.css';

// Main App Component with Routing Logic
function AppContent() {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState('login');

  // Navigation handler - switches between pages
  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  // If user is logged in, show Dashboard
  if (user) {
    return <Dashboard />;
  }

  // If not logged in, show Login or Register based on currentPage
  return (
    <>
      {currentPage === 'login' && <Login onNavigate={handleNavigate} />}
      {currentPage === 'register' && <Register onNavigate={handleNavigate} />}
    </>
  );
}

// Wrap entire app with AuthProvider so all components can access auth
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;