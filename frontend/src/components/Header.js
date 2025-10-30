import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { ThemeContext } from '../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';
import { useTranslation } from 'react-i18next';

const Header = () => {
  const { t } = useTranslation();
  const { user, logout } = useContext(AuthContext);
  const { darkMode } = useContext(ThemeContext);
  const navigate = useNavigate();

  return (
    <header className={`bg-blue-600 dark:bg-blue-800 text-white p-4 flex justify-between items-center ${darkMode ? 'dark' : ''}`}>
      <Link to="/" className="text-xl font-bold">{t('bithunter')}</Link>
      <div className="flex items-center space-x-4">
        <span>{t('welcome')}, {user?.username}!</span>
        <ThemeToggle />
        <button onClick={() => { logout(); navigate('/login'); }} className="bg-red-500 px-4 py-2 rounded">{t('logout')}</button>
      </div>
    </header>
  );
};

export default Header;
