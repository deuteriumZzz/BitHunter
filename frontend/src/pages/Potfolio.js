import React from 'react';
import PortfolioTable from '../components/PortfolioTable';
import { useTranslation } from 'react-i18next';

const Portfolio = () => {
  const { t } = useTranslation();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('portfolio')}</h1>
      <PortfolioTable />
    </div>
  );
};

export default Portfolio;
