import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import ProtectedRoute from './components/ProtectedRoute';
import MyReports from './pages/MyReports';
import AdminDashboard from './pages/AdminDashboard';
import ReportForm from './components/ReportForm';
import { isAuthenticated, getDecodedToken } from './utils/auth';

import './App.css';

function App() {
    // Root redirect logic - send authenticated users to their appropriate dashboard
    const RootRedirect = () => {
        if (!isAuthenticated()) {
            return <Navigate to="/login" replace />;
        }

        const decoded = getDecodedToken();
        const role = decoded?.role;

        if (role === 'municipal_officer') {
            return <Navigate to="/admin/dashboard" replace />;
        } else if (role === 'citizen') {
            return <Navigate to="/my-reports" replace />;
        }

        return <Navigate to="/login" replace />;
    };

    return (
        <Router>
            <div className="App">
                <Routes>
                    {/* Public Routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />

                    {/* Protected Routes - Citizen */}
                    <Route
                        path="/my-reports"
                        element={
                            <ProtectedRoute allowedRoles={['citizen']}>
                                <MyReports />
                            </ProtectedRoute>
                        }
                    />

                    {/* Report Creation - Citizen Only */}
                    <Route
                        path="/create-report"
                        element={
                            <ProtectedRoute allowedRoles={['citizen']}>
                                <ReportForm />
                            </ProtectedRoute>
                        }
                    />

                    {/* Protected Routes - Municipal Officer */}
                    <Route
                        path="/admin/dashboard"
                        element={
                            <ProtectedRoute allowedRoles={['municipal_officer']}>
                                <AdminDashboard />
                            </ProtectedRoute>
                        }
                    />

                    {/* Root Route - Redirect based on authentication */}
                    <Route path="/" element={<RootRedirect />} />

                    {/* Catch-all - Redirect to root */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
