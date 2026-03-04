import React, { useState, useEffect } from 'react';
import { authAPI, reportsAPI } from '../utils/api';
import { logout } from '../utils/auth';
import { haversineDistance, formatDistance, getTimeAgo } from '../utils/distance';
import '../components/Dashboard.css';
import './OfficerDashboard.css';

// Default Municipal Office location (can be configured)
const OFFICE_LOCATION = {
    lat: 40.7128,
    lng: -74.0060,
    name: 'Municipal Office, New York'
};

function AdminDashboard() {
    const [user, setUser] = useState(null);
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [updatingStatus, setUpdatingStatus] = useState(false);
    const [newStatus, setNewStatus] = useState('');
    const [statusComment, setStatusComment] = useState('');
    const [resolvedImage, setResolvedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);

    useEffect(() => {
        loadUserData();
        loadReports();
    }, []);

    const loadUserData = async () => {
        try {
            const response = await authAPI.getMe();
            setUser(response.data);
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    };

    const loadReports = async () => {
        try {
            setLoading(true);
            const response = await reportsAPI.getAll();

            // Filter for Pending and In-Progress, sort by most recent
            const filteredReports = response.data
                .filter(report => ['pending', 'in_progress'].includes(report.status))
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            setReports(filteredReports);
        } catch (error) {
            console.error('Error loading reports:', error);
        } finally {
            setLoading(false);
        }
    };

    const calculateDistance = (report) => {
        const distance = haversineDistance(
            OFFICE_LOCATION.lat,
            OFFICE_LOCATION.lng,
            report.latitude,
            report.longitude
        );
        return formatDistance(distance);
    };

    const handleEditClick = (report) => {
        setSelectedReport(report);
        setNewStatus(report.status);
        setStatusComment('');
        setResolvedImage(null);
        setImagePreview(null);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedReport(null);
        setNewStatus('');
        setStatusComment('');
        setResolvedImage(null);
        setImagePreview(null);
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }

            // Validate file size (10MB max)
            if (file.size > 10 * 1024 * 1024) {
                alert('Image must be less than 10MB');
                return;
            }

            setResolvedImage(file);

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleStatusUpdate = async () => {
        if (!selectedReport || !newStatus) return;

        // Validate: if status is 'resolved', image is required
        if (newStatus === 'resolved' && !resolvedImage) {
            alert('Please upload an "after" photo when marking as resolved');
            return;
        }

        setUpdatingStatus(true);
        try {
            // Create FormData
            const formData = new FormData();
            formData.append('new_status', newStatus);
            if (statusComment) {
                formData.append('comment', statusComment);
            }
            if (resolvedImage) {
                formData.append('resolved_image', resolvedImage);
            }

            await reportsAPI.updateStatus(selectedReport.id, formData);

            // Refresh reports
            await loadReports();
            handleCloseModal();
            alert('Status updated successfully! Email notification sent to citizen.');
        } catch (error) {
            console.error('Error updating status:', error);
            const errorMsg = error.response?.data?.detail || 'Failed to update status. Please try again.';
            alert(errorMsg);
        } finally {
            setUpdatingStatus(false);
        }
    };

    const handleLogout = () => {
        logout();
    };

    const getStatusBadge = (status) => {
        const badges = {
            pending: { class: 'status-badge-pending', text: 'Pending' },
            in_progress: { class: 'status-badge-in-progress', text: 'In Progress' },
        };
        const badge = badges[status] || { class: '', text: status };
        return <span className={`status-badge ${badge.class}`}>{badge.text}</span>;
    };

    const getPriorityBadge = (priority) => {
        const badges = {
            low: { class: 'priority-low', icon: '🟢' },
            medium: { class: 'priority-medium', icon: '🟡' },
            high: { class: 'priority-high', icon: '🔴' },
        };
        const badge = badges[priority] || { class: '', icon: '⚪' };
        return <span className={`priority-badge ${badge.class}`}>{badge.icon} {priority}</span>;
    };

    if (loading && reports.length === 0) {
        return (
            <div className="dashboard-container">
                <div className="loading">Loading reports...</div>
            </div>
        );
    }

    return (
        <div className="dashboard-container">
            <nav className="dashboard-nav">
                <div className="nav-brand">
                    <h2>🏛️ CivicFix Admin</h2>
                </div>
                <div className="nav-user">
                    <span className="user-name">
                        {user?.first_name} {user?.last_name}
                    </span>
                    <span className="user-role badge-officer">Municipal Officer</span>
                    <button onClick={handleLogout} className="btn-logout">
                        Logout
                    </button>
                </div>
            </nav>

            <div className="dashboard-content">
                <div className="page-header">
                    <div>
                        <h1>Officer Dashboard</h1>
                        <p>Manage pending and in-progress reports</p>
                    </div>
                    <button onClick={loadReports} className="btn-refresh" disabled={loading}>
                        {loading ? '⟳ Refreshing...' : '🔄 Refresh'}
                    </button>
                </div>

                {/* Statistics */}
                <div className="quick-stats">
                    <div className="stat-card pending">
                        <div className="stat-number">
                            {reports.filter(r => r.status === 'pending').length}
                        </div>
                        <div className="stat-label">Pending</div>
                    </div>
                    <div className="stat-card in-progress">
                        <div className="stat-number">
                            {reports.filter(r => r.status === 'in_progress').length}
                        </div>
                        <div className="stat-label">In Progress</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{reports.length}</div>
                        <div className="stat-label">Total Active</div>
                    </div>
                </div>

                {/* Reports Table */}
                <div className="table-container">
                    <h3>📋 Active Reports</h3>

                    {reports.length === 0 ? (
                        <div className="no-reports-table">
                            <p>No pending or in-progress reports at this time.</p>
                        </div>
                    ) : (
                        <div className="table-wrapper">
                            <table className="reports-table">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Category</th>
                                        <th>Priority</th>
                                        <th>Status</th>
                                        <th>Distance</th>
                                        <th>Reported</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {reports.map((report) => (
                                        <tr key={report.id}>
                                            <td className="title-cell">
                                                <strong>{report.title}</strong>
                                                <div className="subtitle">{report.description.substring(0, 60)}...</div>
                                            </td>
                                            <td>{report.category}</td>
                                            <td>{getPriorityBadge(report.priority)}</td>
                                            <td>{getStatusBadge(report.status)}</td>
                                            <td className="distance-cell">
                                                📍 {calculateDistance(report)}
                                            </td>
                                            <td className="time-cell">
                                                {getTimeAgo(report.created_at)}
                                            </td>
                                            <td>
                                                <button
                                                    onClick={() => handleEditClick(report)}
                                                    className="btn-edit"
                                                >
                                                    ✏️ Edit
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Status Edit Modal */}
            {showModal && selectedReport && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Edit Report Status</h2>
                            <button onClick={handleCloseModal} className="btn-close">×</button>
                        </div>

                        <div className="modal-body">
                            <div className="report-info">
                                <h3>{selectedReport.title}</h3>
                                <p className="report-desc">{selectedReport.description}</p>
                                <div className="report-meta">
                                    <span>📍 {calculateDistance(selectedReport)} from office</span>
                                    <span>📅 {new Date(selectedReport.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="status">New Status</label>
                                <select
                                    id="status"
                                    value={newStatus}
                                    onChange={(e) => setNewStatus(e.target.value)}
                                    className="modal-select"
                                >
                                    <option value="pending">Pending</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="resolved">Resolved</option>
                                    <option value="rejected">Rejected</option>
                                </select>
                            </div>

                            {/* Image Upload - Required for Resolved */}
                            {newStatus === 'resolved' && (
                                <div className="form-group">
                                    <label htmlFor="resolved_image">
                                        After Photo (Required for Resolved) *
                                    </label>
                                    <p className="field-help">Upload a photo showing the resolved issue</p>
                                    <input
                                        type="file"
                                        id="resolved_image"
                                        accept="image/*"
                                        onChange={handleImageChange}
                                        className="file-input"
                                    />
                                    {imagePreview && (
                                        <div className="image-preview-modal">
                                            <img src={imagePreview} alt="After photo preview" />
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setResolvedImage(null);
                                                    setImagePreview(null);
                                                }}
                                                className="btn-remove-preview"
                                            >
                                                × Remove
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="form-group">
                                <label htmlFor="comment">Comment (Optional)</label>
                                <textarea
                                    id="comment"
                                    value={statusComment}
                                    onChange={(e) => setStatusComment(e.target.value)}
                                    placeholder="Add a comment about this status change..."
                                    rows="3"
                                    className="modal-textarea"
                                />
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button
                                onClick={handleCloseModal}
                                className="btn-cancel-modal"
                                disabled={updatingStatus}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleStatusUpdate}
                                className="btn-save-modal"
                                disabled={updatingStatus || !newStatus}
                            >
                                {updatingStatus ? 'Updating...' : 'Update Status'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default AdminDashboard;
