import React, { useState } from 'react';
import Button from './Button';
import styles from '../styles/components/StudentForm.module.css';

const StudentForm = ({ onAddStudent }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    course: '',
    status: 'Pending'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = () => {
    if (!formData.name || !formData.email || !formData.phone || !formData.course) {
      alert('Please fill in all fields');
      return;
    }

    const newStudent = {
      id: Date.now(),
      ...formData,
      appliedDate: new Date().toLocaleDateString()
    };

    onAddStudent(newStudent);

    setFormData({
      name: '',
      email: '',
      phone: '',
      course: '',
      status: 'Pending'
    });

    alert('Student application added successfully!');
  };

  return (
    <div className={styles.formContainer}>
      <div className={styles.formHeader}>
        <div className={styles.formIcon}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="24" height="24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </div>
        <h2 className={styles.formTitle}>Add New Student Application</h2>
      </div>
      
      <div className={styles.formGrid}>
        <div className={styles.formGroup}>
          <label className={styles.label}>
            Full Name <span className={styles.required}>*</span>
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={styles.input}
              placeholder="Enter student name"
            />
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            Email Address <span className={styles.required}>*</span>
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={styles.input}
              placeholder="student@example.com"
            />
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            Phone Number <span className={styles.required}>*</span>
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className={styles.input}
              placeholder="1234567890"
            />
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            Course <span className={styles.required}>*</span>
          </label>
          <select
            name="course"
            value={formData.course}
            onChange={handleChange}
            className={styles.select}
          >
            <option value="">Select Course</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Business Administration">Business Administration</option>
            <option value="Mechanical Engineering">Mechanical Engineering</option>
            <option value="Medicine">Medicine</option>
            <option value="Law">Law</option>
          </select>
        </div>
      </div>

      <div className={styles.buttonContainer}>
        <Button onClick={handleSubmit} variant="primary">
          Add Student Application
        </Button>
      </div>
    </div>
  );
};

export default StudentForm;