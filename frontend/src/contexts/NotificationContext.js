import React, { createContext, useContext } from 'react';
import { toast } from 'react-toastify';
import { AuthContext } from './AuthContext';
import { api } from '../services/api';

export const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const { user } = useContext(AuthContext);

  const showNotification = (message, type = 'info') => {
    toast[type](message, { position: 'top-right' });
  };

  const fetchNotifications = async () => {
    if (!user) return;
    try {
      const response = await api.get('/api/notifications/');
      // Обработайте данные и покажите уведомления
      showNotification('Новые уведомления загружены!');
    } catch (error) {
      showNotification('Ошибка загрузки уведомлений', 'error');
    }
  };

  return (
    <NotificationContext.Provider value={{ showNotification, fetchNotifications }}>
      {children}
    </NotificationContext.Provider>
  );
};
