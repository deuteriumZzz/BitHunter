import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { AuthContext } from './contexts/AuthContext';
import NavBar from './components/NavBar';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import Trading from './components/Trading';
import Analytics from './components/Analytics';
import Alerts from './components/Alerts';

function App() {
    const { user } = useContext(AuthContext);

    const ProtectedRoute = ({ children }) => {
        return user ? children : <Navigate to="/login" />;
    };

    return (
        <Router>
            <NavBar />
            <Routes>
                <Route path="/" element={<Navigate to="/trading" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                <Route path="/trading" element={<ProtectedRoute><Trading /></ProtectedRoute>} />
                <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
                <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
            </Routes>
        </Router>
    );
}

export default App;
