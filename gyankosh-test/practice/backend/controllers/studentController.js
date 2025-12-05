import Student from '../models/Student.js';

/**
 * @desc    Create new student application
 * @route   POST /api/students
 * @access  Private
 */
export const createStudent = async (req, res, next) => {
  try {
    const { name, email, phone, course, status } = req.body;

    // Create student with userId from authenticated user
    const student = await Student.create({
      name,
      email,
      phone,
      course,
      status: status || 'Pending',
      userId: req.user._id,
      appliedDate: new Date()
    });

    res.status(201).json({
      success: true,
      message: 'Student application created successfully',
      data: student
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @desc    Get all students for logged in user
 * @route   GET /api/students
 * @access  Private
 */
export const getStudents = async (req, res, next) => {
  try {
    // Build query object
    const query = { userId: req.user._id };

    // Add filters from query parameters
    if (req.query.status) {
      query.status = req.query.status;
    }

    if (req.query.course) {
      query.course = req.query.course;
    }

    // Search functionality
    if (req.query.search) {
      const searchRegex = new RegExp(req.query.search, 'i');
      query.$or = [
        { name: searchRegex },
        { email: searchRegex },
        { course: searchRegex }
      ];
    }

    // Execute query with sorting (newest first)
    const students = await Student.find(query)
      .sort({ appliedDate: -1 })
      .lean();

    res.status(200).json({
      success: true,
      count: students.length,
      data: students
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @desc    Get single student by ID
 * @route   GET /api/students/:id
 * @access  Private
 */
export const getStudent = async (req, res, next) => {
  try {
    const student = await Student.findById(req.params.id);

    // Check if student exists
    if (!student) {
      return res.status(404).json({
        success: false,
        error: 'Student not found'
      });
    }

    // Verify student belongs to logged in user
    if (student.userId.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        error: 'Not authorized to access this student'
      });
    }

    res.status(200).json({
      success: true,
      data: student
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @desc    Update student
 * @route   PUT /api/students/:id
 * @access  Private
 */
export const updateStudent = async (req, res, next) => {
  try {
    let student = await Student.findById(req.params.id);

    // Check if student exists
    if (!student) {
      return res.status(404).json({
        success: false,
        error: 'Student not found'
      });
    }

    // Verify student belongs to logged in user
    if (student.userId.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        error: 'Not authorized to update this student'
      });
    }

    // Update student
    student = await Student.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true
      }
    );

    res.status(200).json({
      success: true,
      message: 'Student updated successfully',
      data: student
    });
  } catch (error) {
    next(error);
  }
};

/**
 * @desc    Delete student
 * @route   DELETE /api/students/:id
 * @access  Private
 */
export const deleteStudent = async (req, res, next) => {
  try {
    const student = await Student.findById(req.params.id);

    // Check if student exists
    if (!student) {
      return res.status(404).json({
        success: false,
        error: 'Student not found'
      });
    }

    // Verify student belongs to logged in user
    if (student.userId.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        error: 'Not authorized to delete this student'
      });
    }

    await student.deleteOne();

    res.status(200).json({
      success: true,
      message: 'Student deleted successfully',
      data: {}
    });
  } catch (error) {
    next(error);
  }
};