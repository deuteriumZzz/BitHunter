import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      bithunter: 'BitHunter',
      welcome: 'Welcome',
      logout: 'Logout',
      dashboard: 'Dashboard',
      alerts: 'Alerts',
      analytics: 'Analytics',
      trading: 'Trading',
      news: 'News',
      portfolio: 'Portfolio',
      community: 'Community',
      settings: 'Settings',
      asset: 'Asset',
      balance: 'Balance',
      value: 'Value',
      export_csv: 'Export CSV',
      search: 'Search...',
      sort: 'Sort',
      send: 'Send',
      login: 'Login',
      username: 'Username',
      password: 'Password',
      register: 'Register',
      error: 'Error',
      loading: 'Loading...',
      // Добавьте остальные ключи по необходимости
    }
  },
  ru: {
    translation: {
      bithunter: 'BitHunter',
      welcome: 'Добро пожаловать',
      logout: 'Выйти',
      dashboard: 'Дашборд',
      alerts: 'Алерты',
      analytics: 'Аналитика',
      trading: 'Трейдинг',
      news: 'Новости',
      portfolio: 'Портфолио',
      community: 'Сообщество',
      settings: 'Настройки',
      asset: 'Актив',
      balance: 'Баланс',
      value: 'Стоимость',
      export_csv: 'Экспорт в CSV',
      search: 'Поиск...',
      sort: 'Сортировка',
      send: 'Отправить',
      login: 'Войти',
      username: 'Имя пользователя',
      password: 'Пароль',
      register: 'Регистрация',
      error: 'Ошибка',
      loading: 'Загрузка...',
      // Добавьте остальные ключи
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ru', // По умолчанию русский
    fallbackLng: 'en',
    interpolation: { escapeValue: false }
  });

export default i18n;
