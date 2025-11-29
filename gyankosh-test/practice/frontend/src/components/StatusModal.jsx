import React, { useState } from 'react';
import Button from './Button';

// Modal component to update student application status
const StatusModal = ({ student, onClose, onUpdateStatus }) => {
  const [selectedStatus, setSelectedStatus] = useState(student.status);

  const handleUpdate = () => {
    onUpdateStatus(student.id, selectedStatus);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Update Application Status</h3>
        
        <div className="mb-4">
          <p className="text-gray-600 mb-2">Student: <span className="font-medium">{student.name}</span></p>
          <p className="text-gray-600">Course: <span className="font-medium">{student.course}</span></p>
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2">Select Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="Pending">Pending</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>

        <div className="flex space-x-3">
          <Button onClick={handleUpdate} variant="success" className="flex-1">
            Update Status
          </Button>
          <Button onClick={onClose} variant="secondary" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
};

export default StatusModal;