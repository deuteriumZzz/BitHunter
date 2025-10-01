import React, { useContext, useState, useEffect } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, Alert, CircularProgress } from '@mui/material';
import axios from 'axios';
import { AuthContext } from '../contexts/AuthContext';

function Profile() {
    const { user } = useContext(AuthContext);
    const [profile, setProfile] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('/api/accounts/profile/').then(res => {
            setProfile(res.data);
            setLoading(false);
        }).catch(() => setError('Failed to load profile'));
    }, []);

    const handleSubmit = async (values) => {
        try {
            await axios.put('/api/accounts/profile/', values);
            setProfile(values);
        } catch (err) {
            setError('Update failed');
        }
    };

    if (loading) return <CircularProgress />;

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Profile</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Formik initialValues={profile} validationSchema={Yup.object({ balance: Yup.number().required() })} onSubmit={handleSubmit}>
                <Form>
                    <Field name="balance" as={TextField} label="Balance" fullWidth margin="normal" />
                    <Field name="api_key" as={TextField} label="API Key" fullWidth margin="normal" />
                    <Field name="secret_key" type="password" as={TextField} label="Secret Key" fullWidth margin="normal" />
                    <Field name="telegram_chat_id" as={TextField} label="Telegram Chat ID" fullWidth margin="normal" />
                    <Button type="submit" variant="contained">Update</Button>
                </Form>
            </Formik>
        </Box>
    );
}

export default Profile;
