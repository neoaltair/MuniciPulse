import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { reportsAPI, API_BASE_URL } from '../utils/api';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker icons
const greenIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

function MapView() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [center] = useState([20.5937, 78.9629]); // Default: India (center)
    const [zoom] = useState(5); // Zoom level for country view

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            setLoading(true);
            // Fetch all reports (API will filter by user role automatically)
            const response = await reportsAPI.getAll();

            // Filter for only Resolved and Pending reports
            const filteredReports = response.data.filter(
                report => report.status === 'resolved' || report.status === 'pending'
            );

            setReports(filteredReports);
            setError(null);
        } catch (err) {
            console.error('Error fetching reports:', err);
            setError('Failed to load reports');
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmFix = async (reportId) => {
        if (window.confirm('Are you sure you want to confirm this fix?')) {
            try {
                // This could be an API call to mark as "verified" or add a comment
                console.log('Confirming fix for report:', reportId);
                alert('Fix confirmed! Thank you for your feedback.');
                // Optionally refresh reports
                fetchReports();
            } catch (err) {
                console.error('Error confirming fix:', err);
                alert('Failed to confirm fix. Please try again.');
            }
        }
    };

    const getMarkerIcon = (status) => {
        return status === 'resolved' ? greenIcon : redIcon;
    };

    const getStatusBadge = (status) => {
        const badgeClass = status === 'resolved' ? 'status-resolved' : 'status-pending';
        const statusText = status === 'resolved' ? 'Resolved' : 'Pending';
        return <span className={`status-badge ${badgeClass}`}>{statusText}</span>;
    };

    if (loading) {
        return (
            <div className="map-loading">
                <div className="spinner"></div>
                <p>Loading map...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="map-error">
                <p>⚠️ {error}</p>
                <button onClick={fetchReports} className="btn-retry">Retry</button>
            </div>
        );
    }

    return (
        <div className="map-view-container">
            <div className="map-header">
                <h2>📍 Civic Reports Map</h2>
                <div className="map-legend">
                    <div className="legend-item">
                        <span className="legend-dot green"></span>
                        <span>Resolved ({reports.filter(r => r.status === 'resolved').length})</span>
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot red"></span>
                        <span>Pending ({reports.filter(r => r.status === 'pending').length})</span>
                    </div>
                </div>
            </div>

            <MapContainer
                center={center}
                zoom={zoom}
                style={{ height: '600px', width: '100%' }}
                className="leaflet-map"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {reports.map((report) => (
                    <Marker
                        key={report.id}
                        position={[report.latitude, report.longitude]}
                        icon={getMarkerIcon(report.status)}
                    >
                        <Popup className="report-popup">
                            <div className="popup-content">
                                <div className="popup-header">
                                    <h3>{report.title}</h3>
                                    {getStatusBadge(report.status)}
                                </div>

                                {/* Display first image if available */}
                                {report.images && report.images.length > 0 && (
                                    <div className="popup-image">
                                        <img
                                            src={`${API_BASE_URL}${report.images[0].image_url}`}
                                            alt={report.title}
                                            onError={(e) => {
                                                e.target.src = 'https://via.placeholder.com/300x200?text=Image+Not+Found';
                                            }}
                                        />
                                    </div>
                                )}

                                <div className="popup-description">
                                    <strong>Description:</strong>
                                    <p>{report.description}</p>
                                </div>

                                <div className="popup-meta">
                                    <p><strong>Category:</strong> {report.category}</p>
                                    <p><strong>Priority:</strong> {report.priority}</p>
                                    <p><strong>Reported:</strong> {new Date(report.created_at).toLocaleDateString()}</p>
                                </div>

                                {/* Show Confirm Fix button only for Resolved reports */}
                                {report.status === 'resolved' && (
                                    <button
                                        onClick={() => handleConfirmFix(report.id)}
                                        className="btn-confirm-fix"
                                    >
                                        ✓ Confirm Fix
                                    </button>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {reports.length === 0 && (
                <div className="no-reports">
                    <p>No resolved or pending reports to display on the map.</p>
                </div>
            )}
        </div>
    );
}

export default MapView;
