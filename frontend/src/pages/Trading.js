import React from 'react';
import TradingViewWidget from 'react-tradingview-widget';
import { useTranslation } from 'react-i18next';

const Trading = () => {
  const { t } = useTranslation();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('trading')}</h1>
      <TradingViewWidget symbol="BTCUSD" />
    </div>
  );
};

export default Trading;
