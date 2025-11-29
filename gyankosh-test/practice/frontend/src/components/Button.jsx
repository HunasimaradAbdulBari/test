import React from 'react';

// Reusable Button Component with different variants
const Button = ({ children, onClick, variant = 'primary', className = '' }) => {
  // Base styles that apply to all buttons
  const baseStyle = 'px-4 py-2 rounded-lg font-medium transition-all duration-200 cursor-pointer';
  
  // Different color schemes based on variant prop
  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600 shadow-sm hover:shadow-md',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md',
    success: 'bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md'
  };

  return (
    <button
      onClick={onClick}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;