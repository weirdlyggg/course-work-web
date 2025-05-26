import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchCurrentUser } from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAdmin, setIsAdmin] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadUser = async () => {
            try {
                const response = await fetchCurrentUser();
                setUser(response.data);
                setIsAdmin(response.data.is_admin); // Предположим, что в ответе есть is_admin
                setLoading(false);
            } catch (err) {
                setUser(null);
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, isAdmin, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);