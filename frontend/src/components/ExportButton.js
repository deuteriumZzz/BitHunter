import React from 'react';
import { exportToCSV } from '../utils/csvExporter';
import { useTranslation } from 'react-i18next';

const ExportButton = ({ data }) => {
  const { t } = useTranslation();

  const handleExport = () => {
    exportToCSV(data);
  };

  return (
    <button onClick={handleExport} className="bg-green-500 text-white px-4 py-2 rounded mb-4">
      {t('export_csv')}
    </button>
  );
};

export default ExportButton;
