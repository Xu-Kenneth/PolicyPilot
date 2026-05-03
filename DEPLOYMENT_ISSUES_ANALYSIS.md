# PolicyPilot Deployment Issues - Diagnostic Report

**Date:** 2026-05-03  
**Status:** Critical Issues Found

---

## 🔴 Critical Issues

### 1. **Missing Streamlit Deployment Configuration**
- **Problem:** `railway.toml` only configures the FastAPI backend, not the Streamlit frontend
- **Impact:** Streamlit frontend never gets deployed to Railway
- **Solution:** Add Streamlit service configuration to `railway.toml`

### 2. **Streamlit Not in Root Requirements**
- **Problem:** Root `requirements.txt` doesn't include Streamlit or its dependencies
- **Impact:** Streamlit app won't be available during deployment
- **Solution:** Create/update `requirements-streamlit.txt` and reference it in deployment

### 3. **Hardcoded API URL**
- **Problem:** API URL hardcoded in `streamlit_app.py` to: `https://policypilot-production-1603.up.railway.app`
- **Impact:** 
  - Changes to backend URL require code changes
  - URL may be outdated
  - No fallback for environment variables
- **Solution:** Use environment variables properly with fallback

### 4. **Secrets Management Issue**
- **Problem:** `.streamlit/secrets.toml` contains hardcoded API URL - won't work in Railway
- **Impact:** Streamlit can't find backend in cloud environment
- **Solution:** Use Railway environment variables, not local secrets file

### 5. **CORS Configuration Problems**
- **Problem:** Backend CORS allows `localhost` but Railway uses different URLs
- **Impact:** Frontend can't reach backend from production
- **Solution:** Configure CORS to accept environment-based URLs

### 6. **Missing Streamlit Port Configuration**
- **Problem:** No port binding configuration for Streamlit in Railway
- **Impact:** Streamlit might not bind to the correct port ($PORT variable)
- **Solution:** Add Streamlit config to specify port

### 7. **Two Different Technology Stacks Mentioned**
- **Problem:** Documentation mentions Node.js/Express but code uses FastAPI/Python
- **Impact:** Confusing setup and potential misconfigurations
- **Solution:** Clarify that this is a Python project (FastAPI + Streamlit)

---

## 📋 Missing Files

- `requirements-streamlit.txt` - not found (referenced in STREAMLIT_README.md)
- `Procfile` - could help with deployment clarity
- `.streamlit/deployment.toml` - Production-specific Streamlit config

---

## 🔧 Required Fixes

### Fix 1: Update `railway.toml` for dual deployment
- Add Streamlit service configuration
- Ensure backend service is properly configured

### Fix 2: Create `requirements-streamlit.txt`
- Include Streamlit and all frontend dependencies

### Fix 3: Update `streamlit_app.py`
- Use environment variables properly with `os.getenv()`
- Support both local and Railway deployments

### Fix 4: Update backend `app/config.py`
- Configure CORS origins dynamically based on environment

### Fix 5: Add Streamlit production config
- Port configuration
- Memory settings
- Client settings for compatibility

### Fix 6: Create `.streamlit/deployment.toml`
- Production-specific Streamlit configuration

---

## ✅ Deployment Checklist

- [ ] Fix `railway.toml` for both services
- [ ] Create `requirements-streamlit.txt`
- [ ] Update `streamlit_app.py` for environment variables
- [ ] Update backend CORS configuration
- [ ] Add Streamlit production configuration
- [ ] Set Railway environment variables correctly
- [ ] Test local deployment first
- [ ] Test Railway staging deployment
- [ ] Verify CORS and API connectivity
