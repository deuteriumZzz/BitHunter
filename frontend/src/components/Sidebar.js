import React from 'react';
import { Link } from 'react-router-dom';
import { FiHome, FiBell, FiBarChart, FiDollarSign, FiNews, FiSettings, FiWallet, FiMessageSquare } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const Sidebar = () => {
  const { t } = useTranslation();

  const navItems = [
    { path: '/', icon: FiHome, label: 'dashboard' },
    { path: '/alerts', icon: FiBell, label: 'alerts' },
    { path: '/analytics', icon: FiBarChart, label: 'analytics' },
    { path: '/trading', icon: FiDollarSign, label: 'trading' },
    { path: '/news', icon: FiNews, label: 'news' },
    { path: '/portfolio', icon: FiWallet, label: 'portfolio' },
    { path: '/community', icon: FiMessageSquare, label: 'community' },
    { path: '/settings', icon: FiSettings, label: 'settings' }
  ];

  return (
    <aside className="bg-gray-800 dark:bg-gray-900 text-white w-64 p-4 hidden md:block flex-shrink-0">
      <nav className="space-y-2">
        {navItems.map(({ path, icon: Icon, label }) => (
          <Link key={path} to={path} className="flex items-center p-2 rounded hover:bg-gray-700">
            <Icon className="mr-3" />
            {t(label)}
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
