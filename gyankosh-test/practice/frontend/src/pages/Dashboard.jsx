import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import StudentForm from '../components/StudentForm';
import StudentTable from '../components/StudentTable';
import StatusModal from '../components/StatusModal';
import styles from '../styles/pages/Dashboard.module.css';

const Dashboard = () => {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch students from API on component mount
  useEffect(() => {
    fetchStudents();
  }, []);

  // Fetch students from backend
  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await api.get('/students');
      
      if (response.data.success) {
        // Transform data to match frontend format
        const transformedStudents = response.data.data.map(student => ({
          id: student._id,
          name: student.name,
          email: student.email,
          phone: student.phone,
          course: student.course,
          status: student.status,
          appliedDate: new Date(student.appliedDate).toLocaleDateString()
        }));
        
        setStudents(transformedStudents);
      }
    } catch (error) {
      console.error('Error fetching students:', error);
      setError('Failed to load students. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Add new student
  const handleAddStudent = async (newStudent) => {
    try {
      const response = await api.post('/students', {
        name: newStudent.name,
        email: newStudent.email,
        phone: newStudent.phone,
        course: newStudent.course,
        status: newStudent.status
      });

      if (response.data.success) {
        // Add to state with transformed data
        const student = response.data.data;
        const transformedStudent = {
          id: student._id,
          name: student.name,
          email: student.email,
          phone: student.phone,
          course: student.course,
          status: student.status,
          appliedDate: new Date(student.appliedDate).toLocaleDateString()
        };
        
        setStudents(prev => [transformedStudent, ...prev]);
        alert('Student application added successfully!');
      }
    } catch (error) {
      console.error('Error adding student:', error);
      alert(error.response?.data?.error || 'Failed to add student. Please try again.');
    }
  };

  // Delete student
  const handleDeleteStudent = async (studentId) => {
    if (!window.confirm('Are you sure you want to delete this student application?')) {
      return;
    }

    try {
      const response = await api.delete(`/students/${studentId}`);
      
      if (response.data.success) {
        setStudents(prev => prev.filter(s => s.id !== studentId));
        alert('Student deleted successfully!');
      }
    } catch (error) {
      console.error('Error deleting student:', error);
      alert(error.response?.data?.error || 'Failed to delete student. Please try again.');
    }
  };

  // Update student status
  const handleUpdateStatus = async (studentId, newStatus) => {
    try {
      // Find the student to get all their data
      const student = students.find(s => s.id === studentId);
      
      const response = await api.put(`/students/${studentId}`, {
        name: student.name,
        email: student.email,
        phone: student.phone,
        course: student.course,
        status: newStatus
      });

      if (response.data.success) {
        setStudents(prev =>
          prev.map(s =>
            s.id === studentId ? { ...s, status: newStatus } : s
          )
        );
        alert('Status updated successfully!');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert(error.response?.data?.error || 'Failed to update status. Please try again.');
    }
  };

  // Filter students based on search term
  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.course.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className={styles.dashboardContainer}>
      <Navbar />
      
      <div className={styles.dashboardContent}>
        {error && (
          <div style={{ 
            padding: '1rem', 
            marginBottom: '1rem', 
            background: '#fee2e2', 
            color: '#dc2626', 
            borderRadius: '0.5rem' 
          }}>
            {error}
          </div>
        )}

        <div className={styles.searchContainer}>
          <div className={styles.searchWrapper}>
            <input
              type="text"
              placeholder="Search by name, email, course, or status..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={styles.searchInput}
            />
            <svg className={styles.searchIcon} width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <StudentForm onAddStudent={handleAddStudent} />

        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            All Applications
            <span className={styles.badge}>{filteredStudents.length}</span>
          </h2>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'white' }}>
            Loading students...
          </div>
        ) : (
          <StudentTable
            students={filteredStudents}
            onDeleteStudent={handleDeleteStudent}
            onOpenStatusModal={setSelectedStudent}
          />
        )}

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