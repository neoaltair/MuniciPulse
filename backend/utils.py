"""
Utility functions for CivicFix backend
"""
import math
import os
import uuid
from datetime import datetime
from typing import Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula for accurate distance calculation.
    
    Args:
        lat1: Latitude of point 1 in decimal degrees
        lon1: Longitude of point 1 in decimal degrees
        lat2: Latitude of point 2 in decimal degrees
        lon2: Longitude of point 2 in decimal degrees
    
    Returns:
        Distance in meters
    """
    # Radius of Earth in meters
    R = 6371000
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent collisions.
    
    Args:
        original_filename: Original uploaded filename
    
    Returns:
        Unique filename with timestamp and UUID
    """
    ext = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{ext}"


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Validate GPS coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (-90 <= latitude <= 90):
        return False, "Latitude must be between -90 and 90"
    
    if not (-180 <= longitude <= 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, ""


def validate_image_file(filename: str, content_type: str) -> Tuple[bool, str]:
    """
    Validate uploaded image file.
    
    Args:
        filename: Uploaded filename
        content_type: MIME type of the file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    allowed_mime_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File extension {ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    if content_type not in allowed_mime_types:
        return False, f"MIME type {content_type} not allowed. Allowed: {', '.join(allowed_mime_types)}"
    
    return True, ""
