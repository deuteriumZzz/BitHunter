import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';

function Analytics() {
    const [prediction, setPrediction] = useState(null);
    const [chartData, setChartData] = useState({});

    const predict = () => {
        axios.post('http://localhost:8000/analytics/predict/', { symbol: 'BTC/USDT' }).then(res => {
            setPrediction(res.data.prediction);
            // Пример данных для графика
            setChartData({
                labels: ['Jan', 'Feb', 'Mar'],
                datasets: [{ label: 'Price', data: [100, 200, res.data.prediction] }]
            });
        });
    };

    return (
        <div>
            <h2>Analytics</h2>
            <button onClick={predict}>Predict Price</button>
            {prediction && <p>Prediction: {prediction}</p>}
            <Line data={chartData} />
        </div>
    );
}

export default Analytics;
