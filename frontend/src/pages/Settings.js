import React, { useState, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { api } from '../services/api';
import { useTranslation } from 'react-i18next';

const Settings = () => {
  const { t } = useTranslation();
  const { user } = useContext(AuthContext);
  const [settings, setSettings] = useState({ twoFA: false, language: 'ru', notifications: true });

  const handleSave = async () => {
    await api.post('/api/settings/', settings);
    alert('Настройки сохранены');
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('settings')}</h1>
      <label>
        <input
          type="checkbox"
          checked={settings.twoFA}
          onChange={(e) => setSettings({ ...settings, twoFA: e.target.checked })}
        />
        2FA
      </label>
      {/* Другие настройки */}
      <button onClick={handleSave} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">Сохранить</button>
    </div>
  );
};

export default Settings;
