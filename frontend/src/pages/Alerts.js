import React, { useState } from 'react';
import { useAlerts } from '../hooks/useAlerts';
import SearchBar from '../components/SearchBar';
import SortDropdown from '../components/SortDropdown';
import { useTranslation } from 'react-i18next';

const Alerts = () => {
  const { t } = useTranslation();
  const { alerts, loading } = useAlerts();
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('date');

  const filteredAlerts = alerts.filter(alert => alert.message.includes(search)).sort((a, b) => {
    if (sort === 'date') return new Date(b.date) - new Date(a.date);
    return 0;
  });

  if (loading) return <div>{t('loading')}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('alerts')}</h1>
      <SearchBar onSearch={setSearch} />
      <SortDropdown options={[{ value: 'date', label: 'По дате' }]} onSort={(opt) => setSort(opt.value)} />
      <ul>
        {filteredAlerts.map((alert, index) => (
          <li key={index} className="border p-2 mb-2">{alert.message}</li>
        ))}
      </ul>
    </div>
  );
};

export default Alerts;
