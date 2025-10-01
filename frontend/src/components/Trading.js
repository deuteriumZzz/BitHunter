import React, { useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, List, ListItem, ListItemText, Alert, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import axios from 'axios';

function Trading() {
    const [strategies, setStrategies] = useState([]);
    const [trades, setTrades] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('/api/trading/').then(res => setStrategies(res.data)).catch(() => setError('Failed to load strategies'));
        axios.get('/api/trading/trades/').then(res => setTrades(res.data)).catch(() => setError('Failed to load trades'));
    }, []);

    const handleStartBot = async (id) => {
        try {
            await axios.post(`/api/trading/${id}/start/`);
            alert('Bot started');
        } catch (err) {
            setError('Start failed');
        }
    };

    const handleTrade = async (values) => {
        try {
            await axios.post('/api/trading/trade/', values);
            setTrades([...trades, values]);
        } catch (err) {
            setError('Trade failed');
        }
    };

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Trading</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Typography variant="h5">Strategies</Typography>
            <List>
                {strategies.map(s => (
                    <ListItem key={s.id} secondaryAction={<Button onClick={() => handleStartBot(s.id)}>Start Bot</Button>}>
                        <ListItemText primary={s.name} />
                    </ListItem>
                ))}
            </List>
            <Typography variant="h5">Place Trade</Typography>
            <Formik initialValues={{ symbol: 'BTC/USDT', amount: '', type: 'buy' }} validationSchema={Yup.object({ symbol: Yup.string().required(), amount: Yup.number().required() })} onSubmit={handleTrade}>
                <Form>
                    <Field name="symbol" as={TextField} label="Symbol" fullWidth margin="normal" />
                    <Field name="amount" as={TextField} label="Amount" type="number" fullWidth margin="normal" />
                    <FormControl fullWidth margin="normal">
                        <InputLabel>Type</InputLabel>
                        <Field name="type" as={Select}>
                            <MenuItem value="buy">Buy</MenuItem>
                            <MenuItem value="sell">Sell</MenuItem>
                        </Field>
                    </FormControl>
                    <Button type="submit" variant="contained">Place Trade</Button>
                </Form>
            </Formik>
            <Typography variant="h5">Trade History</Typography>
            <List>
                {trades.map(t => (
                    <ListItem key={t.id}>
                        <ListItemText primary={`${t.symbol} - ${t.type} - ${t.amount}`} />
                    </ListItem>
                ))}
            </List>
        </Box>
    );
}

export default Trading;
