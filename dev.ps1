<#
.SYNOPSIS
    Inicia simultáneamente el Backend (Flask) y Frontend (React/Vite).
.DESCRIPTION
    Ejecuta el script 'dev' del workspace raíz mediante pnpm y concurrently.
#>

Write-Host "Iniciando entorno de desarrollo Vino Nuevo (Backend + Frontend)..." -ForegroundColor Cyan
pnpm dev

