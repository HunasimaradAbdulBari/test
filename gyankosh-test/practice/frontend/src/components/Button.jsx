import React from 'react';
import styles from '../styles/components/Button.module.css';

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium',
  fullWidth = false,
  disabled = false,
  loading = false,
  className = '' 
}) => {
  const buttonClasses = [
    styles.button,
    styles[variant],
    size && styles[size],
    fullWidth && styles.fullWidth,
    loading && styles.loading,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      onClick={onClick}
      className={buttonClasses}
      disabled={disabled || loading}
    >
      {children}
    </button>
  );
};

export default Button;