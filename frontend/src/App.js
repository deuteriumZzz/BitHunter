import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Trading from './components/Trading';
import Analytics from './components/Analytics';
import Alerts from './components/Alerts';

function App() {
    return (
        <Router>
            <div>
                <h1>BitHunter</h1>
                <Routes>
                    <Route path="/trading" element={<Trading />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="/alerts" element={<Alerts />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
