import React, { useState } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, Alert, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

function Analytics() {
    const [prediction, setPrediction] = useState(null);
    const [chartData, setChartData] = useState({});
    const [error, setError] = useState('');

    const handlePredict = async (values) => {
        try {
            const res = await axios.post('/api/analytics/predict/', values);
            setPrediction(res.data.prediction);
            setChartData({
                labels: ['Day 1', 'Day 2', 'Day 3', 'Prediction'],
                datasets: [{ label: 'Price', data: [100, 150, 200, res.data.prediction], borderColor: 'rgba(75,192,192,1)' }]
            });
        } catch (err) {
            setError('Prediction failed');
        }
    };

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Analytics</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Formik initialValues={{ symbol: 'BTC/USDT', timeframe: '1d' }} validationSchema={Yup.object({ symbol: Yup.string().required() })} onSubmit={handlePredict}>
                <Form>
                    <Field name="symbol" as={TextField} label="Symbol" fullWidth margin="normal" />
                    <FormControl fullWidth margin="normal">
                        <InputLabel>Timeframe</InputLabel>
                        <Field name="timeframe" as={Select}>
                            <MenuItem value="1m">1 Minute</MenuItem>
                            <MenuItem value="1h">1 Hour</MenuItem>
                            <MenuItem value="1d">1 Day</MenuItem>
                        </Field>
                    </FormControl>
                    <Button type="submit" variant="contained">Predict</Button>
                </Form>
            </Formik>
            {prediction && <Typography>Predicted Price: {prediction}</Typography>}
            <Line data={chartData} />
        </Box>
    );
}

export default Analytics;
