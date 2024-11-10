import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Auth0 from './auth/Auth0';
import Dashboard from './components/Dashboard';
import AddLocalFile from './components/AddLocalFile';
import AddGoogleAccount from './components/AddGoogleAccount';

const App = () => {
  return (
    <Auth0>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/add-local" element={<AddLocalFile />} />
          <Route path="/add-google" element={<AddGoogleAccount />} />
        </Routes>
      </Router>
    </Auth0>
  );
};

export default App;
