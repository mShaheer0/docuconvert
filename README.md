# Scalable File Converter (FastAPI)

This project provides a scalable, modular web application for:

- PDF to Word (.docx)
- Word (.docx) to PDF

## Architecture

- Backend: Python + FastAPI
- Frontend: HTML + CSS + JavaScript
- Modular backend layers:
  - routes: API endpoint handling
  - services: conversion logic
  - utils: file utilities and response helpers
  - core: settings, security, custom exceptions
  - middlewares: rate limiting

## Features

- Dark themed, responsive, interactive frontend
- Drag-and-drop upload UX
- File preview with name and size
- Loading/progress indicator
- Auto download on successful conversion
- Friendly error messages
- Strict file type checks (PDF or DOCX)
- File size limit (10 MB)
- Sanitized filenames
- Temporary-file cleanup after conversion
- Safe global error handling
- Basic in-memory rate limiting

## Project Structure

```
backend/
  app/
    core/
    middlewares/
    routes/
    services/
    utils/
    main.py
frontend/
  assets/
    css/
    js/
  pdf-to-word.html
  word-to-pdf.html
requirements.txt
README.md
```

## Local Setup

1. Create and activate a virtual environment:

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the server from project root:

   ```powershell
   uvicorn backend.app.main:app --reload
   ```

4. Open in browser:

- http://127.0.0.1:8000/pdf-to-word
- http://127.0.0.1:8000/word-to-pdf

## Notes About DOCX to PDF

DOCX to PDF conversion requires one of these tools on the host:

- Microsoft Word (used by docx2pdf)
- LibreOffice CLI (`soffice` command)

If neither is installed, the API returns a safe error message explaining what is missing.

## Scalability Notes

- Clear separation of concerns makes it easy to add future converters.
- Stateless API design is deployment-friendly.
- Temporary file usage is scoped and cleaned automatically.
- Validation and rate limiting reduce abuse risk.

## Deploy: GitHub Pages (Frontend) + Azure Web App (Backend)

This repository now includes CI/CD workflows:

- [deploy-frontend-gh-pages.yml](.github/workflows/deploy-frontend-gh-pages.yml)
- [deploy-backend-azure.yml](.github/workflows/deploy-backend-azure.yml)

### 1. Deploy Backend to Azure

1. Create an Azure Web App (Python 3.12, Linux recommended).
2. In Azure Web App, set startup command:

  ```bash
  python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
  ```

3. In Azure Web App > Environment variables, set:
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`
- `SENDER_EMAIL=memershaheer@gmail.com`
- `SENDER_PASSWORD=<your app password>`
- `FRONTEND_ORIGINS=https://<your-github-username>.github.io`
  If project site path is used, include full origin only (no path).

4. In GitHub repository secrets, add:
- `AZURE_WEBAPP_NAME`
- `AZURE_WEBAPP_PUBLISH_PROFILE`

5. Push to `main` (or run workflow manually) to deploy backend.

### 2. Deploy Frontend to GitHub Pages

1. In [frontend/assets/js/runtime-config.js](frontend/assets/js/runtime-config.js), set:

  ```javascript
  window.DOCUCONVERT_API_BASE_URL = "https://<your-azure-app>.azurewebsites.net";
  ```

2. In GitHub repo Settings > Pages:
- Source: GitHub Actions

3. Push to `main` (or run workflow manually) to deploy frontend.

### 3. Verify

1. Open your GitHub Pages URL.
2. Convert PDF/Word files.
3. Open Contact Us form and submit a message.
4. Confirm backend health at:

  ```
  https://<your-azure-app>.azurewebsites.net/health
  ```
