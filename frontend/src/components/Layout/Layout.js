import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Layout = ({ children }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="container">
            <div className="header">
                <h1 onClick={() => navigate('/tasks')} style={{ cursor: 'pointer' }}>🐧 Linux Security Training Platform</h1>
                <div className="user-info">
                    <span>👤 {user?.username}</span>
                    <span className={`user-role role-${user?.role}`}>{user?.role}</span>
                    <button className="logout-btn" onClick={logout}>Logout</button>
                </div>
            </div>
            <div className="tabs">
                <button className="tab active" onClick={() => navigate('/tasks')}>📚 Tasks</button>
                {user?.role === 'admin' && (
                    <button className="tab" onClick={() => navigate('/admin')}>⚙️ Admin Panel</button>
                )}
            </div>
            <main>{children}</main>
        </div>
    );
};

export default Layout;
