import React from 'react';
import { useTranslation } from 'react-i18next';

const Analytics = () => {
  const { t } = useTranslation();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('analytics')}</h1>
      <p>Графики и статистика.</p>
    </div>
  );
};

export default Analytics;
