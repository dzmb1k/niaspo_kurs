# CI/CD Pipeline

## Overview
This project uses GitHub Actions for continuous integration and deployment.

## Pipeline Stages

### 1. **Lint** - Code Quality Check
- Runs `black` for code formatting
- Runs `isort` for import sorting
- Runs `flake8` for linting
- Ensures code meets quality standards

### 2. **Test** - Automated Testing
- Spins up PostgreSQL and Redis test databases
- Runs pytest with coverage reporting
- Tests all backend endpoints

### 3. **Build** - Docker Image Creation
- Builds Docker images for:
  - Backend (FastAPI)
  - Worker (Background tasks)
  - Nginx (Reverse proxy)
- Pushes images to GitHub Container Registry (ghcr.io)
- Uses layer caching for faster builds

### 4. **Security Scan** - Vulnerability Detection
- Scans codebase with Trivy
- Uploads results to GitHub Security tab
- Identifies security vulnerabilities

### 5. **Notify** - Status Reporting
- Reports overall build status
- Provides summary of all stages

## Triggers
- **Push** to `main` or `develop` branches
- **Pull Request** to `main` branch

## Image Tagging Strategy
- `latest` - Latest build from main branch
- `main` - All builds from main branch
- `develop` - All builds from develop branch
- `SHA` - Specific commit builds

## Local Testing

Run linting locally:
```bash
pip install flake8 black isort
black backend worker
isort backend worker
flake8 backend worker
```

Run tests locally:
```bash
cd backend
pip install -r requirements.txt pytest pytest-cov
pytest tests -v
```

Build images locally:
```bash
docker build -t ticketinghub-backend ./backend
docker build -t ticketinghub-worker ./worker
docker build -t ticketinghub-nginx ./nginx
```

## GitHub Container Registry

Images are automatically pushed to:
- `ghcr.io/dzmb1k/niaspo_kurs-backend`
- `ghcr.io/dzmb1k/niaspo_kurs-worker`  
- `ghcr.io/dzmb1k/niaspo_kurs-nginx`

Pull images:
```bash
docker pull ghcr.io/dzmb1k/niaspo_kurs-backend:latest
```
