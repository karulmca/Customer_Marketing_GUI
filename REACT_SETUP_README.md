# Company Data Scraper - React + FastAPI Architecture

## 🎯 Overview

This is a modern web application that replaces the Tkinter GUI with a React frontend and FastAPI backend, providing a better user experience while keeping all existing Python functionality intact.

## 🏗️ Architecture

```
📁 Project Structure
├── 🐍 backend_api/          # FastAPI backend
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── ⚛️ frontend/             # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.js          # Main app component
│   ├── public/             # Static files
│   └── package.json        # Node.js dependencies
├── 🗃️ auth/                # Existing authentication (unchanged)
├── 💾 database_config/     # Existing database logic (unchanged)
├── 🔧 gui/                 # Legacy Tkinter GUIs (still available)
└── 📊 scrapers/            # Existing scraping logic (unchanged)
```

## ✨ Features

### 🔐 Authentication
- **Login/Register**: Modern Material-UI forms
- **Session Management**: Secure token-based authentication
- **User Info Display**: Welcome messages and user context

### 📁 File Upload
- **Drag & Drop**: Modern file upload interface
- **File Preview**: Table preview with column analysis
- **File Validation**: Excel file type and size validation
- **Progress Tracking**: Real-time upload progress

### ⚙️ Processing
- **Background Processing**: Non-blocking file processing
- **Real-time Status**: Live progress updates
- **Processing Options**: Enable/disable scraping and AI analysis
- **Results Display**: Detailed processing results

### 🎨 UI/UX
- **Material-UI Design**: Modern, responsive interface
- **Dark/Light Theme**: Professional appearance
- **Mobile Responsive**: Works on all devices
- **Real-time Notifications**: Success/error messages

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Setup (Automated)
```bash
# Windows
setup_react_app.bat

# Linux/Mac
bash setup_react_app.sh
```

### 2. Manual Setup
```bash
# Install Python backend dependencies
cd backend_api
pip install -r requirements.txt

# Install React frontend dependencies
cd ../frontend
npm install
```

### 3. Run Application
```bash
# Option 1: Run both together (Windows)
run_react_app.bat

# Option 2: Run separately
# Terminal 1 - FastAPI Backend
python backend_api/main.py

# Terminal 2 - React Frontend
cd frontend
npm start
```

### 4. Access Application
- **React Frontend**: http://localhost:3000
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
Create `.env` file in the root directory:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/company_scraper
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=company_scraper
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# API Configuration
API_SECRET_KEY=your-secret-key-here
API_ALGORITHM=HS256
```

### FastAPI Configuration
The FastAPI backend automatically connects to your existing:
- PostgreSQL database
- Authentication system
- File processing logic
- Scraping functionality

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### File Operations
- `POST /api/files/upload` - Upload Excel file
- `POST /api/files/process/{file_id}` - Start file processing
- `GET /api/files/status/{file_id}` - Get processing status

### System
- `GET /api/database/status` - Check database connection
- `GET /api/health` - Health check

## 🎨 Frontend Components

### LoginForm
- Material-UI login interface
- Form validation
- Registration modal
- Error handling

### FileUploadDashboard
- Drag & drop file upload
- File preview with data analysis
- Processing status with progress bars
- Results display
- Database status monitoring

## 🔄 Migration from Tkinter

### What's Changed
- **UI Framework**: Tkinter → React + Material-UI
- **Architecture**: Desktop app → Web application
- **API Layer**: Direct calls → REST API via FastAPI

### What's Unchanged
- **Database Logic**: All PostgreSQL operations remain the same
- **Authentication**: Existing user authentication system
- **File Processing**: All scraping and data processing logic
- **Configuration**: Same .env and config files

### Benefits
- **Better UX**: Modern, responsive interface
- **Scalability**: Web-based, multi-user capable
- **Maintainability**: Separated frontend and backend
- **Accessibility**: Works on any device with a browser

## 🛠️ Development

### Adding New Features

1. **Backend (FastAPI)**:
   ```python
   # Add new endpoint in backend_api/main.py
   @app.post("/api/new-feature")
   async def new_feature(data: FeatureRequest):
       # Your existing Python logic here
       return {"result": "success"}
   ```

2. **Frontend (React)**:
   ```javascript
   // Add new service in src/services/
   export const NewFeatureService = {
     async callFeature(data) {
       const response = await api.post('/new-feature', data);
       return response.data;
     }
   };
   ```

### Testing
```bash
# Backend tests
cd backend_api
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Production Build
```bash
# Build React frontend
cd frontend
npm run build

# Run FastAPI with production settings
cd ../backend_api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM node:16 as frontend-builder
COPY frontend/ /app/frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

FROM python:3.9
COPY backend_api/ /app/backend_api/
COPY --from=frontend-builder /app/frontend/build /app/static/
WORKDIR /app
RUN pip install -r backend_api/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Keep existing Python logic intact
2. Follow React best practices
3. Use Material-UI components
4. Add proper error handling
5. Update API documentation

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)
- [Axios HTTP Client](https://axios-http.com/)

## 🆚 Legacy Support

The original Tkinter GUI remains available:
```bash
# Run original Tkinter GUI
python gui/login_gui.py
python gui/file_upload_json_gui.py
```

This ensures backward compatibility while you transition to the new React interface.

---

**🎉 Your Python backend logic remains 100% unchanged - we've just given it a modern web interface!**