import React, { useState } from 'react';

const SelectDirectoryPopup = () => {
  const [directories, setDirectories] = useState([]);

  const handleSelectDirectories = async () => {
    try {
      const selectedDirectories = await window.electronAPI.selectDirectories();
      if (selectedDirectories && selectedDirectories.length > 0) {
        setDirectories(selectedDirectories);

        try {
          const response = await fetch('http://127.0.0.1:5000/LocalPaths', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filePaths: selectedDirectories })
          });

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const data = await response.json();
          alert('Directories sent to backend successfully!');
        } catch (error) {
          alert('Failed to send directories to the backend. Check the console for details.');
        }
      }
    } catch (error) {
      alert('An error occurred while selecting directories.');
    }
  };

  return (
    <div>
      <button onClick={handleSelectDirectories}>Select Directories</button>
      {directories.length > 0 && (
        <div>
          <h4>Selected Directories:</h4>
          <ul>
            {directories.map((dir, index) => (
              <li key={index}>{dir}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SelectDirectoryPopup;
