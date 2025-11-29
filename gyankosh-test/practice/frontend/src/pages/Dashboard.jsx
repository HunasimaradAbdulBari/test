import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import StudentForm from '../components/StudentForm';
import StudentTable from '../components/StudentTable';
import StatusModal from '../components/StatusModal';
import styles from '../styles/pages/Dashboard.module.css';

const Dashboard = () => {
  const [students, setStudents] = useState(() => {
    const saved = localStorage.getItem('students');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    localStorage.setItem('students', JSON.stringify(students));
  }, [students]);

  const handleAddStudent = (newStudent) => {
    setStudents(prev => [...prev, newStudent]);
  };

  const handleDeleteStudent = (studentId) => {
    if (window.confirm('Are you sure you want to delete this student application?')) {
      setStudents(prev => prev.filter(s => s.id !== studentId));
    }
  };

  const handleUpdateStatus = (studentId, newStatus) => {
    setStudents(prev =>
      prev.map(s =>
        s.id === studentId ? { ...s, status: newStatus } : s
      )
    );
  };

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

        <StudentTable
          students={filteredStudents}
          onDeleteStudent={handleDeleteStudent}
          onOpenStatusModal={setSelectedStudent}
        />

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