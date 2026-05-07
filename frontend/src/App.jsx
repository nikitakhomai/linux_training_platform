import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import TaskList from './components/Tasks/TaskList';
import AdminPanel from './components/Admin/AdminPanel';

const PrivateRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="form-card">Loading...</div>;
    if (!user) return <Navigate to="/login" />;
    return children;
};

const AdminRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="form-card">Loading...</div>;
    if (!user || user.role !== 'admin') return <Navigate to="/tasks" />;
    return children;
};

const TeacherOrAdminRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="form-card">Loading...</div>;
    if (!user || (user.role !== 'admin' && user.role !== 'teacher')) return <Navigate to="/tasks" />;
    return children;
};

function AppRoutes() {
    const { user } = useAuth();

    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Navigate to="/tasks" />} />
            <Route path="/tasks" element={
                <PrivateRoute>
                    <Layout>
                        <TaskList />
                    </Layout>
                </PrivateRoute>
            } />
            <Route path="/admin" element={
                <AdminRoute>
                    <Layout>
                        <AdminPanel />
                    </Layout>
                </AdminRoute>
            } />
        </Routes>
    );
}

function App() {
    return (
        <AuthProvider>
            <Toaster position="top-right" />
            <AppRoutes />
        </AuthProvider>
    );
}

export default App;
