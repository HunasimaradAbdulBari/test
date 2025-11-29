import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import StudentForm from '../components/StudentForm';
import StudentTable from '../components/StudentTable';
import StatusModal from '../components/StatusModal';

// Main Dashboard component - manages all student data
const Dashboard = () => {
  // Load students from localStorage on first render
  const [students, setStudents] = useState(() => {
    const saved = localStorage.getItem('students');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);

  // Save students to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('students', JSON.stringify(students));
  }, [students]);

  // Add new student to the list
  const handleAddStudent = (newStudent) => {
    setStudents(prev => [...prev, newStudent]);
  };

  // Delete student from the list
  const handleDeleteStudent = (studentId) => {
    if (window.confirm('Are you sure you want to delete this student application?')) {
      setStudents(prev => prev.filter(s => s.id !== studentId));
    }
  };

  // Update student status
  const handleUpdateStatus = (studentId, newStatus) => {
    setStudents(prev =>
      prev.map(s =>
        s.id === studentId ? { ...s, status: newStatus } : s
      )
    );
  };

  // Filter students based on search term
  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.course.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by name, email, course, or status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
          />
        </div>

        {/* Add Student Form */}
        <StudentForm onAddStudent={handleAddStudent} />

        {/* Students Table */}
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            All Applications ({filteredStudents.length})
          </h2>
        </div>
        <StudentTable
          students={filteredStudents}
          onDeleteStudent={handleDeleteStudent}
          onOpenStatusModal={setSelectedStudent}
        />

        {/* Status Update Modal */}
        {selectedStudent && (
          <StatusModal
            student={selectedStudent}
            onClose={() => setSelectedStudent(null)}
            onUpdateStatus={handleUpdateStatus}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;