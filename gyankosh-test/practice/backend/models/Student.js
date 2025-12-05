import mongoose from 'mongoose';

/**
 * Student Schema for Admission Applications
 * Stores student application data with reference to user
 */
const studentSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Please add student name'],
      trim: true,
      minlength: [2, 'Name must be at least 2 characters long']
    },
    email: {
      type: String,
      required: [true, 'Please add student email'],
      trim: true,
      match: [
        /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
        'Please add a valid email'
      ]
    },
    phone: {
      type: String,
      required: [true, 'Please add phone number'],
      trim: true,
      match: [
        /^[0-9]{10}$/,
        'Please add a valid 10-digit phone number'
      ]
    },
    course: {
      type: String,
      required: [true, 'Please select a course'],
      enum: {
        values: [
          'Computer Science',
          'Business Administration',
          'Mechanical Engineering',
          'Medicine',
          'Law'
        ],
        message: '{VALUE} is not a valid course'
      }
    },
    status: {
      type: String,
      default: 'Pending',
      enum: {
        values: ['Pending', 'Approved', 'Rejected'],
        message: '{VALUE} is not a valid status'
      }
    },
    appliedDate: {
      type: Date,
      default: Date.now
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'User ID is required']
    }
  },
  {
    timestamps: true // Automatically adds createdAt and updatedAt
  }
);

/**
 * Create indexes for better query performance
 * Index on userId for fast user-specific queries
 * Compound index on userId and status for filtered queries
 */
studentSchema.index({ userId: 1 });
studentSchema.index({ userId: 1, status: 1 });
studentSchema.index({ userId: 1, course: 1 });

/**
 * Virtual field to format appliedDate for frontend
 */
studentSchema.virtual('formattedDate').get(function () {
  return this.appliedDate.toLocaleDateString();
});

/**
 * Ensure virtuals are included when converting to JSON
 */
studentSchema.set('toJSON', { virtuals: true });
studentSchema.set('toObject', { virtuals: true });

const Student = mongoose.model('Student', studentSchema);

export default Student;