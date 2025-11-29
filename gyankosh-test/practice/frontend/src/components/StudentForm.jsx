import React, { useState, createContext, useContext, useEffect } from 'react';
const StudentForm = ({ onAddStudent }) => {
  // Form state - holds all input values
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    course: '',
    status: 'Pending'
  });

  // Update form fields as user types
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Submit form
  const handleSubmit = () => {
    // Validate all fields are filled
    if (!formData.name || !formData.email || !formData.phone || !formData.course) {
      alert('Please fill in all fields');
      return;
    }

    // Create new student object with unique ID
    const newStudent = {
      id: Date.now(), // Simple unique ID using timestamp
      ...formData,
      appliedDate: new Date().toLocaleDateString()
    };

    // Send to parent component
    onAddStudent(newStudent);

    // Clear form after submission
    setFormData({
      name: '',
      email: '',
      phone: '',
      course: '',
      status: 'Pending'
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Add New Student Application</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-gray-700 font-medium mb-2">Full Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Enter student name"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-2">Email Address *</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="student@example.com"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-2">Phone Number *</label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="1234567890"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-2">Course *</label>
          <select
            name="course"
            value={formData.course}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">Select Course</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Business Administration">Business Administration</option>
            <option value="Mechanical Engineering">Mechanical Engineering</option>
            <option value="Medicine">Medicine</option>
            <option value="Law">Law</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <Button onClick={handleSubmit} variant="primary">
            Add Student Application
          </Button>
        </div>
      </div>
    </div>
  );
};