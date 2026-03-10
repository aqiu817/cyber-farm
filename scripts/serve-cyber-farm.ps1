param(
  [int]$Port = 4173
)

Write-Host "Cyber Farm available on all interfaces at port $Port"
Write-Host "Open this machine's LAN IP from another device, for example: http://<your-lan-ip>:$Port/"
python .\app.py --host 0.0.0.0 --port $Port
