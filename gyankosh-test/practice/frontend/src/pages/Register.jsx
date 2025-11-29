import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import styles from '../styles/pages/Register.module.css';

const Register = ({ onNavigate }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async () => {
    setError('');
    setSuccess(false);
    setIsLoading(true);

    // Validation
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setIsLoading(false);
      return;
    }

    // Call register API
    const result = await register(name, email, password);
    
    if (result.success) {
      setSuccess(true);
      setName('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        onNavigate('login');
      }, 2000);
    } else {
      setError(result.error);
    }
    
    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSubmit();
    }
  };

  return (
    <div className={styles.registerContainer}>
      <div className={styles.registerCard}>
        <div className={styles.header}>
          <h2 className={styles.title}>Create Account</h2>
          <p className={styles.subtitle}>Join our admission portal</p>
        </div>
        
        {error && (
          <div className={`${styles.alert} ${styles.alertError}`}>
            {error}
          </div>
        )}

        {success && (
          <div className={`${styles.alert} ${styles.alertSuccess}`}>
            Account created successfully! Redirecting to login...
          </div>
        )}

        <div className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.label}>Full Name</label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyPress={handleKeyPress}
                className={styles.input}
                placeholder="John Doe"
                disabled={isLoading || success}
              />
            </div>
          </div>

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
                disabled={isLoading || success}
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
                disabled={isLoading || success}
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Confirm Password</label>
            <div className={styles.inputWrapper}>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onKeyPress={handleKeyPress}
                className={styles.input}
                placeholder="••••••••"
                disabled={isLoading || success}
              />
            </div>
          </div>

          <Button 
            onClick={handleSubmit} 
            variant="primary" 
            fullWidth={true}
            loading={isLoading}
            disabled={isLoading || success}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </div>

        <p className={styles.footer}>
          Already have an account?{' '}
          <span className={styles.link} onClick={() => !isLoading && !success && onNavigate('login')}>
            Login here
          </span>
        </p>
      </div>
    </div>
  );
};

export default Register;