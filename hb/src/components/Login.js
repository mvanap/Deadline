import './Login.css';

function Login() {
    return (
    <div className="login-page">
        <h2>Login</h2>
        <form>
            <input type="email" placeholder="Email" /><br />
            <input type="password" placeholder="Password" /><br />
            <button type="submit">Login</button>
        </form>
    </div>
   );
}

export default Login;