import React, { useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../contexts/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/accounts/login/', { username, password });
      login(res.data.access);
    } catch (err) {
      alert('Ошибка входа');
    }
  };

  return (
    <div className="flex justify-center items-center h-full">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow">
        <h2 className="text-2xl mb-4">Вход</h2>
        <input type="text" placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} className="block w-full p-2 mb-2 border" />
        <input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} className="block w-full p-2 mb-2 border" />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Войти</button>
      </form>
    </div>
  );
};

export default Login;
