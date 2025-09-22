import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../services/config';

const ConnectionTest = () => {
  const [status, setStatus] = useState('Testing...');
  const [error, setError] = useState(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        setStatus('Testing connection...');
        const response = await fetch(`${API_BASE_URL}/api/health`);
        
        if (response.ok) {
          const data = await response.json();
          setStatus(`Connected! Backend status: ${data.status}`);
          setError(null);
        } else {
          setStatus('Connection failed');
          setError(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (err) {
        setStatus('Connection failed');
        setError(err.message);
      }
    };

    testConnection();
  }, []);

  const testChatAPI = async () => {
    try {
      setStatus('Testing chat API...');
      const response = await fetch(`${API_BASE_URL}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: 'test' })
      });
      
      if (response.ok) {
        const data = await response.json();
        setStatus('Chat API working!');
        setError(null);
        console.log('Chat API response:', data);
      } else {
        setStatus('Chat API failed');
        setError(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      setStatus('Chat API failed');
      setError(err.message);
    }
  };

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold mb-2">Connection Test</h3>
      <p className="text-sm mb-2">Status: {status}</p>
      {error && (
        <p className="text-sm text-red-600 mb-2">Error: {error}</p>
      )}
      <button
        onClick={testChatAPI}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Test Chat API
      </button>
    </div>
  );
};

export default ConnectionTest; 