// import React, { useState, useRef, useEffect } from 'react';
// import './ChatInterface.css';

// interface Message {
//   id: string;
//   content: string;
//   role: 'user' | 'assistant';
//   timestamp: Date;
// }

// interface ChatInterfaceProps {
//   apiUrl?: string; // Optional API URL, defaults to localhost:8000
// }

// const ChatInterface: React.FC<ChatInterfaceProps> = ({ apiUrl = 'http://localhost:8000' }) => {
//   const [messages, setMessages] = useState<Message[]>([
//     {
//       id: '1',
//       content: 'Hello! I\'m your Physical AI & Humanoid Robotics assistant. Ask me anything about the book content!',
//       role: 'assistant',
//       timestamp: new Date(),
//     }
//   ]);
//   const [inputValue, setInputValue] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [selectedText, setSelectedText] = useState('');
//   const messagesEndRef = useRef<HTMLDivElement>(null);
//   const textareaRef = useRef<HTMLTextAreaElement>(null);

//   // Auto-scroll to bottom when messages change
//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   // Handle text selection
//   useEffect(() => {
//     const handleSelection = () => {
//       const selection = window.getSelection();
//       if (selection && selection.toString().trim() !== '') {
//         setSelectedText(selection.toString().trim());
//       }
//     };

//     document.addEventListener('mouseup', handleSelection);
//     return () => {
//       document.removeEventListener('mouseup', handleSelection);
//     };
//   }, []);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   const handleSendMessage = async () => {
//     if (!inputValue.trim() || isLoading) return;

//     // Log the frontend → backend flow initiation
//     console.log('[FRONTEND_LOG] Sending question to backend:', {
//       question: inputValue,
//       context: selectedText,
//       timestamp: new Date().toISOString()
//     });

//     // Add user message
//     const userMessage: Message = {
//       id: Date.now().toString(),
//       content: inputValue,
//       role: 'user',
//       timestamp: new Date(),
//     };

//     setMessages(prev => [...prev, userMessage]);
//     setInputValue('');
//     setIsLoading(true);

//     try {
//       // Prepare context if there's selected text
//       let question = inputValue;
//       if (selectedText) {
//         question = `Context: ${selectedText}\n\nQuestion: ${inputValue}`;
//         console.log('[FRONTEND_LOG] Using selected text as context:', selectedText);
//       }

//       // Validate API URL
//       let validatedApiUrl = apiUrl;
//       if (!validatedApiUrl.startsWith('http')) {
//         validatedApiUrl = `http://${validatedApiUrl}`;
//       }

//       // Call the backend API
//       const startTime = Date.now();
//       console.log('[FRONTEND_LOG] Initiating API request to:', validatedApiUrl);

//       const response = await fetch(`${validatedApiUrl}/query`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           query: question,
//           top_k: 5,
          
//         }),
//       });

//       const responseTime = Date.now() - startTime;
//       console.log('[FRONTEND_LOG] API response received:', {
//         status: response.status,
//         responseTime: `${responseTime}ms`,
//         timestamp: new Date().toISOString()
//       });

//       if (!response.ok) {
//         const errorText = await response.text();
//         console.error('[BACKEND_ERROR] API request failed:', {
//           status: response.status,
//           statusText: response.statusText,
//           errorBody: errorText,
//           url: `${validatedApiUrl}/ask`
//         });

//         throw new Error(`API request failed with status ${response.status}: ${response.statusText}. Details: ${errorText}`);
//       }

//       const data = await response.json();
//       console.log('[BACKEND_RESPONSE] Raw response data:', data);

//       // Log the backend → retrieval → answer flow completion
//       console.log('[FRONTEND_LOG] Answer received from backend:', {
//         answerLength: data.answer?.length || 0,
//         hasReferences: !!data.references,
//         timestamp: new Date().toISOString()
//       });

//       // Validate response data
//       if (!data || typeof data.answer !== 'string') {
//         console.warn('[FRONTEND_WARN] Invalid response format received from backend:', data);
//         throw new Error('Invalid response format from backend');
//       }

//       // Add assistant response
//       const assistantMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         content: data.answer,
//         role: 'assistant',
//         timestamp: new Date(),
//       };

//       setMessages(prev => [...prev, assistantMessage]);
//     } catch (error) {
//       console.error('[FRONTEND_ERROR] Error in question-answer flow:', {
//         error: error instanceof Error ? error.message : String(error),
//         stack: error instanceof Error ? error.stack : null,
//         inputValue,
//         selectedText,
//         timestamp: new Date().toISOString()
//       });

//       // Determine appropriate error message based on error type
//       let errorMessageText = 'Sorry, I encountered an error while processing your question. Please try again.';

//       if (error instanceof TypeError && error.message.includes('fetch')) {
//         errorMessageText = 'Network error: Unable to connect to the backend service. Please check if the RAG agent is running at ' + apiUrl;
//       } else if (error instanceof Error && error.message.includes('404')) {
//         errorMessageText = 'Backend endpoint not found. Please ensure the RAG agent is properly configured and running.';
//       } else if (error instanceof Error && error.message.includes('400')) {
//         errorMessageText = 'Invalid request sent to the backend. Please try rephrasing your question.';
//       } else if (error instanceof Error && error.message.includes('500')) {
//         errorMessageText = 'Backend server error occurred. Please try again later.';
//       }

//       const errorMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         content: errorMessageText,
//         role: 'assistant',
//         timestamp: new Date(),
//       };

//       setMessages(prev => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//       setSelectedText('');
//       console.log('[FRONTEND_LOG] Question-answer cycle completed', {
//         timestamp: new Date().toISOString(),
//         duration: `${Date.now() - parseInt(userMessage.id)}ms`
//       });
//     }
//   };

//   const handleKeyDown = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSendMessage();
//     }
//   };

//   const handleUseSelectedText = () => {
//     if (selectedText) {
//       setInputValue(prev => prev ? `${prev} [Context: ${selectedText}]` : selectedText);
//       setSelectedText('');
//     }
//   };

//   return (
//     <div className="chat-interface">
//       <div className="chat-header">
//         <h3>Physical AI & Robotics Assistant</h3>
//         <div className="header-info">
//           {selectedText && (
//             <button
//               className="use-context-btn"
//               onClick={handleUseSelectedText}
//               title="Use selected text as context"
//             >
//               📝 Use Selected Text
//             </button>
//           )}
//         </div>
//       </div>

//       <div className="chat-messages">
//         {messages.map((message) => (
//           <div
//             key={message.id}
//             className={`message ${message.role}`}
//             title={message.timestamp.toLocaleTimeString()}
//           >
//             <div className="message-content">
//               {message.content}
//             </div>
//             <div className="message-timestamp">
//               {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
//             </div>
//           </div>
//         ))}
//         {isLoading && (
//           <div className="message assistant">
//             <div className="message-content">
//               <div className="typing-indicator">
//                 <div className="typing-dot"></div>
//                 <div className="typing-dot"></div>
//                 <div className="typing-dot"></div>
//               </div>
//             </div>
//           </div>
//         )}
//         <div ref={messagesEndRef} />
//       </div>

//       <div className="chat-input-area">
//         {selectedText && (
//           <div className="selected-text-preview">
//             <span className="selected-label">Context:</span> {selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}
//             <button
//               className="clear-context-btn"
//               onClick={() => setSelectedText('')}
//             >
//               ×
//             </button>
//           </div>
//         )}
//         <div className="input-container">
//           <textarea
//             ref={textareaRef}
//             value={inputValue}
//             onChange={(e) => setInputValue(e.target.value)}
//             onKeyDown={handleKeyDown}
//             placeholder="Ask a question about Physical AI & Robotics..."
//             disabled={isLoading}
//             rows={2}
//           />
//           <button
//             className="send-button"
//             onClick={handleSendMessage}
//             disabled={isLoading || !inputValue.trim()}
//           >
//             {isLoading ? 'Sending...' : 'Send'}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatInterface;


















import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatInterfaceProps {
  apiUrl?: string; // Optional API URL, defaults to localhost:8000
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ apiUrl = 'https://my-backend-ruby-eta.vercel.app' }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your Physical AI & Humanoid Robotics assistant. Ask me anything about the book content!',
      role: 'assistant',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim() !== '') {
        setSelectedText(selection.toString().trim());
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    console.log('[FRONTEND_LOG] Sending question to backend:', {
      question: inputValue,
      context: selectedText,
      timestamp: new Date().toISOString()
    });

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let question = inputValue;
      if (selectedText) {
        question = `Context: ${selectedText}\n\nQuestion: ${inputValue}`;
        console.log('[FRONTEND_LOG] Using selected text as context:', selectedText);
      }

      let validatedApiUrl = apiUrl;
      if (!validatedApiUrl.startsWith('http')) {
        validatedApiUrl = `http://${validatedApiUrl}`;
      }

      const startTime = Date.now();
      console.log('[FRONTEND_LOG] Initiating API request to:', validatedApiUrl);

      const response = await fetch(`${validatedApiUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question, top_k: 5 }),
      });

      const responseTime = Date.now() - startTime;
      console.log('[FRONTEND_LOG] API response received:', {
        status: response.status,
        responseTime: `${responseTime}ms`,
        timestamp: new Date().toISOString()
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[BACKEND_ERROR] API request failed:', {
          status: response.status,
          statusText: response.statusText,
          errorBody: errorText,
          url: `${validatedApiUrl}/query`
        });
        throw new Error(`API request failed with status ${response.status}: ${response.statusText}. Details: ${errorText}`);
      }

      const data = await response.json();
      console.log('[BACKEND_RESPONSE] Raw response data:', data);

      // --- FIXED BLOCK: Use `results` array from backend ---
      if (!data || !Array.isArray(data.results)) {
        throw new Error('Invalid response format from backend');
      }

      const combinedAnswer = data.results
        .map((r: any, i: number) => `(${i + 1}) ${r.text}`)
        .join('\n\n');

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: combinedAnswer || 'No relevant answer found.',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('[FRONTEND_ERROR] Error in question-answer flow:', {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : null,
        inputValue,
        selectedText,
        timestamp: new Date().toISOString()
      });

      let errorMessageText = 'Sorry, I encountered an error while processing your question. Please try again.';
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessageText = 'Network error: Unable to connect to the backend service. Please check if the RAG agent is running at ' + apiUrl;
      } else if (error instanceof Error && error.message.includes('404')) {
        errorMessageText = 'Backend endpoint not found. Please ensure the RAG agent is properly configured and running.';
      } else if (error instanceof Error && error.message.includes('400')) {
        errorMessageText = 'Invalid request sent to the backend. Please try rephrasing your question.';
      } else if (error instanceof Error && error.message.includes('500')) {
        errorMessageText = 'Backend server error occurred. Please try again later.';
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessageText,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText('');
      console.log('[FRONTEND_LOG] Question-answer cycle completed', {
        timestamp: new Date().toISOString(),
        duration: `${Date.now() - parseInt(userMessage.id)}ms`
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUseSelectedText = () => {
    if (selectedText) {
      setInputValue(prev => prev ? `${prev} [Context: ${selectedText}]` : selectedText);
      setSelectedText('');
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Physical AI & Robotics Assistant</h3>
        <div className="header-info">
          {selectedText && (
            <button
              className="use-context-btn"
              onClick={handleUseSelectedText}
              title="Use selected text as context"
            >
              📝 Use Selected Text
            </button>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.role}`}
            title={message.timestamp.toLocaleTimeString()}
          >
            <div className="message-content">{message.content}</div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {selectedText && (
          <div className="selected-text-preview">
            <span className="selected-label">Context:</span> {selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}
            <button className="clear-context-btn" onClick={() => setSelectedText('')}>×</button>
          </div>
        )}
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about Physical AI & Robotics..."
            disabled={isLoading}
            rows={2}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;






