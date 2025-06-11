import React, { useState, useRef } from 'react';
import './ChatBox.css';
 
const ChatBox = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]); // Track messages in the conversation
    const inputRef = useRef(null); // Reference to the contenteditable div
 
    // Mark handleSend as async so we can use await inside it
    const handleSend = async () => {
        if (!message.trim()) return; // Avoid sending empty messages
   
        // Add user's message to the chat
        setMessages(prevMessages => [...prevMessages, { role: 'user', content: message }]);
        setMessage(''); // Clear the input field
        if (inputRef.current) {
            inputRef.current.innerText = ''; // Clear contenteditable div
        }
   
        // Show a typing indicator before receiving the response
        setMessages(prevMessages => [
            ...prevMessages,
            { role: 'assistant', content: "HealthBuddy is typing..." }
        ]);
   
        // Send the message to the backend
        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
           
            const data = await response.json();
            console.log("Backend response:", data);  // Log the response to check the structure
 
            // Check for the correct response structure
            if (data.You && data.HealthBuddy) {
                setMessages(prevMessages => [
                    ...prevMessages.slice(0, -1),  // Remove the typing indicator
                    { role: 'assistant', content: data.HealthBuddy }
                ]);
            } else {
                setMessages(prevMessages => [
                    ...prevMessages.slice(0, -1),  // Remove the typing indicator
                    { role: 'assistant', content: "Sorry, I didn't understand that." }
                ]);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prevMessages => [
                ...prevMessages.slice(0, -1),  // Remove the typing indicator
                { role: 'assistant', content: "Something went wrong, please try again later." }
            ]);
        }
    };      
 
    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
   
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (fileExtension !== 'pdf') {
            setMessages(prevMessages => [
                ...prevMessages,
                { role: 'assistant', content: '❌ The files uploaded are not supported.' }
            ]);
            return;
        }
   
        const formData = new FormData();
        formData.append('file', file);
   
        try {
            const res = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData
            });
   
            const data = await res.json();
            console.log("Upload response:", data);
   
            // Show upload success message
            setMessages(prevMessages => [
                ...prevMessages,
                { role: 'assistant', content: '✅ File uploaded' }
            ]);
           
   
            // ✅ Automatically ask for a summary
            const summaryRes = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: `Give a summary of the uploaded file ${file.name}` })
            });
   
            const summaryData = await summaryRes.json();
            console.log("Summary response:", summaryData);
   
            setMessages(prevMessages => [
                ...prevMessages,
                { role: 'assistant', content: summaryData.HealthBuddy || "Summary not available." }
            ]);
   
        } catch (err) {
            console.error('Upload error:', err);
            setMessages(prevMessages => [
                ...prevMessages,
                { role: 'assistant', content: '❌ Upload failed. Please try again.' }
            ]);
        }
    };
   
   
    const handleInputChange = () => {
        if (inputRef.current) {
            const text = inputRef.current.innerText;
            setMessage(text);
        }
    };
 
    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent default behavior of Enter key
            handleSend(); // Send the message
        }
    };
 
    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.length === 0 ? (
                    <p className="placeholder">Chat messages will appear here...</p>
                ) : (
                    messages.map((msg, index) => (
                        <p key={index} className={msg.role === 'user' ? 'user-message' : 'assistant-message'}>
                            <strong>{msg.role === 'user' ? 'You' : 'HealthBuddy'}:</strong> {msg.content}
                        </p>
                    ))
                )}
            </div>
            <div className="chat-input-area">
                <div
                    ref={inputRef}
                    contentEditable
                    onInput={handleInputChange}
                    onKeyDown={handleKeyDown}
                    className="chat-input"
                    style={{ minHeight: '40px', border: '1px solid #ccc', padding: '8px', borderRadius: '4px' }}
                    suppressContentEditableWarning={true}
                >              
                    {message === '' && <span style={{ color: '#aaa' }}>Type your message...</span>}
                </div>    
               
                {/* File Upload Input (hidden) */}
                <input
                    type="file"
                    id="fileInput"
                    style={{ display: 'none' }}
                    onChange={handleUpload}
                />
                <label htmlFor="fileInput" className="upload-btn">Upload</label>
                <button onClick={handleSend} className="send-btn">Send</button>
            </div>
        </div>
    );
};
 
export default ChatBox;