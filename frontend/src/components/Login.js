import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, Alert } from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';

function Login() {
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();
    const [error, setError] = React.useState('');

    const validationSchema = Yup.object({
        username: Yup.string().required('Required'),
        password: Yup.string().required('Required'),
    });

    const handleSubmit = async (values) => {
        try {
            await login(values);
            navigate('/trading');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <Box sx={{ maxWidth: 400, mx: 'auto', mt: 5 }}>
            <Typography variant="h4">Login</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Formik initialValues={{ username: '', password: '' }} validationSchema={validationSchema} onSubmit={handleSubmit}>
                <Form>
                    <Field name="username" as={TextField} label="Username" fullWidth margin="normal" />
                    <Field name="password" type="password" as={TextField} label="Password" fullWidth margin="normal" />
                    <Button type="submit" variant="contained" fullWidth>Login</Button>
                </Form>
            </Formik>
        </Box>
    );
}

export default Login;
