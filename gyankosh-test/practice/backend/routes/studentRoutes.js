import express from 'express';
import { body } from 'express-validator';
import {
  createStudent,
  getStudents,
  getStudent,
  updateStudent,
  deleteStudent
} from '../controllers/studentController.js';
import protect from '../middleware/auth.js';
import validate from '../middleware/validate.js';

const router = express.Router();

// All routes are protected - require authentication
router.use(protect);

/**
 * Student validation rules
 */
const studentValidation = [
  body('name')
    .trim()
    .notEmpty()
    .withMessage('Student name is required')
    .isLength({ min: 2 })
    .withMessage('Name must be at least 2 characters long'),
  body('email')
    .trim()
    .notEmpty()
    .withMessage('Email is required')
    .isEmail()
    .withMessage('Please provide a valid email'),
  body('phone')
    .trim()
    .notEmpty()
    .withMessage('Phone number is required')
    .matches(/^[0-9]{10}$/)
    .withMessage('Please provide a valid 10-digit phone number'),
  body('course')
    .notEmpty()
    .withMessage('Course is required')
    .isIn([
      'Computer Science',
      'Business Administration',
      'Mechanical Engineering',
      'Medicine',
      'Law'
    ])
    .withMessage('Please select a valid course'),
  body('status')
    .optional()
    .isIn(['Pending', 'Approved', 'Rejected'])
    .withMessage('Invalid status value')
];

/**
 * Create and Get All Students Routes
 * POST /api/students - Create new student
 * GET /api/students - Get all students with optional filters
 */
router.route('/')
  .post(studentValidation, validate, createStudent)
  .get(getStudents);

/**
 * Get, Update, Delete Single Student Routes
 * GET /api/students/:id - Get single student
 * PUT /api/students/:id - Update student
 * DELETE /api/students/:id - Delete student
 */
router.route('/:id')
  .get(getStudent)
  .put(studentValidation, validate, updateStudent)
  .delete(deleteStudent);

export default router;