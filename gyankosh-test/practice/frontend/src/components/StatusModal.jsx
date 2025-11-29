import React, { useState } from 'react';
import Button from './Button';
import styles from '../styles/components/StatusModal.module.css';

const StatusModal = ({ student, onClose, onUpdateStatus }) => {
  const [selectedStatus, setSelectedStatus] = useState(student.status);

  const handleUpdate = () => {
    onUpdateStatus(student.id, selectedStatus);
    onClose();
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h3 className={styles.modalTitle}>
            <div className={styles.titleIcon}>
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            Update Application Status
          </h3>
          <button className={styles.closeButton} onClick={onClose}>
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.modalBody}>
          <div className={styles.studentInfo}>
            <div className={styles.infoRow}>
              <div className={styles.infoIcon}>
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div>
                <div className={styles.infoLabel}>Student</div>
                <div className={styles.infoValue}>{student.name}</div>
              </div>
            </div>
            <div className={styles.infoRow}>
              <div className={styles.infoIcon}>
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div>
                <div className={styles.infoLabel}>Course</div>
                <div className={styles.infoValue}>{student.course}</div>
              </div>
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Select New Status</label>
            <div className={styles.selectWrapper}>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className={styles.select}
              >
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
              <svg className={styles.selectIcon} width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className={styles.modalFooter}>
          <button onClick={handleUpdate} className={`${styles.actionButton} ${styles.updateButton}`}>
            Update Status
          </button>
          <button onClick={onClose} className={`${styles.actionButton} ${styles.cancelButton}`}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatusModal;