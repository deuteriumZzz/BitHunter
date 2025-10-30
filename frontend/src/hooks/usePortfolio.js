import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const usePortfolio = () => {
  const [portfolio, setPortfolio] = useState({ assets: [], balance: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await api.get('/api/portfolio/');
        setPortfolio(response.data);
      } catch (error) {
        console.error('Ошибка загрузки портфолио:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPortfolio();
  }, []);

  return { portfolio, loading };
};
