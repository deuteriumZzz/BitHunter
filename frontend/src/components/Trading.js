import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Trading() {
    const [strategies, setStrategies] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8000/trading/').then(res => setStrategies(res.data));
    }, []);

    const startBot = (id) => {
        axios.post(`http://localhost:8000/trading/${id}/start/`).then(() => alert('Bot started'));
    };

    return (
        <div>
            <h2>Trading</h2>
            {strategies.map(s => (
                <div key={s.id}>
                    <p>{s.name}</p>
                    <button onClick={() => startBot(s.id)}>Start Bot</button>
                </div>
            ))}
        </div>
    );
}

export default Trading;
