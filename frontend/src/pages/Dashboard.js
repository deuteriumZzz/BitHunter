import React from 'react';
import { useTranslation } from 'react-i18next';

const Dashboard = () => {
  const { t } = useTranslation();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('dashboard')}</h1>
      <p>Обзор: баланс, активы, алерты.</p>
    </div>
  );
};

export default Dashboard;
