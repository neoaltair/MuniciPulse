import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getDecodedToken } from '../utils/auth';

/**
 * ProtectedRoute component that checks authentication and role-based access
 * @param {object} props - Component props
 * @param {JSX.Element} props.children - Child components to render if authorized
 * @param {string[]} props.allowedRoles - Array of allowed roles (e.g., ['citizen', 'municipal_officer'])
 */
function ProtectedRoute({ children, allowedRoles }) {
    // Check if user is authenticated
    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }

    // If allowedRoles is specified, check user's role
    if (allowedRoles && allowedRoles.length > 0) {
        const decoded = getDecodedToken();
        const userRole = decoded?.role;

        if (!userRole || !allowedRoles.includes(userRole)) {
            // User doesn't have permission - redirect to appropriate page
            if (userRole === 'citizen') {
                return <Navigate to="/my-reports" replace />;
            } else if (userRole === 'municipal_officer') {
                return <Navigate to="/admin/dashboard" replace />;
            }
            return <Navigate to="/login" replace />;
        }
    }

    return children;
}

export default ProtectedRoute;
