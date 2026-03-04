import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../utils/api';
import { setToken, getDecodedToken } from '../utils/auth';
import './Auth.css';

function Signup() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        role: 'citizen', // Default to citizen
        phone_number: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // Validate password match
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        // Validate password length
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            setLoading(false);
            return;
        }

        try {
            // Register user
            const registerData = {
                username: formData.username,
                email: formData.email || null,
                password: formData.password,
                role: formData.role,
                first_name: formData.first_name,
                last_name: formData.last_name,
                phone_number: formData.phone_number || null,
            };

            await authAPI.register(registerData);

            // Auto-login after registration
            const loginResponse = await authAPI.login({
                username: formData.username,
                password: formData.password,
            });

            const token = loginResponse.data.access_token;
            setToken(token);

            // Decode token and redirect based on role
            const decoded = getDecodedToken();
            const role = decoded.role;

            if (role === 'municipal_officer') {
                navigate('/admin/dashboard');
            } else if (role === 'citizen') {
                navigate('/my-reports');
            } else {
                navigate('/');
            }
        } catch (err) {
            // Handle different error response formats
            let errorMessage = 'Registration failed. Please try again.';

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
                <h1 className="auth-title">Create Account</h1>
                <p className="auth-subtitle">Join CivicFix to report civic issues</p>

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
                            placeholder="Choose a username"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="first_name">First Name</label>
                            <input
                                type="text"
                                id="first_name"
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                                required
                                placeholder="John"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="last_name">Last Name</label>
                            <input
                                type="text"
                                id="last_name"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                                required
                                placeholder="Doe"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email (Optional)</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="your.email@example.com"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="phone_number">Phone Number (Optional)</label>
                        <input
                            type="tel"
                            id="phone_number"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleChange}
                            placeholder="+1234567890"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="role">I am a</label>
                        <select
                            id="role"
                            name="role"
                            value={formData.role}
                            onChange={handleChange}
                            required
                            disabled={loading}
                        >
                            <option value="citizen">Citizen</option>
                            <option value="municipal_officer">Municipal Officer</option>
                        </select>
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
                            placeholder="Minimum 8 characters"
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            placeholder="Re-enter your password"
                            disabled={loading}
                        />
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Creating account...' : 'Sign Up'}
                    </button>
                </form>

                <p className="auth-footer">
                    Already have an account? <Link to="/login">Sign in here</Link>
                </p>
            </div>
        </div>
    );
}

export default Signup;
