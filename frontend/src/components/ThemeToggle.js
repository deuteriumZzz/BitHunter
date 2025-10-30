import React, { useContext } from 'react';
import { ThemeContext } from '../contexts/ThemeContext';
import { FiSun, FiMoon } from 'react-icons/fi';

const ThemeToggle = () => {
  const { darkMode, toggleTheme } = useContext(ThemeContext);

  return (
    <button onClick={toggleTheme} className="p-2 rounded-full bg-gray-200 dark:bg-gray-700">
      {darkMode ? <FiSun /> : <FiMoon />}
    </button>
  );
};

export default ThemeToggle;
