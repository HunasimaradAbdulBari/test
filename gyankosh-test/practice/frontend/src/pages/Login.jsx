import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import styles from '../styles/pages/Login.module.css';

const Login = ({ onNavigate }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async () => {
    setError('');
    setIsLoading(true);

    // Basic validation
    if (!email || !password) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    // Call login API
    const result = await login(email, password);
    
    if (!result.success) {
      setError(result.error);
      setIsLoading(false);
    }
    // If success, user state will update and Dashboard will show automatically
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSubmit();
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <h2 className={styles.title}>Welcome Back</h2>
          <p className={styles.subtitle}>Login to your admission portal</p>
        </div>
        
        {error && (
          <div className={`${styles.alert} ${styles.alertError}`}>
            {error}
          </div>
        )}

        <div className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.label}>Email Address</label>
            <div className={styles.inputWrapper}>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyPress={handleKeyPress}
                className={styles.input}
                placeholder="you@example.com"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Password</label>
            <div className={styles.inputWrapper}>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={handleKeyPress}
                className={styles.input}
                placeholder="••••••••"
                disabled={isLoading}
              />
            </div>
          </div>

          <Button 
            onClick={handleSubmit} 
            variant="primary" 
            fullWidth={true}
            loading={isLoading}
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
        </div>

        <p className={styles.footer}>
          Don't have an account?{' '}
          <span className={styles.link} onClick={() => !isLoading && onNavigate('register')}>
            Register here
          </span>
        </p>
      </div>
    </div>
  );
};

export default Login;