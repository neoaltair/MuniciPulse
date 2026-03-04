import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, reportsAPI, API_BASE_URL } from '../utils/api';
import { logout } from '../utils/auth';
import MapView from '../components/MapView';
import './Dashboard.css';
import './ReportsList.css';

function MyReports() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [reports, setReports] = useState([]);
    const [publicReports, setPublicReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeView, setActiveView] = useState('overview'); // 'overview', 'list', 'public', or 'map'

    useEffect(() => {
        loadUserData();
        loadReports();
        loadPublicReports();
    }, []);

    // Reload reports when switching back to overview or list
    useEffect(() => {
        if (activeView === 'overview' || activeView === 'list') {
            loadReports();
        } else if (activeView === 'public') {
            loadPublicReports();
        }
    }, [activeView]);

    const loadUserData = async () => {
        try {
            const response = await authAPI.getMe();
            setUser(response.data);
        } catch (error) {
            console.error('Error loading user data:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadReports = async () => {
        try {
            const response = await reportsAPI.getAll();
            setReports(response.data);
        } catch (error) {
            console.error('Error loading reports:', error);
        }
    };

    const loadPublicReports = async () => {
        try {
            const response = await reportsAPI.getPublic();
            setPublicReports(response.data);
        } catch (error) {
            console.error('Error loading public reports:', error);
        }
    };

    const handleLogout = () => {
        logout();
    };

    if (loading) {
        return (
            <div className="dashboard-container">
                <div className="loading">Loading...</div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <nav className="dashboard-nav">
                <div className="nav-brand">
                    <h2>🏘️ CivicFix</h2>
                </div>
                <div className="nav-user">
                    <span className="user-name">
                        {user?.first_name} {user?.last_name}
                    </span>
                    <span className="user-role badge-citizen">Citizen</span>
                    <button onClick={handleLogout} className="btn-logout">
                        Logout
                    </button>
                </div>
            </nav>

            <div className="dashboard-content">
                <div className="page-header">
                    <h1>My Reports</h1>
                    <div className="view-tabs">
                        <button
                            className={`tab-btn ${activeView === 'overview' ? 'active' : ''}`}
                            onClick={() => setActiveView('overview')}
                        >
                            📊 Overview
                        </button>
                        <button
                            className={`tab-btn ${activeView === 'list' ? 'active' : ''}`}
                            onClick={() => setActiveView('list')}
                        >
                            📋 My Reports
                        </button>
                        <button
                            className={`tab-btn ${activeView === 'public' ? 'active' : ''}`}
                            onClick={() => setActiveView('public')}
                        >
                            🌍 All Reports
                        </button>
                        <button
                            className={`tab-btn ${activeView === 'map' ? 'active' : ''}`}
                            onClick={() => setActiveView('map')}
                        >
                            🗺️ Map View
                        </button>
                    </div>
                </div>

                {activeView === 'overview' ? (
                    <>
                        <div className="welcome-card">
                            <h3>👋 Welcome, {user?.first_name}!</h3>
                            <p>
                                This is your citizen dashboard. Here you can view all your submitted reports,
                                track their status, and create new reports.
                            </p>
                            <div className="quick-stats">
                                <div className="stat-card">
                                    <div className="stat-number">{reports.length}</div>
                                    <div className="stat-label">Total Reports</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-number">
                                        {reports.filter(r => r.status === 'pending').length}
                                    </div>
                                    <div className="stat-label">Pending</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-number">
                                        {reports.filter(r => r.status === 'in_progress').length}
                                    </div>
                                    <div className="stat-label">In Progress</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-number">
                                        {reports.filter(r => r.status === 'resolved').length}
                                    </div>
                                    <div className="stat-label">Resolved</div>
                                </div>
                            </div>
                            <button className="btn-primary" onClick={() => navigate('/create-report')}>
                                + Create New Report
                            </button>
                        </div>

                        <div className="info-box">
                            <h4>📋 Features Available:</h4>
                            <ul>
                                <li>View detailed list of your reports (click My Reports tab)</li>
                                <li>Track status updates and officer comments</li>
                                <li>See reports on interactive map (click Map View tab)</li>
                                <li>View before/after photos for resolved issues</li>
                            </ul>
                        </div>
                    </>
                ) : activeView === 'list' ? (
                    <div className="reports-list">
                        <div className="list-header">
                            <h2>My Submitted Reports</h2>
                            <button className="btn-primary" onClick={() => navigate('/create-report')}>
                                + New Report
                            </button>
                        </div>

                        {reports.length === 0 ? (
                            <div className="empty-state">
                                <p>😔 You haven't submitted any reports yet.</p>
                                <button className="btn-primary" onClick={() => navigate('/create-report')}>
                                    Create Your First Report
                                </button>
                            </div>
                        ) : (
                            <div className="reports-grid">
                                {reports.map(report => (
                                    <div key={report.id} className="report-card">
                                        <div className="report-card-header">
                                            <h3>{report.title}</h3>
                                            <span className={`status-badge status-${report.status}`}>
                                                {report.status === 'pending' && '🔴 Pending'}
                                                {report.status === 'in_progress' && '🟡 In Progress'}
                                                {report.status === 'resolved' && '🟢 Resolved'}
                                                {report.status === 'rejected' && '⚫ Rejected'}
                                            </span>
                                        </div>

                                        {report.images && report.images.length > 0 && (
                                            <div className="report-card-image">
                                                <img
                                                    src={`${API_BASE_URL}${report.images[0].image_url}`}
                                                    alt={report.title}
                                                    onError={(e) => {
                                                        e.target.src = 'https://via.placeholder.com/400x200?text=Image+Not+Available';
                                                    }}
                                                />
                                            </div>
                                        )}

                                        <div className="report-card-body">
                                            <p className="report-description">{report.description}</p>

                                            <div className="report-meta">
                                                <div className="meta-item">
                                                    <strong>📂 Category:</strong> {report.category}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>⚠️ Priority:</strong> {report.priority}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>📅 Submitted:</strong> {new Date(report.created_at).toLocaleDateString()}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>🕒 Last Updated:</strong> {new Date(report.updated_at).toLocaleString()}
                                                </div>
                                            </div>

                                            {report.resolved_image_url && (
                                                <div className="resolved-section">
                                                    <h4>✅ After Fix Photo:</h4>
                                                    <img
                                                        src={`${API_BASE_URL}${report.resolved_image_url}`}
                                                        alt="Resolved"
                                                        className="resolved-image"
                                                        onError={(e) => {
                                                            e.target.src = 'https://via.placeholder.com/300x200?text=Image+Not+Available';
                                                        }}
                                                    />
                                                </div>
                                            )}

                                            {report.status_history && report.status_history.length > 0 && (
                                                <div className="status-history">
                                                    <h4>📝 Status Updates:</h4>
                                                    {report.status_history.slice().reverse().map((history, idx) => (
                                                        <div key={idx} className="history-item">
                                                            <div className="history-status">
                                                                <span className={`status-badge status-${history.status}`}>
                                                                    {history.status}
                                                                </span>
                                                                <span className="history-date">
                                                                    {new Date(history.created_at).toLocaleString()}
                                                                </span>
                                                            </div>
                                                            {history.comment && (
                                                                <p className="history-comment">
                                                                    💬 Officer: "{history.comment}"
                                                                </p>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ) : activeView === 'public' ? (
                    <div className="reports-list">
                        <div className="list-header">
                            <h2>🌍 All Public Reports</h2>
                            <p style={{ fontSize: '14px', color: '#666' }}>Viewing reports from all users</p>
                        </div>

                        {publicReports.length === 0 ? (
                            <div className="empty-state">
                                <p>📭 No public reports available yet.</p>
                            </div>
                        ) : (
                            <div className="reports-grid">
                                {publicReports.map(report => (
                                    <div key={report.id} className="report-card">
                                        <div className="report-card-header">
                                            <h3>{report.title}</h3>
                                            <span className={`status-badge status-${report.status}`}>
                                                {report.status === 'pending' && '🔴 Pending'}
                                                {report.status === 'in_progress' && '🟡 In Progress'}
                                                {report.status === 'resolved' && '🟢 Resolved'}
                                                {report.status === 'rejected' && '⚫ Rejected'}
                                            </span>
                                        </div>

                                        {report.images && report.images.length > 0 && (
                                            <div className="report-card-image">
                                                <img
                                                    src={`${API_BASE_URL}${report.images[0].image_url}`}
                                                    alt={report.title}
                                                    onError={(e) => {
                                                        e.target.src = 'https://via.placeholder.com/400x200?text=Image+Not+Available';
                                                    }}
                                                />
                                            </div>
                                        )}

                                        <div className="report-card-body">
                                            <p className="report-description">{report.description}</p>

                                            <div className="report-meta">
                                                <div className="meta-item">
                                                    <strong>📂 Category:</strong> {report.category}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>⚠️ Priority:</strong> {report.priority}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>📅 Submitted:</strong> {new Date(report.created_at).toLocaleDateString()}
                                                </div>
                                                <div className="meta-item">
                                                    <strong>🕒 Last Updated:</strong> {new Date(report.updated_at).toLocaleString()}
                                                </div>
                                            </div>

                                            {report.resolved_image_url && (
                                                <div className="resolved-section">
                                                    <h4>✅ After Fix Photo:</h4>
                                                    <img
                                                        src={`${API_BASE_URL}${report.resolved_image_url}`}
                                                        alt="Resolved"
                                                        className="resolved-image"
                                                        onError={(e) => {
                                                            e.target.src = 'https://via.placeholder.com/300x200?text=Image+Not+Available';
                                                        }}
                                                    />
                                                </div>
                                            )}

                                            {report.status_history && report.status_history.length > 0 && (
                                                <div className="status-history">
                                                    <h4>📝 Status Updates:</h4>
                                                    {report.status_history.slice().reverse().map((history, idx) => (
                                                        <div key={idx} className="history-item">
                                                            <div className="history-status">
                                                                <span className={`status-badge status-${history.status}`}>
                                                                    {history.status}
                                                                </span>
                                                                <span className="history-date">
                                                                    {new Date(history.created_at).toLocaleString()}
                                                                </span>
                                                            </div>
                                                            {history.comment && (
                                                                <p className="history-comment">
                                                                    💬 Officer: "{history.comment}"
                                                                </p>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ) : (
                    <MapView />
                )}
            </div>
        </div>
    );
}

export default MyReports;
