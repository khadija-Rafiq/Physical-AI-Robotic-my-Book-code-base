import React, { useState } from 'react';
import ChatInterface from '../components/ChatInterface';

export default function Root({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {children}

      {/* Floating Button */}
      <button
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: '#2e8555',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          fontSize: '24px',
          boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
          zIndex: 9999,
        }}
        onClick={() => setOpen(!open)}
      >
        💬
      </button>

      {/* Chat Window */}
      {open && (
        <div
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            width: '380px',
            height: '500px',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
            zIndex: 9999,
            overflow: 'hidden'
          }}
        >
          <ChatInterface apiUrl="http://localhost:8000" />
        </div>
      )}
    </>
  );
}
