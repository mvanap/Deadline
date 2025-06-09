import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
 
  return (
    <nav className="navbar">
      {/* Home Button on the left side */}
      <Link to="/" className="navbar-button">
        Home
      </Link>
      <h1 className="navbar-heading">Welcome to the HealthBuddy</h1>
      <div className="navbar-buttons">
        <button className="navbar-button" onClick={() => navigate('/login')}>Login</button>
        <button className="navbar-button" onClick={() => navigate('/signup')}>Sign Up</button>
        <div style={{ position: 'relative' }}>
          <button className="navbar-button" onClick={() => setShowDropdown(!showDropdown)}>Profile ⏷</button>
          {showDropdown && (
            <div className="profile-dropdown">
              <Link to="/upgrade-plan"><button>Upgrade Plan</button></Link><br />
              <Link to="/settings"><button>Settings</button></Link><br />
              <Link to="/support"><button>Support</button></Link><br />
              <Link to="/logout"><button>Logout</button></Link><br />
            </div>
          )}
        </div>
      </div>
    </nav>    
  );
}
 
export default Navbar;