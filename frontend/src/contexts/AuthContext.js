import React, { createContext, useState, useEffect } from 'react';
import jwtDecode from 'jwt-decode';
import { api } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser(decoded);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/login/', { username, password });
      const { access } = response.data;
      localStorage.setItem('token', access);
      const decoded = jwtDecode(access);
      setUser(decoded);
      return true;
    } catch (error) {
      throw new Error('Неверные данные');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
