# VayuCheck+ 🌀

**AI-Powered Air Quality & Health Companion**

A modern web application that monitors air quality and provides personalized health advice using AI.

## 🚀 Quick Start

### Option 1: One-Click Start (Recommended)
```bash
# Install dependencies (first time only)
npm run install:all

# Start both backend and frontend
npm run dev
```

### Option 2: Windows Batch File
Double-click `start-dev.bat` to start both servers in separate windows.

### Option 3: PowerShell Script
Right-click `start-dev.ps1` and select "Run with PowerShell" to start both servers.

### Option 4: Manual Start
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🛠️ Available Scripts

- `npm run dev` - Start both backend and frontend
- `npm run dev:backend` - Start only backend
- `npm run dev:frontend` - Start only frontend
- `npm run install:all` - Install all dependencies
- `npm run build` - Build frontend for production

## 🏗️ Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: MongoDB
- **AI**: Rule-based health advice system

## 👨‍💻 Developer

**KAPIL CHOUDHARY**

---

*Built with ❤️ for better air quality and health monitoring* 