import React from 'react';
import ChatComponent from '../components/ChatComponent';
import { useTranslation } from 'react-i18next';

const Community = () => {
  const { t } = useTranslation();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('community')}</h1>
      <ChatComponent />
    </div>
  );
};

export default Community;
