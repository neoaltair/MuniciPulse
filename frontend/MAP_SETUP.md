# MapView Component - Setup Instructions

## Installation

The MapView component requires additional dependencies. Install them with:

```bash
cd frontend
npm install react-leaflet@^4.2.1 leaflet@^1.9.4
```

## Features

✅ **Interactive Map** - Displays reports on Leaflet.js map  
✅ **Color-Coded Markers**:
- 🟢 **Green** - Resolved reports
- 🔴 **Red** - Pending reports

✅ **Detailed Popups** - Click markers to see:
- Report title and status badge
- First uploaded image
- Description
- Category, priority, and date
- "Confirm Fix" button (for resolved reports only)

✅ **Legend** - Shows count of resolved vs pending reports  
✅ **Responsive** - Works on mobile and desktop

## Usage

The MapView component has been integrated into the Citizen dashboard:

1. Navigate to `/my-reports`
2. Click the **🗺️ Map View** tab
3. Map will display all resolved and pending reports
4. Click any marker to see report details

## API Integration

The component fetches reports using:
```javascript
reportsAPI.getAll()
```

Then filters for only `'resolved'` and `'pending'` statuses.

## Marker Icons

Using public CDN images from leaflet-color-markers:
- Green: `marker-icon-2x-green.png`
- Red: `marker-icon-2x-red.png`

## Confirm Fix Feature

When a user clicks "Confirm Fix" on a resolved report:
1. Confirmation dialog appears
2. Console logs the action (placeholder)
3. Shows success alert
4. Can be extended to call backend API

## Customization

**Change Map Center:**
```javascript
const [center] = useState([YOUR_LAT, YOUR_LNG]);
```

**Change Zoom Level:**
```javascript
const [zoom] = useState(13); // Adjust 1-18
```

**Add More Statuses:**
Update the filter in `fetchReports()`:
```javascript
const filteredReports = response.data.filter(
  report => ['resolved', 'pending', 'in_progress'].includes(report.status)
);
```

## Files Created

- `src/components/MapView.jsx` - Main map component
- `src/components/MapView.css` - Map styling
- Updated `src/pages/MyReports.jsx` - Added tab navigation
- Updated `package.json` - Added leaflet dependencies

## Next Steps

- Add map to Officer dashboard
- Implement actual "Confirm Fix" API endpoint
- Add clustering for many markers
- Filter by category/status
- Show user's location
