import React, { useState, createContext, useContext, useEffect } from 'react';
const Button = ({ children, onClick, variant = 'primary', className = '' }) => {
  // Different button styles based on variant prop
  const baseStyle = 'px-4 py-2 rounded-lg font-medium transition-all duration-200 cursor-pointer';
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