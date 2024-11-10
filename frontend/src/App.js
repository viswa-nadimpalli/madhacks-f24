import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Auth0 from './auth/Auth0';
import Dashboard from './components/Dashboard';

const App = () => {
  return (
    <Auth0>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </Router>
    </Auth0>
  );
};

export default App;
