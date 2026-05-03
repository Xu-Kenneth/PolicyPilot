# Railway Deployment Troubleshooting Guide

**For:** PolicyPilot Streamblit + FastAPI on Railway  
**Last Updated:** 2026-05-03

---

## 🚨 Top Issues & Solutions

### Issue #1: "❌ Backend API is unavailable" (Most Common)

**Symptoms:**
- Frontend loads but shows this message
- Can't upload/analyze files
- Red error in UI

**Root Causes:**

1. **Missing `API_BASE_URL` environment variable**
   ```bash
   # Check in Railway Dashboard
   # Frontend Service → Variables → Look for API_BASE_URL
   ```
   - **Fix:** Add `API_BASE_URL` with full URL of backend:
     ```
     API_BASE_URL=https://policypilot-backend-production-1234.up.railway.app
     ```

2. **Wrong backend URL format**
   - **Wrong:** `http://localhost:8000` (localhost only works locally)
   - **Wrong:** `backend` or `backend.local` (not accessible from Railway)
   - **Correct:** `https://xxx-backend-production-xxxx.up.railway.app`

3. **Backend service isn't running**
   - **Check:** Railway Dashboard → backend service → Deployments
   - **Fix:** Redeploy backend or check logs for errors

4. **CORS blocking the request**
   - **Check:** Browser DevTools → Network tab → failed request
   - **Look for:** `Cross-Origin Request Blocked` error
   - **Fix:** Add frontend URL to backend CORS (requires code change + redeploy)

**Debug Steps:**
```bash
# 1. Check if backend is reachable
curl https://xxx-backend-production-xxxx.up.railway.app/api/health

# 2. Check frontend logs
railway logs frontend --follow
# Look for: "Connection refused", "timeout", "No address associated"

# 3. Check backend logs
railway logs backend --follow
# Look for: "CORS error", "Connection from"
```

**Solution Checklist:**
- [ ] Backend URL is complete: `https://xxx-production-xxxx.up.railway.app`
- [ ] No special characters or typos in URL
- [ ] `API_BASE_URL` is set in frontend service variables
- [ ] Backend service status is "running" (green)
- [ ] Restart frontend service after changing variables

---

### Issue #2: Frontend Service Won't Start / Crashes

**Symptoms:**
- Frontend service shows "Failed" or "Crashed" status
- Deployment gets stuck or times out
- Service keeps restarting

**Root Causes:**

1. **`streamlit` not installed**
   ```bash
   # Check logs for:
   # "ModuleNotFoundError: No module named 'streamlit'"
   ```
   - **Fix:** Ensure `requirements-streamlit.txt` exists in root directory

2. **Wrong start command**
   - **Wrong:** `streamlit run streamlit_app.py` (doesn't use Railway port)
   - **Correct:** `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Check:** `railway.toml` has correct command for frontend service

3. **Port binding issues**
   - **Current:** Streamlit tries to use port 8501, but Railway assigns `$PORT`
   - **Fix:** Always use `--server.port=$PORT`

4. **Missing dependencies**
   ```bash
   # Check logs for:
   # "ModuleNotFoundError" for pandas, requests, plotly, etc.
   ```
   - **Fix:** Verify `requirements-streamlit.txt` has all dependencies

**Debug Steps:**
```bash
# 1. Check frontend logs
railway logs frontend --follow

# 2. Look for the actual error (usually near the end)

# 3. Common log patterns:
# SUCCESS: "You can now view your Streamlit app in your browser"
# ERROR: "Address already in use"
# ERROR: "ModuleNotFoundError"
# ERROR: "Address [...] is not assignable to"
```

**Solution Checklist:**
- [ ] `requirements-streamlit.txt` exists in root with all packages
- [ ] Start command in `railway.toml` uses `--server.port=$PORT`
- [ ] No typos in `streamlit_app.py` filename
- [ ] `.streamlit/config.toml` exists and is valid TOML
- [ ] Restart service or redeploy after fixes

---

### Issue #3: Port Binding / "Address Already in Use"

**Symptoms:**
- Log shows: `"Address already in use"` or `"Bind: address already in use"`
- Service won't start
- Timeout on deployment

**Root Causes:**

1. **Hardcoded port instead of `$PORT` variable**
   - **Wrong:** `streamlit run streamlit_app.py --server.port=8501`
   - **Correct:** `streamlit run streamlit_app.py --server.port=$PORT`

2. **Duplicate services trying to use same port**
   - Check `railway.toml` - shouldn't have both services on port 8000

3. **`config.toml` overriding command-line settings**
   ```toml
   # .streamlit/config.toml
   [server]
   port = 8501  # ← This can conflict!
   ```
   - **Fix:** Remove port from config.toml in production, let `$PORT` variable handle it

**Debug Steps:**
```bash
# Check what port Railway assigned
railway logs frontend --follow
# Look for: "Listening on http://0.0.0.0:12345"

# Verify the configuration
cat railway.toml
# Should show: --server.port=$PORT for Streamlit
```

**Solution Checklist:**
- [ ] Start command uses `--server.port=$PORT`
- [ ] `.streamlit/config.toml` doesn't hardcode port (or uses `$PORT`)
- [ ] Only ONE service per port in `railway.toml`
- [ ] Redeploy after fixing configuration

---

### Issue #4: CORS Errors (Backend Blocks Frontend)

**Symptoms:**
- Browser console shows:
  ```
  Access to XMLHttpRequest at 'https://xxx-backend...' from origin 
  'https://xxx-frontend...' has been blocked by CORS policy
  ```
- Frontend receives `null` responses
- API calls fail silently

**Causes:**
- Frontend URL not in backend CORS allow list
- Backend CORS configuration too restrictive

**Debug Steps:**
```bash
# 1. Test CORS manually
curl -H "Origin: https://xxx-frontend.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     https://xxx-backend.up.railway.app/api/health

# 2. Check backend CORS config
# Backend code in app/main.py should have:
# - Your frontend URL in allow_origins list
# - ENVIRONMENT=production set

# 3. Check backend logs
railway logs backend --follow
# Look for CORS-related errors
```

**Solution Options:**

**Option A: For Quick Fix (Development)**
```python
# In backend/app/main.py - NOT RECOMMENDED for production
allow_origins=["*"]  # Allow all (less secure)
```

**Option B: Proper Fix (Recommended)**
```python
# In backend/app/main.py
def get_cors_origins():
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return [
            os.getenv("FRONTEND_URL"),
            "https://xxx-frontend-production-xxxx.up.railway.app",
            "https://*.up.railway.app",
        ]
    else:
        return ["*"]
```

Then set `FRONTEND_URL` as backend environment variable.

**Solution Checklist:**
- [ ] Frontend URL added to backend CORS allow list
- [ ] Backend redeployed with new CORS config
- [ ] `ENVIRONMENT=production` set in backend
- [ ] Refresh browser to clear any cached CORS responses

---

### Issue #5: Timeouts / Slow Performance

**Symptoms:**
- Requests take 30+ seconds
- Upload/Analysis hangs
- "Request timed out" errors

**Root Causes:**

1. **Not enough memory allocated**
   - Railway default: 512MB
   - Streamlit + file processing needs ~1GB minimum
   - **Fix:** Upgrade Railway plan

2. **Large file uploads**
   - **Check:** `backend/app/config.py` - `max_upload_size`
   - Default: 100MB
   - **Cause:** Network latency, processing time
   - **Fix:** Test with smaller files first (< 10MB)

3. **Network connection issues**
   - **Check:** Both services on same Railway project (should be milliseconds)
   - **Fix:** Move to faster Railway region if needed

4. **Backend process running out of memory**
   - **Logs show:** `MemoryError` or service restart
   - **Fix:** Upgrade plan or optimize file processing

**Debug Steps:**
```bash
# Check memory usage
railway logs backend --follow
# Look for warnings about memory

# Test locally with same files
# If it's fast locally but slow on Railway → likely resource issue

# Check if requests are actually hanging or just slow
# In browser DevTools → Network tab → check request timing
```

**Solution Checklist:**
- [ ] Start with smaller test files (< 10MB)
- [ ] Check Railway metrics for CPU/Memory usage
- [ ] Consider upgrading Railway plan if needed
- [ ] Optimize file processing if possible (filter by file type)

---

### Issue #6: "Invalid Request" / 422 Errors

**Symptoms:**
```json
{
  "detail": [
    {
      "loc": ["body"],
      "msg": "A single Pydantic model instance is expected",
      "type": "type_error.parse_error"
    }
  ]
}
```

**Root Causes:**
1. Wrong content-type header
2. Malformed JSON in request body
3. API contract mismatch between frontend/backend

**Solution:**
- Check `streamlit_app.py` API calls
- Verify `Content-Type: application/json` headers
- Test API manually:
  ```bash
  curl -X POST https://xxx-backend.up.railway.app/api/analyze \
    -H "Content-Type: application/json" \
    -d '{"upload_id": "123", "project_name": "test"}'
  ```

---

## 🔍 Diagnosis Workflow

When something isn't working:

```
1. CHECK LOGS FIRST
   a. Backend: railway logs backend --follow
   b. Frontend: railway logs frontend --follow
   c. Look for: ERROR, exception, failed

2. VERIFY CONFIGURATION
   a. Environment variables set correctly
   b. Start commands are correct
   c. File paths are correct

3. TEST CONNECTIVITY
   a. Can you curl the backend from somewhere?
   b. Can frontend see backend?
   c. Are there network errors?

4. RESTART & REDEPLOY
   a. Restart services in Railway Dashboard
   b. Or redeploy: git push to trigger new build
   c. Check if that fixes it

5. IF STILL BROKEN
   a. Review error messages carefully
   b. Check Railway documentation
   c. Search GitHub issues
```

---

## 📋 Pre-Deployment Verification

Before deploying, run locally:

```bash
# 1. Start backend
cd backend
python run.py
curl http://localhost:8000/api/health
# Should get: {"status":"healthy"}

# 2. In another terminal, start frontend
streamlit run streamlit_app.py
# Should see: "You can now view your Streamlit app"

# 3. Open http://localhost:8501
# Should see: "✅ Backend API is healthy"

# 4. Try uploading a file
# Should complete without errors

# 5. If all works locally, safe to deploy
git push origin main
```

---

## 💡 Useful Railway Commands

```bash
# View all logs
railway logs --follow

# View specific service logs
railway logs backend --follow
railway logs frontend --follow

# View deployment status
railway services

# Check environment variables
railway variables

# Restart a service
railway restart backend
# or in Dashboard: click service → Restart

# Open service dashboard
railway open
```

---

## 🆘 Still Not Working?

### Gather Information
1. Error logs (copy full error messages)
2. Screenshots of Railway Dashboard
3. What exactly is broken (upload? analyze? download?)
4. When it breaks (on startup? after 10 seconds?)

### Get Help
1. Check Railway docs: https://docs.railway.app/
2. Search this guide for your error message
3. Check GitHub issues for similar problems
4. Railway support team

### Emergency: Roll Back

If deployment broke everything:
```bash
# Go back to previous commit
git revert HEAD
git push origin main
# Railway will auto-deploy previous version
```

---

## ✅ Success Indicators

Your deployment is working when:
- ✅ Frontend loads without errors
- ✅ Shows "✅ Backend API is healthy"
- ✅ Can upload files
- ✅ Can analyze files
- ✅ Can download reports
- ✅ No errors in browser console
- ✅ No errors in Railway logs
- ✅ Fast response times (< 5 seconds for analysis)

---

**Last Resort:** Completely rebuild from scratch on Railway:
1. Create new Railway project
2. Reconnect GitHub repo
3. Start fresh deployment
4. Set environment variables again
5. This often fixes mysterious issues!
