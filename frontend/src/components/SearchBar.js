import React from 'react';
import { FiSearch } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const SearchBar = ({ onSearch, placeholder }) => {
  const { t } = useTranslation();

  return (
    <div className="flex items-center border rounded-lg p-2 mb-4 max-w-md">
      <FiSearch className="mr-2" />
      <input
        type="text"
        onChange={(e) => onSearch(e.target.value)}
        placeholder={placeholder || t('search')}
        className="flex-1 outline-none bg-transparent"
      />
    </div>
  );
};

export default SearchBar;
