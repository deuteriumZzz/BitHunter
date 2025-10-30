import React, { useContext } from 'react';
import { usePortfolio } from '../hooks/usePortfolio';
import ExportButton from './ExportButton';
import { useTranslation } from 'react-i18next';
import { NotificationContext } from '../contexts/NotificationContext';

const PortfolioTable = () => {
  const { t } = useTranslation();
  const { portfolio, loading } = usePortfolio();
  const { showNotification } = useContext(NotificationContext);

  if (loading) return <div>{t('loading')}</div>;

  const data = portfolio.assets.map(asset => ({ asset: asset.name, balance: asset.balance, value: asset.value }));

  return (
    <div>
      <ExportButton data={data} />
      <table className="w-full table-auto border-collapse border">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-800">
            <th className="border p-2">{t('asset')}</th>
            <th className="border p-2">{t('balance')}</th>
            <th className="border p-2">{t('value')}</th>
          </tr>
        </thead>
        <tbody>
          {portfolio.assets.map((asset, index) => (
            <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="border p-2">{asset.name}</td>
              <td className="border p-2">{asset.balance}</td>
              <td className="border p-2">{asset.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PortfolioTable;
