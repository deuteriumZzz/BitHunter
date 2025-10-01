import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, Alert } from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';

function Register() {
    const { register } = React.useContext(AuthContext);
    const navigate = useNavigate();
    const [error, setError] = React.useState('');

    const validationSchema = Yup.object({
        username: Yup.string().required('Required'),
        email: Yup.string().email('Invalid email').required('Required'),
        password: Yup.string().min(6, 'Min 6 chars').required('Required'),
    });

    const handleSubmit = async (values) => {
        try {
            await register(values);
            navigate('/login');
        } catch (err) {
            setError('Registration failed');
        }
    };

    return (
        <Box sx={{ maxWidth: 400, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Register</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Formik initialValues={{ username: '', email: '', password: '' }} validationSchema={validationSchema} onSubmit={handleSubmit}>
                <Form>
                    <Field name="username" as={TextField} label="Username" fullWidth margin="normal" />
                    <Field name="email" as={TextField} label="Email" fullWidth margin="normal" />
                    <Field name="password" type="password" as={TextField} label="Password" fullWidth margin="normal" />
                    <Button type="submit" variant="contained" fullWidth>Register</Button>
                </Form>
            </Formik>
        </Box>
    );
}

export default Register;
