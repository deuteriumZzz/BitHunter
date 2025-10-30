import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

const Login = () => {
  const { t } = useTranslation();
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ username: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(credentials.username, credentials.password);
      navigate('/');
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-6 rounded shadow-md">
        <h2 className="text-xl mb-4">{t('login')}</h2>
        <input
          type="text"
          placeholder={t('username')}
          value={credentials.username}
          onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
          className="w-full p-2 mb-2 border"
          required
        />
        <input
          type="password"
          placeholder={t('password')}
          value={credentials.password}
          onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
          className="w-full p-2 mb-4 border"
          required
        />
        <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">{t('login')}</button>
      </form>
    </div>
  );
};

export default Login;
