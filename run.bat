@echo off
title Akatsuki Terminal Tools v2.0
cd /d "%~dp0"

:: Cek python3 atau python
where python3 >nul 2>nul
if %errorlevel% equ 0 (
    python3 akatsuki.py
) else (
    python akatsuki.py
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Gagal menjalankan script. Pastikan Python sudah terinstall dan ada di PATH.
    pause
)
