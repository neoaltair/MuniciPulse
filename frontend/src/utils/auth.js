/**
 * Authentication utilities for JWT token management
 */
import { jwtDecode } from 'jwt-decode';

const TOKEN_KEY = 'civicfix_token';

/**
 * Store JWT token in localStorage
 * @param {string} token - JWT token
 */
export const setToken = (token) => {
    localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Get JWT token from localStorage
 * @returns {string|null} JWT token or null if not found
 */
export const getToken = () => {
    return localStorage.getItem(TOKEN_KEY);
};

/**
 * Remove JWT token from localStorage
 */
export const removeToken = () => {
    localStorage.removeItem(TOKEN_KEY);
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has a valid token
 */
export const isAuthenticated = () => {
    const token = getToken();
    if (!token) return false;

    try {
        const decoded = jwtDecode(token);
        // Check if token is expired
        if (decoded.exp * 1000 < Date.now()) {
            removeToken();
            return false;
        }
        return true;
    } catch (error) {
        removeToken();
        return false;
    }
};

/**
 * Decode JWT token and extract user information
 * @returns {object|null} Decoded token data or null
 */
export const getDecodedToken = () => {
    const token = getToken();
    if (!token) return null;

    try {
        return jwtDecode(token);
    } catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
};

/**
 * Get user role from JWT token
 * @returns {string|null} User role ('citizen' or 'municipal_officer')
 */
export const getUserRole = () => {
    const decoded = getDecodedToken();
    return decoded ? decoded.role : null;
};

/**
 * Get user scopes from JWT token
 * @returns {array} Array of scopes ['citizen'] or ['officer']
 */
export const getUserScopes = () => {
    const decoded = getDecodedToken();
    return decoded ? decoded.scopes : [];
};

/**
 * Get user ID from JWT token
 * @returns {string|null} User ID
 */
export const getUserId = () => {
    const decoded = getDecodedToken();
    return decoded ? decoded.sub : null;
};

/**
 * Check if user has specific scope
 * @param {string} scope - Scope to check ('citizen' or 'officer')
 * @returns {boolean} True if user has the scope
 */
export const hasScope = (scope) => {
    const scopes = getUserScopes();
    return scopes.includes(scope);
};

/**
 * Logout user by removing token
 */
export const logout = () => {
    removeToken();
    window.location.href = '/login';
};
