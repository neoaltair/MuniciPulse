$url = "http://localhost:8000/auth/register"
$body = @{
    email = "test3@example.com"
    password = "password123"
    role = "citizen"
    first_name = "Test"
    last_name = "User"
    phone_number = $null
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-WebRequest -Uri $url -Method POST -Body $body -Headers $headers -UseBasicParsing
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Response: $($_.Exception.Response)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $ reader.DiscardBufferedData()
        Write-Host "Error Response: $($reader.ReadToEnd())"
    }
}
