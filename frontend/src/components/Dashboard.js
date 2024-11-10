import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import './Dashboard.css';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth0();

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Fileppe</h2>
        <div className="account-section">
          <h3>Google</h3>
          <ul>
            <li>acct1</li>
            <li>acct2</li>
          </ul>
        </div>
        <div className="sidebar-buttons">
          <button className="add-button">ADD</button>
          <button className="delete-button">DEL</button>
        </div>
      </div>

      {/* Main workspace */}
      <div className="workspace">
        <h2>Your Workspace</h2>
        <div className="folder-grid">
          <div className="folder-item"></div>
          <div className="folder-item"></div>
        </div>
      </div>

      {/* User info */}
      <div className="user-info">
        {isAuthenticated ? (
          <>
            <img src={user.picture} alt="User" className="user-picture" />
            <span>{user.name}</span>
            <LogoutButton />
          </>
        ) : (
          <LoginButton />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
