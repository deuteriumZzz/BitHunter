import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import SearchBar from '../components/SearchBar';
import SortDropdown from '../components/SortDropdown';
import { useTranslation } from 'react-i18next';

const News = () => {
  const { t } = useTranslation();
  const [news, setNews] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/api/news/').then(response => setNews(response.data));
  }, []);

  const filteredNews = news.filter(item => item.title.includes(search));

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">{t('news')}</h1>
      <SearchBar onSearch={setSearch} />
      <ul>
        {filteredNews.map((item, index) => (
          <li key={index} className="border p-2 mb-2">{item.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default News;
