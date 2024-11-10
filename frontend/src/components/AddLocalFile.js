import React from 'react';
import { useNavigate } from 'react-router-dom';
import SelectDirectoryPopup from './SelectDirectoryPopup';
import './Dashboard.css';

const AddLocalFile = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h2>Fileppe</h2>
        {/* Sidebar content copied from Dashboard */}
      </div>

      <div className="workspace">
        <h2>Add Local File Path</h2>
        <SelectDirectoryPopup />
        <div className="back-button-container">
          <button className="styled-button" onClick={() => navigate('/')} style={{ marginTop: '20px' }}>
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddLocalFile;
