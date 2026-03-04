import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsAPI } from '../utils/api';
import './ReportForm.css';

function ReportForm() {
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: 'infrastructure',
        priority: 'medium',
        latitude: '',
        longitude: '',
    });

    const [images, setImages] = useState([]);
    const [imagePreviews, setImagePreviews] = useState([]);
    const [locationLoading, setLocationLoading] = useState(false);
    const [locationError, setLocationError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        setError('');
    };

    // Geolocation API - Get current location
    const handleGetLocation = () => {
        setLocationLoading(true);
        setLocationError('');

        if (!navigator.geolocation) {
            setLocationError('Geolocation is not supported by your browser');
            setLocationLoading(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                setFormData({
                    ...formData,
                    latitude: position.coords.latitude.toFixed(6),
                    longitude: position.coords.longitude.toFixed(6),
                });
                setLocationLoading(false);
            },
            (error) => {
                let errorMessage = 'Unable to retrieve your location';
                if (error.code === error.PERMISSION_DENIED) {
                    errorMessage = 'Location permission denied. Please enable location access.';
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    errorMessage = 'Location information unavailable';
                } else if (error.code === error.TIMEOUT) {
                    errorMessage = 'Location request timed out';
                }
                setLocationError(errorMessage);
                setLocationLoading(false);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0,
            }
        );
    };

    // Handle image selection with preview
    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);

        if (files.length === 0) return;

        // Limit to 5 images
        if (images.length + files.length > 5) {
            setError('Maximum 5 images allowed');
            return;
        }

        // Validate file types and sizes
        const validFiles = [];
        const newPreviews = [];

        files.forEach((file) => {
            // Check file type
            if (!file.type.startsWith('image/')) {
                setError(`${file.name} is not an image file`);
                return;
            }

            // Check file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                setError(`${file.name} exceeds 10MB limit`);
                return;
            }

            validFiles.push(file);

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                newPreviews.push({
                    file: file,
                    preview: reader.result,
                    name: file.name,
                });

                // Update state when all files are read
                if (newPreviews.length === validFiles.length) {
                    setImages([...images, ...validFiles]);
                    setImagePreviews([...imagePreviews, ...newPreviews]);
                }
            };
            reader.readAsDataURL(file);
        });
    };

    // Remove image from selection
    const handleRemoveImage = (index) => {
        setImages(images.filter((_, i) => i !== index));
        setImagePreviews(imagePreviews.filter((_, i) => i !== index));
    };

    // Form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError('');

        // Validation
        if (!formData.title.trim()) {
            setError('Please enter a title');
            setSubmitting(false);
            return;
        }

        if (!formData.description.trim()) {
            setError('Please enter a description');
            setSubmitting(false);
            return;
        }

        if (formData.description.trim().length < 5) {
            setError('Description must be at least 5 characters long');
            setSubmitting(false);
            return;
        }

        if (!formData.latitude || !formData.longitude) {
            setError('Please get your location or enter coordinates manually');
            setSubmitting(false);
            return;
        }

        if (images.length === 0) {
            setError('Please upload at least one image');
            setSubmitting(false);
            return;
        }

        try {
            // Create FormData for multipart/form-data submission
            const submitData = new FormData();
            submitData.append('title', formData.title);
            submitData.append('description', formData.description);
            submitData.append('category', formData.category);
            submitData.append('latitude', formData.latitude);
            submitData.append('longitude', formData.longitude);
            submitData.append('priority', formData.priority);

            // Append all images
            images.forEach((image) => {
                submitData.append('images', image);
            });

            // Submit to API
            const response = await reportsAPI.create(submitData);

            // Success - redirect to reports page
            alert('Report submitted successfully!');
            navigate('/my-reports');
        } catch (err) {
            console.error('Error submitting report:', err);
            setError(
                err.response?.data?.detail || 'Failed to submit report. Please try again.'
            );
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="report-form-container">
            <div className="report-form-card">
                <div className="form-header">
                    <h1>📝 Report an Issue</h1>
                    <p>Help improve your community by reporting civic issues</p>
                </div>

                {error && <div className="error-banner">{error}</div>}

                <form onSubmit={handleSubmit} className="report-form">
                    {/* Title */}
                    <div className="form-group">
                        <label htmlFor="title">Issue Title *</label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleInputChange}
                            placeholder="e.g., Pothole on Main Street"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div className="form-group">
                        <label htmlFor="description">Description * (min. 5 characters)</label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            placeholder="Provide detailed information about the issue (at least 5 characters)..."
                            rows="4"
                            required
                        />
                    </div>

                    {/* Category and Priority */}
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="category">Category</label>
                            <select
                                id="category"
                                name="category"
                                value={formData.category}
                                onChange={handleInputChange}
                            >
                                <option value="infrastructure">Infrastructure</option>
                                <option value="sanitation">Sanitation</option>
                                <option value="lighting">Street Lighting</option>
                                <option value="parks">Parks & Recreation</option>
                                <option value="traffic">Traffic & Roads</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="priority">Priority</label>
                            <select
                                id="priority"
                                name="priority"
                                value={formData.priority}
                                onChange={handleInputChange}
                            >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                    </div>

                    {/* Location Section */}
                    <div className="location-section">
                        <h3>📍 Location</h3>
                        <button
                            type="button"
                            onClick={handleGetLocation}
                            className="btn-location"
                            disabled={locationLoading}
                        >
                            {locationLoading ? (
                                <>
                                    <span className="spinner-small"></span> Getting location...
                                </>
                            ) : (
                                <>
                                    <span>📍</span> Get Current Location
                                </>
                            )}
                        </button>

                        {locationError && (
                            <div className="location-error">{locationError}</div>
                        )}

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="latitude">Latitude *</label>
                                <input
                                    type="number"
                                    id="latitude"
                                    name="latitude"
                                    value={formData.latitude}
                                    onChange={handleInputChange}
                                    placeholder="40.7128"
                                    step="any"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="longitude">Longitude *</label>
                                <input
                                    type="number"
                                    id="longitude"
                                    name="longitude"
                                    value={formData.longitude}
                                    onChange={handleInputChange}
                                    placeholder="-74.0060"
                                    step="any"
                                    required
                                />
                            </div>
                        </div>

                        {formData.latitude && formData.longitude && (
                            <div className="location-preview">
                                ✓ Location set: {formData.latitude}, {formData.longitude}
                            </div>
                        )}
                    </div>

                    {/* Image Upload Section */}
                    <div className="image-section">
                        <h3>📷 Photos</h3>
                        <p className="image-help">Upload up to 5 images (max 10MB each)</p>

                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleImageChange}
                            accept="image/*"
                            capture="environment"
                            multiple
                            style={{ display: 'none' }}
                        />

                        <div className="image-upload-buttons">
                            <button
                                type="button"
                                onClick={() => fileInputRef.current.click()}
                                className="btn-upload"
                            >
                                📸 Take Photo / Choose Images
                            </button>
                        </div>

                        {/* Image Previews */}
                        {imagePreviews.length > 0 && (
                            <div className="image-previews">
                                {imagePreviews.map((preview, index) => (
                                    <div key={index} className="image-preview-item">
                                        <img src={preview.preview} alt={`Preview ${index + 1}`} />
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveImage(index)}
                                            className="btn-remove-image"
                                            title="Remove image"
                                        >
                                            ×
                                        </button>
                                        <div className="image-name">{preview.name}</div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {images.length === 0 && (
                            <div className="no-images">
                                <span>📁</span>
                                <p>No images selected</p>
                            </div>
                        )}
                    </div>

                    {/* Submit Buttons */}
                    <div className="form-actions">
                        <button
                            type="button"
                            onClick={() => navigate('/my-reports')}
                            className="btn-cancel"
                            disabled={submitting}
                        >
                            Cancel
                        </button>
                        <button type="submit" className="btn-submit" disabled={submitting}>
                            {submitting ? (
                                <>
                                    <span className="spinner-small"></span> Submitting...
                                </>
                            ) : (
                                'Submit Report'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ReportForm;
