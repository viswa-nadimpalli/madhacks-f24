// frontend/src/components/Dashboard.js

import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import './Dashboard.css'; // Import CSS for styling

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth0();

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Menu</h2>
        <ul>
          <li>Your Workspace</li>
          <li>Google Drive</li>
          <li>Microsoft OneDrive</li>
        </ul>
      </div>

      {/* Main content */}
      <div className="main-content">
        {isAuthenticated && (
          <div className="user-info">
            <img src={user.picture} alt="User" className="user-picture" />
            <span className="user-name">{user.name}</span>
          </div>
        )}
        <h1>Welcome to Your Dashboard</h1>
      </div>
    </div>
  );
};

export default Dashboard;
