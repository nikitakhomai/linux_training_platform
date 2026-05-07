import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Register = () => {
    const [formData, setFormData] = useState({ username: '', email: '', password: '', role: 'student' });
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password.length < 8) {
            alert('Password must be at least 8 characters');
            return;
        }
        setLoading(true);
        const result = await register(formData.email, formData.username, formData.password, formData.role);
        setLoading(false);
        if (result.id) {
            alert('Registration successful! Please login.');
            navigate('/login');
        } else {
            alert('Registration failed');
        }
    };

    return (
        <div className="auth-form">
            <h2>📝 Create Account</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Username" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} required />
                <input type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
                <input type="password" placeholder="Password (min 8 characters)" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} required />
                <select value={formData.role} onChange={(e) => setFormData({ ...formData, role: e.target.value })}>
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                    <option value="admin">Admin</option>
                </select>
                <button type="submit" disabled={loading}>{loading ? 'Loading...' : 'Register'}</button>
            </form>
            <div className="auth-switch">
                Already have an account? <a onClick={() => navigate('/login')}>Login</a>
            </div>
        </div>
    );
};

export default Register;
