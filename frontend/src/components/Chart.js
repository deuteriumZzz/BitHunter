import React from 'react';
import { Line } from 'react-chartjs-2';

const Chart = ({ data }) => {
  const chartData = {
    labels: data.map(d => d.date),
    datasets: [{ label: 'Цена BTC', data: data.map(d => d.price), borderColor: 'blue' }]
  };

  return <Line data={chartData} />;
};

export default Chart;
