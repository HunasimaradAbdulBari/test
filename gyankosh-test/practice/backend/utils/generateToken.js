import jwt from 'jsonwebtoken';

/**
 * Generate JWT Token
 * Creates a signed JWT token with user ID as payload
 * 
 * @param {string} userId - MongoDB User ID
 * @returns {string} - Signed JWT token
 */
const generateToken = (userId) => {
  return jwt.sign(
    { id: userId }, // Payload - user id
    process.env.JWT_SECRET, // Secret key from environment
    {
      expiresIn: process.env.JWT_EXPIRE || '30d' // Token expiration
    }
  );
};

export default generateToken;