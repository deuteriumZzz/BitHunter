import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { socket } from '../services/socket';

export const useAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await api.get('/api/alerts/');
        setAlerts(response.data);
      } catch (error) {
        console.error('Ошибка загрузки алертов:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();

    socket.on('alert_update', (newAlert) => {
      setAlerts((prev) => [newAlert, ...prev]);
    });

    return () => socket.off('alert_update');
  }, []);

  return { alerts, loading };
};
