import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminRoute = ({ children }) => {
    const { isAdmin, loading } = useAuth();

    if (loading) return <div>Загрузка...</div>;
    if (!isAdmin) return <Navigate to="/" />;

    return children;
};

export default AdminRoute;