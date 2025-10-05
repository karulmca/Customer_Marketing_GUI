# Render Deployment Guide

This guide explains how to deploy the Company Data Scraper application to Render.com using the `render.yaml` configuration.

## 🚀 Quick Deployment

### Step 1: Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository: `karulmca/Customer_Marketing_GUI`
4. Select the `master` branch
5. Render will automatically detect the `render.yaml` file

### Step 2: Configure Environment Variables
Before deployment, you need to set up your database connection:

#### Option A: Use External Database (Recommended)
If you have an existing PostgreSQL database (like Neon, Supabase, or Railway):

1. In the backend service settings, update the `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

#### Option B: Use Render PostgreSQL
1. Create a separate PostgreSQL service in Render
2. Update the `render.yaml` to reference the managed database
3. Set the connection details in environment variables

### Step 3: Deploy
1. Click "Create Blueprint"
2. Render will automatically:
   - Build the backend Docker container
   - Build the React frontend
   - Deploy both services
   - Set up health checks

## 📋 Services Created

The `render.yaml` will create:

1. **Backend API Service** (`company-scraper-backend`)
   - Docker-based Python/FastAPI application
   - Health check endpoint: `/health`
   - Environment: Production

2. **Frontend Service** (`company-scraper-frontend`)
   - Static React application
   - Automatically builds from `frontend/` directory
   - Configured to proxy API calls to backend

## 🔧 Configuration Details

### Backend Environment Variables
- `ENVIRONMENT=production`
- `SECRET_KEY` (auto-generated)
- `DATABASE_URL` (needs to be configured)

### Frontend Environment Variables
- `REACT_APP_API_URL` (automatically set to backend URL)

## 🌐 Access Your Application

After successful deployment:
- **Frontend**: `https://company-scraper-frontend.onrender.com`
- **Backend API**: `https://company-scraper-backend.onrender.com`
- **API Docs**: `https://company-scraper-backend.onrender.com/docs`

## 🔍 Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Ensure `DATABASE_URL` is correctly set
   - Check database credentials and network access

2. **Build Fails**
   - Check build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`

3. **Frontend Can't Connect to Backend**
   - Verify `REACT_APP_API_URL` is correctly set
   - Check CORS settings in backend

### Logs and Monitoring:
- View logs in Render dashboard
- Backend health check: `GET /health`
- Monitor resource usage in Render metrics

## 💡 Production Considerations

### Database Setup:
For production, consider using:
- **Neon** (PostgreSQL) - Free tier available
- **Supabase** (PostgreSQL) - Free tier available  
- **Render PostgreSQL** - Paid service
- **Railway** (PostgreSQL) - Free tier available

### Performance:
- Backend starts with 1 worker (can be scaled)
- Frontend is served as static files (fast delivery)
- Health checks ensure service availability

### Cost:
- Free tier available for both services
- Automatic scaling based on usage
- Pay only for what you use

## 🔄 Updates and Maintenance

### Automatic Deployments:
- Connected to GitHub `master` branch
- Auto-deploys on git push
- Build status notifications

### Manual Updates:
1. Update code in repository
2. Push to `master` branch
3. Render automatically rebuilds and deploys

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test database connectivity
4. Review build logs for errors

For Render-specific issues, consult [Render Documentation](https://render.com/docs).