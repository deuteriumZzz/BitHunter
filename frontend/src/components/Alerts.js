import React from 'react';
import axios from 'axios';

function Alerts() {
    const createAlert = () => {
        axios.post('http://localhost:8000/alerts/create/').then(() => alert('Alert created'));
    };

    return (
        <div>
            <h2>Alerts</h2>
            <button onClick={createAlert}>Create Alert</button>
        </div>
    );
}

export default Alerts;
