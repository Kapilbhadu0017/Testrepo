# VayuCheck+ 🌀

**AI-Powered Air Quality & Health Companion**

A modern, full-stack web application that monitors real-time air quality and provides personalized health advice using the Google Gemini AI.

---

## 🛠️ Tech Stack

-   **Frontend**: React, Vite, Tailwind CSS, Leaflet
-   **Backend**: FastAPI (Python)
-   **Database**: MongoDB
-   **AI**: Google Gemini

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed on your system:

-   [Node.js](https://nodejs.org/) (which includes npm)
-   [Python](https://www.python.org/downloads/)

---

## 🚀 Getting Started

Follow these steps to get your local development environment running.

### 1. Clone the Repository

First, get a copy of the project on your machine.
```bash
git clone [https://github.com/Kapilbhadu0017/Testrepo.git](https://github.com/Kapilbhadu0017/Testrepo.git)
cd Testrepo

### 2. Configure API Keys

The backend needs API keys to function.

1.  In the `backend` folder, rename the file `env.example` to `.env`.
2.  Open the new `.env` file and add your actual API keys. You will need keys for:
      - `GEMINI_API_KEY` (from Google AI Studio)
      - `WAQI_TOKEN` (from the World Air Quality Index Project)
      - `AIRNOW_API_KEY` (from AirNow)
      - `MONGODB_URL` (from your MongoDB Atlas cluster)

### 3. Install All Dependencies

This project has both Node.js (frontend) and Python (backend) dependencies. Run the following commands from the **main project folder**:

```bash
# Install all frontend packages
npm run install:all

# Install all backend packages
pip install -r backend/requirements.txt
```

### 4. Run the Application

This single command starts both the backend and frontend servers at the same time.

```bash
npm run dev
```

-----

## 🌐 Access Points

Once the application is running, you can access it at the following URLs:

  - **Frontend Website**: [http://localhost:5173](https://www.google.com/search?q=http://localhost:5173)
  - **Backend API Docs**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

-----

## 👨‍💻 Developer

**KAPIL CHOUDHARY**

*Built with ❤️ for better air quality and health monitoring*
