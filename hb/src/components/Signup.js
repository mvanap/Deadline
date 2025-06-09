import './Signup.css';

function Signup() {
    return (
    <div className="signup-page">
        <h2>Sign Up</h2>
        <form>
            <input type="text" placeholder="Name" /><br />
            <input type="email" placeholder="Email" /><br />
            <input type="password" placeholder="Create Password" /><br />
            <input type="password" placeholder="Re-Enter Password" /><br />
            <input type="date" placeholder='Date of Birth' /><br />
            <button type="submit">Sign Up</button>
        </form>
    </div>
    );
}

export default Signup;