import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
 
  return (
    <nav className="navbar">
    <h2 className="navbar-logo" onClick={() => navigate('/')}>Welcome to HealthBuddy</h2>
    <div className="navbar-buttons">
    <button className="navbar-button" onClick={() => navigate('/login')}>Login</button>
    <button className="navbar-button" onClick={() => navigate('/signup')}>Sign Up</button>
    <div style={{ position: 'relative' }}>
    <button className="navbar-button" onClick={() => setShowDropdown(!showDropdown)}>Profile ⏷</button>
    
          {showDropdown && (
    <div className="profile-dropdown">
    <p onClick={() => alert('Upgrade Plan')}>Upgrade Plan</p>
    <p onClick={() => alert('Settings')}>Settings</p>
    <p onClick={() => alert('Logged Out')}>Logout</p>
    </div>
    
          )}
    </div>
    </div>
    </nav>    
  );
}
 
export default Navbar;