import React, { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth0();
  const navigate = useNavigate();
  const [linkedGoogleAccounts, setLinkedGoogleAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch linked Google accounts
    const fetchAccounts = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/listAccounts');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.accounts) {
            setLinkedGoogleAccounts(data.accounts);
          } else {
            console.error('No accounts found or invalid response:', data);
            setLinkedGoogleAccounts([]);
          }
        } else {
          console.error('Failed to fetch linked accounts with status:', response.status);
          setError('Failed to fetch linked accounts.');
        }
      } catch (error) {
        console.error('Error fetching accounts:', error);
        setError('Error fetching accounts.');
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Fileppe</h2>

        {/* Google Accounts Section */}
        <div className="account-section">
          <h3>Google Accounts</h3>
          {loading ? (
            <p>Loading accounts...</p>
          ) : error ? (
            <p>{error}</p>
          ) : (
            <ul>
              {linkedGoogleAccounts.length > 0 ? (
                linkedGoogleAccounts.map((account, index) => (
                  <li key={index}>{account}</li>
                ))
              ) : (
                <li>No accounts linked</li>
              )}
            </ul>
          )}
        </div>
        <div className="sidebar-buttons">
          <button
            className="add-button"
            onClick={() => navigate('/add-local')}
          >
            ADD LOCAL
          </button>
          <button
            className="add-button"
            onClick={() => navigate('/add-google')}
          >
            ADD GOOGLE
          </button>
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
