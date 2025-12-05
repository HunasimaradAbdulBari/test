import jwt from 'jsonwebtoken';
import User from '../models/User.js';

/**
 * Authentication Middleware
 * Protects routes by verifying JWT token
 * Adds user object to request if token is valid
 */
const protect = async (req, res, next) => {
  let token;

  // Check if authorization header exists and starts with 'Bearer'
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    try {
      // Extract token from header (format: "Bearer <token>")
      token = req.headers.authorization.split(' ')[1];

      // Verify token and decode payload
      const decoded = jwt.verify(token, process.env.JWT_SECRET);

      // Get user from database using decoded id (exclude password)
      req.user = await User.findById(decoded.id).select('-password');

      // Check if user exists
      if (!req.user) {
        return res.status(401).json({
          success: false,
          error: 'User not found'
        });
      }

      next(); // User is authenticated, proceed to next middleware/route
    } catch (error) {
      console.error('Token verification error:', error.message);
      
      // Handle different JWT errors
      if (error.name === 'TokenExpiredError') {
        return res.status(401).json({
          success: false,
          error: 'Token has expired. Please login again.'
        });
      }
      
      if (error.name === 'JsonWebTokenError') {
        return res.status(401).json({
          success: false,
          error: 'Invalid token. Please login again.'
        });
      }

      return res.status(401).json({
        success: false,
        error: 'Not authorized to access this route'
      });
    }
  }

  // No token found in header
  if (!token) {
    return res.status(401).json({
      success: false,
      error: 'Not authorized. No token provided.'
    });
  }
};

export default protect;