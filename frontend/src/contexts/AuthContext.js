import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));

    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // Загрузить профиль пользователя
            axios.get('/api/accounts/profile/').then(res => setUser(res.data)).catch(() => setToken(null));
        }
    }, [token]);

    const login = async (credentials) => {
        const res = await axios.post('/api/accounts/login/', credentials);
        setToken(res.data.access);
        localStorage.setItem('token', res.data.access);
        setUser(res.data.user);
    };

    const register = async (data) => {
        await axios.post('/api/accounts/register/', data);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
