param(
    [string]$NgrokUrl
)

# Function to get ngrok URL automatically if running locally
function Get-NgrokUrl {
    try {
        $tunnels = (Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" -UseBasicParsing -ErrorAction SilentlyContinue).Content | ConvertFrom-Json
        $backendTunnel = $tunnels.tunnels | Where-Object { $_.config.addr -match "8000" } | Select-Object -First 1
        return $backendTunnel.public_url
    } catch {
        return $null
    }
}

# Try to auto-detect if not provided
if (-not $NgrokUrl) {
    Write-Host "Attempting to auto-detect ngrok backend URL..." -ForegroundColor Cyan
    $NgrokUrl = Get-NgrokUrl
    
    if ($NgrokUrl) {
         Write-Host "Auto-detected URL: $NgrokUrl" -ForegroundColor Green
    }
}

# Prompt if still missing
if (-not $NgrokUrl) {
    Write-Host "Could not detect ngrok URL. Please enter the backend ngrok URL (e.g., https://xyz.ngrok-free.app)" -ForegroundColor Yellow
    $NgrokUrl = Read-Host "Ngrok URL"
}

if (-not $NgrokUrl) {
    Write-Error "Ngrok URL is required to start the app in remote mode."
    exit 1
}

# Remove trailing slash
if ($NgrokUrl.EndsWith("/")) {
    $NgrokUrl = $NgrokUrl.Substring(0, $NgrokUrl.Length - 1)
}

Write-Host "--------------------------------------------------" -ForegroundColor Cyan
Write-Host "🚀 Starting CivicFix Frontend for Remote Access" -ForegroundColor Cyan
Write-Host "📍 Backend URL: $NgrokUrl" -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Cyan

# Set environment variable for this session only
$env:REACT_APP_API_URL = $NgrokUrl

# Start React app
npm start
