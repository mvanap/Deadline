import React from 'react';
import { Navigate } from 'react-router-dom';

const Logout = () => {
    // Perform any logout logic here (e.g., clearing user data, tokens, etc.)
    
    // Redirect to the home page
    return <Navigate to="/" replace />;
};

export default Logout;