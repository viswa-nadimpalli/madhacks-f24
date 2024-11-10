import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Auth0Provider from './auth/Auth0Provider';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Auth0Provider>
      <Router>
        <Dashboard />
      </Router>
    </Auth0Provider>
  );
}

export default App;
