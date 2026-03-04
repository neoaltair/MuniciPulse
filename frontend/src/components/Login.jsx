import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../utils/api';
import { setToken, getDecodedToken } from '../utils/auth';
import './Auth.css';

function Login() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        setError(''); // Clear error on input change
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await authAPI.login(formData);
            const token = response.data.access_token;

            // Store token in localStorage
            setToken(token);

            // Decode token to get role
            const decoded = getDecodedToken();
            const role = decoded.role;

            // Redirect based on role
            if (role === 'municipal_officer') {
                navigate('/admin/dashboard');
            } else if (role === 'citizen') {
                navigate('/my-reports');
            } else {
                navigate('/');
            }
        } catch (err) {
            // Handle different error response formats
            let errorMessage = 'Login failed. Please check your credentials.';

            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;

                // Check if detail is an array of validation errors
                if (Array.isArray(detail)) {
                    // Extract and format validation error messages
                    errorMessage = detail.map(e => e.msg || JSON.stringify(e)).join(', ');
                } else if (typeof detail === 'string') {
                    // Detail is a simple string message
                    errorMessage = detail;
                } else {
                    // Detail is an object, try to extract message
                    errorMessage = detail.msg || detail.message || JSON.stringify(detail);
                }
            }

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1 className="auth-title">CivicFix Login</h1>
                <p className="auth-subtitle">Sign in to report civic issues</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            placeholder="Your username"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <p className="auth-footer">
                    Don't have an account? <Link to="/signup">Sign up here</Link>
                </p>
            </div>
        </div>
    );
}

export default Login;
