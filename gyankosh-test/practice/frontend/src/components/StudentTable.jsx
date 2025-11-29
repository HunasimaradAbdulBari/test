import React from 'react';
import styles from '../styles/components/StudentTable.module.css';

const StudentTable = ({ students, onDeleteStudent, onOpenStatusModal }) => {
  const getStatusClass = (status) => {
    const statusMap = {
      'Pending': styles.statusPending,
      'Approved': styles.statusApproved,
      'Rejected': styles.statusRejected
    };
    return `${styles.statusBadge} ${statusMap[status]}`;
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className={styles.tableContainer}>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead className={styles.thead}>
            <tr>
              <th className={styles.th}>Student Name</th>
              <th className={styles.th}>Email</th>
              <th className={styles.th}>Phone</th>
              <th className={styles.th}>Course</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Applied Date</th>
              <th className={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody className={styles.tbody}>
            {students.length === 0 ? (
              <tr>
                <td colSpan="7" className={styles.td}>
                  <div className={styles.emptyState}>
                    <div className={styles.emptyIcon}>
                      <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                    </div>
                    <div className={styles.emptyTitle}>No Applications Yet</div>
                    <div className={styles.emptyText}>Add your first student application above!</div>
                  </div>
                </td>
              </tr>
            ) : (
              students.map((student) => (
                <tr key={student.id} className={styles.tr}>
                  <td className={styles.td}>
                    <div className={styles.nameCell}>
                      <div className={styles.avatar}>
                        {getInitials(student.name)}
                      </div>
                      <span className={styles.nameText}>{student.name}</span>
                    </div>
                  </td>
                  <td className={styles.td}>{student.email}</td>
                  <td className={styles.td}>{student.phone}</td>
                  <td className={styles.td}>{student.course}</td>
                  <td className={styles.td}>
                    <span className={getStatusClass(student.status)}>
                      {student.status}
                    </span>
                  </td>
                  <td className={styles.td}>{student.appliedDate}</td>
                  <td className={styles.td}>
                    <div className={styles.actions}>
                      <button
                        onClick={() => onOpenStatusModal(student)}
                        className={`${styles.actionButton} ${styles.editButton}`}
                      >
                        Change Status
                      </button>
                      <button
                        onClick={() => onDeleteStudent(student.id)}
                        className={`${styles.actionButton} ${styles.deleteButton}`}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StudentTable;