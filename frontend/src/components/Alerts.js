import React, { useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, List, ListItem, ListItemText, IconButton, Alert } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('/api/alerts/').then(res => setAlerts(res.data)).catch(() => setError('Failed to load alerts'));
    }, []);

    const handleCreate = async (values) => {
        try {
            await axios.post('/api/alerts/', values);
            setAlerts([...alerts, values]);
        } catch (err) {
            setError('Create failed');
        }
    };

    const handleDelete = async (id) => {
        try {
            await axios.delete(`/api/alerts/${id}/`);
            setAlerts(alerts.filter(a => a.id !== id));
        } catch (err) {
            setError('Delete failed');
        }
    };

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Alerts</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Formik initialValues={{ symbol: '', threshold: '' }} validationSchema={Yup.object({ symbol: Yup.string().required(), threshold: Yup.number().required() })} onSubmit={handleCreate}>
                <Form>
                    <Field name="symbol" as={TextField} label="Symbol" fullWidth margin="normal" />
                    <Field name="threshold" as={TextField} label="Threshold" type="number" fullWidth margin="normal" />
                    <Button type="submit" variant="contained">Create Alert</Button>
                </Form>
            </Formik>
            <List>
                {alerts.map(a => (
                    <ListItem key={a.id} secondaryAction={<IconButton onClick={() => handleDelete(a.id)}><DeleteIcon /></IconButton>}>
                        <ListItemText primary={`${a.symbol} - ${a.threshold}`} />
                    </ListItem>
                ))}
            </List>
        </Box>
    );
}

export default Alerts;
