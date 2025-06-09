import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Profile/Navbar';
import Login from './components/Login';
import Signup from './components/Signup';
import UpgradePlan from './components/Profile/UpgradePlan';
import LogOut from './components/Profile/LogOut';
import Support from './components/Profile/Support';
import Settings from './components/Profile/Settings';
import ChatBox from './components/Chatbot/ChatBox';
import './App.css'; // Make sure to import your CSS file
import { useLocation } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Navbar />
      <MainContent />
    </Router>
  );
}

function MainContent() {
  const location = useLocation();

  // Determine if the current route is one where the chat container should not be displayed
  const hideChatContainer = location.pathname === '/login' || location.pathname === '/signup';

  return (
    <div className="app-container">
      <div className="content">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/upgrade-plan" element={<UpgradePlan />} />
          <Route path="/logout" element={<LogOut />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/support" element={<Support />} />
        </Routes>
      </div>
      {!hideChatContainer && (
        <>
          <div className="vertical-line"></div> {/* Vertical line */}
          <div className="chat-container">
            <ChatBox /> {/* Render the ChatBox component ONLY in the chat-container */}
          </div>
        </>
      )}
    </div>
  );
}

export default App;