import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const AddGoogleAccount = () => {
  const [alias, setAlias] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch(`http://127.0.0.1:5000/gooPaths/${alias}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        alert(data.message ? `Success: ${data.message}` : 'Success: Account linked successfully');
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h2>Fileppe</h2>
        {/* Sidebar content copied from Dashboard */}
      </div>

      <div className="workspace">
        <h2>Link Google Account</h2>
        <form onSubmit={handleSubmit}>
          <label htmlFor="alias">Account Alias:</label>
          <input
            type="text"
            id="alias"
            value={alias}
            onChange={(e) => setAlias(e.target.value)}
            required
          />
          <button type="submit" className="styled-button">Link Account</button>
        </form>

        {/* Back to Dashboard Button */}
        <div className="back-button-container">
          <button className="styled-button" onClick={() => navigate('/')}>
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddGoogleAccount;
