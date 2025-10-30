import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from './contexts/AuthContext';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import ErrorBoundary from './components/ErrorBoundary';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Alerts = lazy(() => import('./pages/Alerts'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Trading = lazy(() => import('./pages/Trading'));
const News = lazy(() => import('./pages/News'));
const Settings = lazy(() => import('./pages/Settings'));
const Portfolio = lazy(() => import('./pages/Portfolio'));
const Community = lazy(() => import('./pages/Community'));

function App() {
  const { user } = useContext(AuthContext);
  const isAuthenticated = !!user;

  return (
    <Router>
      <ErrorBoundary>
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
          {isAuthenticated && <Sidebar />}
          <div className="flex-1 flex flex-col overflow-hidden md:flex-row">
            {isAuthenticated && <Header />}
            <main className="flex-1 p-4 overflow-auto">
              <Suspense fallback={<div>Загрузка...</div>}>
                <Routes>
                  <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
                  <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
                  <Route path="/alerts" element={isAuthenticated ? <Alerts /> : <Navigate to="/login" />} />
                  <Route path="/analytics" element={isAuthenticated ? <Analytics /> : <Navigate to="/login" />} />
                  <Route path="/trading" element={isAuthenticated ? <Trading /> : <Navigate to="/login" />} />
                  <Route path="/news" element={isAuthenticated ? <News /> : <Navigate to="/login" />} />
                  <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />
                  <Route path="/portfolio" element={isAuthenticated ? <Portfolio /> : <Navigate to="/login" />} />
                  <Route path="/community" element={isAuthenticated ? <Community /> : <Navigate to="/login" />} />
                </Routes>
              </Suspense>
            </main>
          </div>
        </div>
      </ErrorBoundary>
    </Router>
  );
}

export default App;
