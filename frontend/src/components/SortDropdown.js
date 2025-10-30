import React, { useState } from 'react';
import { FiChevronDown } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const SortDropdown = ({ options, onSort }) => {
  const { t } = useTranslation();
  const [selected, setSelected] = useState(options[0]);

  const handleSort = (option) => {
    setSelected(option);
    onSort(option);
  };

  return (
    <div className="relative">
      <button className="flex items-center border rounded-lg p-2 mb-4">
        {t('sort')}: {selected.label} <FiChevronDown className="ml-2" />
      </button>
      <ul className="absolute top-full left-0 bg-white dark:bg-gray-800 border rounded shadow-md w-full">
        {options.map((option) => (
          <li
            key={option.value}
            onClick={() => handleSort(option)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
          >
            {option.label}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SortDropdown;
