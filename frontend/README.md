# CivicFix Frontend

React application for CivicFix civic reporting platform with role-based authentication.

## Features

✅ **JWT Authentication** - Secure token-based authentication with localStorage  
✅ **Role-Based Routing** - Automatic redirection based on user role  
✅ **Two User Types**:
- **Citizens** → Redirected to `/my-reports`
- **Municipal Officers** → Redirected to `/admin/dashboard`  
✅ **Protected Routes** - Route guards with role validation  
✅ **Modern UI** - Gradient designs with responsive layouts  

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (default: `http://localhost:8000`):
```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm start
```

Application will open at `http://localhost:3000`

## How It Works

### Authentication Flow

1. **Login/Signup** → User submits credentials
2. **JWT Token** → Backend returns JWT token with role and scopes
3. **Store Token** → Token saved to localStorage
4. **Decode Token** → Extract user role from JWT payload
5. **Route Redirect**:
   - `role: 'municipal_officer'` → `/admin/dashboard`
   - `role: 'citizen'` → `/my-reports`

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "role": "citizen",
  "scopes": ["citizen"],
  "exp": 1234567890
}
```

### Token Management

All token operations in `src/utils/auth.js`:

- `setToken(token)` - Store JWT in localStorage
- `getToken()` - Retrieve JWT from localStorage
- `getDecodedToken()` - Decode and return JWT payload
- `getUserRole()` - Get user role from token
- `isAuthenticated()` - Check if token is valid
- `logout()` - Clear token and redirect to login

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Login.jsx               # Login page
│   │   ├── Signup.jsx              # Signup page
│   │   ├── ProtectedRoute.jsx      # Route guard component
│   │   ├── Auth.css                # Auth page styles
│   │   └── Dashboard.css           # Dashboard styles
│   ├── pages/
│   │   ├── MyReports.jsx           # Citizen dashboard
│   │   └── AdminDashboard.jsx      # Officer dashboard
│   ├── utils/
│   │   ├── auth.js                 # JWT token utilities
│   │   └── api.js                  # Axios API client
│   ├── App.jsx                     # Main app with routes
│   ├── App.css                     # Global styles
│   └── index.js                    # Entry point
├── package.json
├── .env.example
└── README.md
```

## Routes

| Route | Access | Redirects To |
|-------|--------|-------------|
| `/login` | Public | N/A |
| `/signup` | Public | N/A |
| `/my-reports` | Citizens only | Dashboard based on role |
| `/admin/dashboard` | Officers only | Dashboard based on role |
| `/` | Authenticated users | Role-specific dashboard |

## Components

### Login (`components/Login.jsx`)

- Email/password authentication
- Stores JWT in localStorage
- Decodes token to get role
- Redirects based on `role` field

### Signup (`components/Signup.jsx`)

- User registration with role selection
- Password validation
- Auto-login after successful registration
- Role-based redirection

### ProtectedRoute (`components/ProtectedRoute.jsx`)

- Higher-order component for route protection
- Checks authentication status
- Validates user role against `allowedRoles`
- Redirects unauthorized users

### MyReports (`pages/MyReports.jsx`)

- Citizen dashboard
- Displays user info
- Placeholder for report management
- Logout functionality

### AdminDashboard (`pages/AdminDashboard.jsx`)

- Municipal officer dashboard
- Displays officer info and stats
- Placeholder for report management tools
- Admin-specific UI

## API Integration

### Axios Client (`utils/api.js`)

Configured with:
- Base URL from environment variable
- Automatic Bearer token injection
- 401 error handling (auto-logout)

### Available API Methods

```javascript
import { authAPI, reportsAPI } from './utils/api';

// Authentication
authAPI.register(userData);
authAPI.login(credentials);
authAPI.getMe();

// Reports
reportsAPI.create(formData);
reportsAPI.getAll(params);
reportsAPI.getById(id);
reportsAPI.updateStatus(id, statusData);
```

## Testing the Application

### 1. Start Backend API

```bash
cd backend
python main.py
```

### 2. Start Frontend

```bash
cd frontend
npm start
```

### 3. Test Flow

**As a Citizen:**
1. Go to `/signup`
2. Fill form with role: "Citizen"
3. Submit → Auto-logged in → Redirected to `/my-reports` ✅

**As an Officer:**
1. Go to `/signup`
2. Fill form with role: "Municipal Officer"
3. Submit → Auto-logged in → Redirected to `/admin/dashboard` ✅

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |

## Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

## Dependencies

- **react** `^18.2.0` - Core React library
- **react-router-dom** `^6.20.0` - Client-side routing
- **jwt-decode** `^4.0.0` - JWT token decoding
- **axios** `^1.6.2` - HTTP client

## Security Notes

🔒 **localStorage** - JWT stored in browser localStorage  
🔒 **Auto-logout** - Expired tokens automatically clear  
🔒 **Role Validation** - Server-side role verification required  
🔒 **Protected Routes** - Route guards prevent unauthorized access  

## Next Steps

- Implement report creation form with image upload
- Add interactive map with Leaflet.js
- Build report list and detail views
- Add status update interface for officers
- Implement real-time notifications
- Add search and filtering

## License

MIT
