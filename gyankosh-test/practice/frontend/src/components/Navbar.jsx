import React from 'react';
import { useAuth } from '../context/AuthContext';
import Button from './Button';
import styles from '../styles/components/Navbar.module.css';

const Navbar = () => {
  const { user, logout } = useAuth();

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarContainer}>
        <div className={styles.navbarContent}>
          <div className={styles.logoSection}>
            <div className={styles.logoIcon}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 className={styles.title}>Admission Portal</h1>
          </div>
          
          <div className={styles.userSection}>
            <span className={styles.welcomeText}>
              Welcome, <span className={styles.userName}>{user?.name}</span>
            </span>
            <div className={styles.userAvatar}>
              {getInitials(user?.name || 'User')}
            </div>
            <Button onClick={logout} variant="secondary">
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;