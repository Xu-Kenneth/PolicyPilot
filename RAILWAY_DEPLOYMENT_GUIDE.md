# PolicyPilot Railway Deployment Guide

**Last Updated:** 2026-05-03  
**Status:** Updated with fixes for dual deployment

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Testing](#local-testing)
3. [Railway Setup](#railway-setup)
4. [Environment Variables](#environment-variables)
5. [Deployment Steps](#deployment-steps)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring](#monitoring)

---

## ✅ Pre-Deployment Checklist

- [ ] Both `requirements.txt` and `requirements-streamlit.txt` are updated
- [ ] `.streamlit/config.toml` and `.streamlit/secrets.toml` are configured
- [ ] `streamlit_app.py` uses environment variables correctly
- [ ] Backend CORS is configured for your frontend URLs
- [ ] `railway.toml` has both backend and frontend services
- [ ] All tests pass locally
- [ ] No sensitive data in code or version control

---

## 🏠 Local Testing

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
pip install -r requirements-streamlit.txt
```

### 2. Start Backend

```bash
cd backend
python run.py
# Should see: "Uvicorn running on http://127.0.0.1:8000"
```

### 3. In Another Terminal, Start Frontend

```bash
streamlit run streamlit_app.py
# Should see: "You can now view your Streamlit app in your browser."
```

### 4. Test API Connectivity

- Open Streamlit app at `http://localhost:8501`
- You should see "✅ Backend API is healthy" message
- Try uploading a file to test the full flow

---

## 🚀 Railway Setup

### Step 1: Create Railway Project

```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init
```

### Step 2: Connect Git Repository

In Railway Dashboard:
- Click "Create New Project"
- Select "Deploy from GitHub"
- Authorize Railway with GitHub
- Select your repository
- Click "Deploy Now"

### Step 3: Configure Services

You should have two services after updating `railway.toml`:

#### Backend Service
- **Build:** Automatic from `Dockerfile`
- **Start Command:** `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Port:** `8000`

#### Frontend Service
- **Build:** Automatic
- **Start Command:** `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
- **Port:** `8501` (or assigned by Railway)

---

## 🔐 Environment Variables

### Railway Dashboard Setup

In Railway Dashboard, go to each service and add these environment variables:

#### Backend Service Variables

```
ENVIRONMENT=production
DEBUG=false
```

#### Frontend Service Variables

```
ENVIRONMENT=production
API_BASE_URL=https://your-backend-service.up.railway.app
```

**Important:** Replace `your-backend-service` with your actual Railway backend service URL.

### Getting Your Service URLs

In Railway Dashboard:
1. Go to "Deployments"
2. Each service will have a unique URL: `https://[service-name]-production-xxxx.up.railway.app`
3. Copy the backend URL and set it as `API_BASE_URL` in the frontend service

---

## 🚀 Deployment Steps

### Step 1: Push to Main Branch

```bash
git add .
git commit -m "fix: update deployment configuration for Railway"
git push origin main
```

### Step 2: Railway Auto-Deploy

Railway automatically deploys when you push to your connected GitHub branch. Watch the deployment:

1. Go to Railway Dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Click on the latest deployment to see logs

### Step 3: Verify Deployment

```bash
# Check backend health
curl https://[backend-service-url].up.railway.app/api/health

# Check frontend
Visit https://[frontend-service-url].up.railway.app in browser
```

---

## 🔧 Troubleshooting

### Issue: Frontend shows "❌ Backend API is unavailable"

**Causes:**
- API_BASE_URL environment variable not set
- Backend service URL is incorrect
- CORS not properly configured

**Solutions:**
1. Verify `API_BASE_URL` environment variable in Railway dashboard
2. Check backend service URL: `railway logs backend` to see startup logs
3. Ensure backend CORS includes your frontend URL
4. Test manually: 
   ```bash
   curl -H "Origin: https://[frontend-url]" https://[backend-url]/api/health
   ```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Cause:** `requirements-streamlit.txt` not being installed

**Solutions:**
1. Ensure `requirements-streamlit.txt` exists in root directory
2. Check Railway logs: `railway logs frontend`
3. Verify start command includes installing requirements before running app
4. Add `pip install -r requirements-streamlit.txt` to your Dockerfile if needed

### Issue: Port Already in Use / Binding Issues

**Cause:** Streamlit trying to use fixed port instead of $PORT variable

**Solutions:**
1. Verify start command uses `--server.port=$PORT`
2. Check `.streamlit/config.toml` isn't hardcoding port in production
3. View logs: `railway logs frontend --follow`

### Issue: Timeouts / Slow Performance

**Causes:**
- Large file uploads
- Memory limits
- Network latency

**Solutions:**
1. Check memory usage: `railway logs [service] --follow`
2. Increase Railway plan if hitting memory limits
3. Enable compression in `.streamlit/config.toml`:
   ```toml
   enableWebsocketCompression = true
   ```
4. Test with smaller files first

### Issue: "Access Denied" errors

**Cause:** CORS rejection

**Solutions:**
1. Check backend CORS configuration in `app/main.py`
2. Verify frontend URL matches CORS allow list
3. Check browser console for CORS errors:
   - Open DevTools (F12)
   - Go to Console tab
   - Look for cross-origin errors
4. Add frontend URL to CORS:
   ```python
   allow_origins=[
       "https://your-frontend-url.up.railway.app",
       ...
   ]
   ```

---

## 📊 Monitoring

### View Logs

```bash
# Backend logs
railway logs backend --follow

# Frontend logs
railway logs frontend --follow

# Both
railway logs --follow
```

### Monitor Deployments

In Railway Dashboard:
- **Deployments:** See all deployments and their status
- **Logs:** Real-time logs for debugging
- **Metrics:** CPU, Memory, Network usage
- **Domain:** Configure custom domains

### Common Log Messages

#### Backend
- ✅ `"INFO:     Uvicorn running on http://0.0.0.0:8000"` - Backend started correctly
- ⚠️ `"ERROR: Permission denied"` - File permissions issue
- ⚠️ `"ERROR: Module not found"` - Missing dependency

#### Frontend
- ✅ `"Collecting streamlit"` / `"Successfully installed"` - Dependencies installing
- ✅ `"You can now view your Streamlit app"` - Frontend started
- ⚠️ `"Connection refused"` - Can't reach backend (check API_BASE_URL)

---

## 📞 Support & Further Help

### Quick Fixes

1. **Restart services:** In Railway Dashboard, click the service and select "Restart"
2. **Clear cache:** Stop the service and redeploy
3. **Check environment:** Click on service to view all environment variables

### Documentation References

- [Railway Documentation](https://docs.railway.app/)
- [Streamlit Deployment Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Debug Environment Variables

Add this to `streamlit_app.py` temporarily to verify config:

```python
import os
st.sidebar.write("### Debug Info")
st.sidebar.write(f"API URL: {os.getenv('API_BASE_URL', 'NOT SET')}")
st.sidebar.write(f"Environment: {os.getenv('ENVIRONMENT', 'local')}")
```

---

## 🎯 Next Steps After Deployment

1. ✅ Test full workflow (upload → analyze → download report)
2. ✅ Monitor error logs for first 24 hours
3. ✅ Set up alerts for deployment failures
4. ✅ Document your deployed URLs for the team
5. ✅ Configure custom domain (optional)
6. ✅ Set up backup/recovery procedures
