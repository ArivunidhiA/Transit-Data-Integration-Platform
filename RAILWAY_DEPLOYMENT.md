# Railway Unified Deployment Guide

Deploy both frontend and backend together on Railway in one project.

## Prerequisites

1. GitHub account and repository
2. Railway account ([Sign up here](https://railway.app/) - free tier available)
3. MBTA API key ([Get one here](https://api-v3.mbta.com/register))

## Step 1: Create Railway Project

1. **Go to Railway Dashboard**
   - Visit [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select repository: `ArivunidhiA/Transit-Data-Integration-Platform`

## Step 2: Deploy Backend Service

1. **Add Backend Service**
   - In your Railway project, click "+ New"
   - Select "GitHub Repo" → Choose your repository
   - Railway will auto-detect it's a Python project

2. **Configure Backend Service**
   - **Service Name**: `mbta-backend`
   - **Root Directory**: `backend`
   - **Build Command**: (Auto-detected) `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - Click on the service → "Variables" tab
   - Add these variables:
     ```
     MBTA_API_KEY=your_mbta_api_key_here
     DATABASE_URL=sqlite:///./data/mbta_telemetry.db
     CORS_ORIGINS=*
     LOG_LEVEL=INFO
     PORT=8000
     ```

4. **Generate Public URL**
   - Click "Settings" → "Generate Domain"
   - Note your backend URL (e.g., `https://mbta-backend-production.up.railway.app`)

## Step 3: Deploy Frontend Service

1. **Add Frontend Service**
   - In the same Railway project, click "+ New" again
   - Select "GitHub Repo" → Choose the same repository
   - Railway will detect it's a Node.js project

2. **Configure Frontend Service**
   - **Service Name**: `mbta-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s dist -l $PORT`

3. **Set Environment Variables**
   - Click on the service → "Variables" tab
   - Add this variable (use your backend URL from Step 2):
     ```
     VITE_API_URL=https://mbta-backend-production.up.railway.app
     PORT=3000
     ```

4. **Generate Public URL**
   - Click "Settings" → "Generate Domain"
   - Note your frontend URL (e.g., `https://mbta-frontend-production.up.railway.app`)

## Step 4: Update CORS Configuration

1. **Update Backend CORS**
   - Go to backend service → "Variables"
   - Update `CORS_ORIGINS` to include your frontend URL:
     ```
     CORS_ORIGINS=https://mbta-frontend-production.up.railway.app,http://localhost:3000
     ```
   - Railway will automatically redeploy

## Step 5: Verify Deployment

### Backend Health Check
Visit: `https://your-backend-url.up.railway.app/health`

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  ...
}
```

### Frontend Verification
1. Visit your frontend URL
2. Check that the Overview page loads
3. Verify API calls are working (check browser console)
4. Test the Live Map page

## Step 6: Enable Continuous Deployment

Railway automatically deploys on push to your main branch by default.

- **Automatic deploys**: Enabled by default
- **Preview deployments**: Created for pull requests
- **Branch deploys**: Can be configured in service settings

## Alternative: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project or create new
railway link

# Deploy backend
cd backend
railway up

# Deploy frontend (in new terminal)
cd frontend
railway up
```

## Environment Variables Summary

### Backend Service
| Variable | Value | Required |
|----------|-------|----------|
| `MBTA_API_KEY` | Your MBTA API key | ✅ Yes |
| `DATABASE_URL` | `sqlite:///./data/mbta_telemetry.db` | ❌ No (default) |
| `CORS_ORIGINS` | Your frontend URL | ✅ Yes |
| `LOG_LEVEL` | `INFO` | ❌ No |
| `PORT` | `8000` | ✅ Yes (auto-set) |

### Frontend Service
| Variable | Value | Required |
|----------|-------|----------|
| `VITE_API_URL` | Your backend URL | ✅ Yes |
| `PORT` | `3000` | ✅ Yes (auto-set) |

## Troubleshooting

### Backend Issues

**Service won't start:**
- Check logs in Railway dashboard
- Verify `MBTA_API_KEY` is set correctly
- Ensure `PORT` environment variable is set (Railway sets this automatically)

**Database errors:**
- SQLite databases persist on Railway
- For production, consider upgrading to Railway PostgreSQL

**CORS errors:**
- Verify `CORS_ORIGINS` includes your frontend URL exactly
- Check that frontend URL has no trailing slash

### Frontend Issues

**Build fails:**
- Check build logs in Railway dashboard
- Ensure `VITE_API_URL` is set correctly
- Verify Node.js version (Railway auto-detects)

**API connection errors:**
- Verify `VITE_API_URL` matches your backend URL exactly
- Check that backend is accessible and healthy
- Verify CORS is configured correctly

**404 errors on routes:**
- Railway serves static files correctly
- Ensure build output is in `dist` directory

## Cost Considerations

### Railway Free Tier
- **$5 credit/month** (enough for small projects)
- **500 hours/month** of usage
- **100GB bandwidth/month**
- **1GB storage**

### Paid Plans
- **Starter**: $5/month + usage
- **Developer**: $20/month + usage
- **Team**: Custom pricing

For production use, the free tier is usually sufficient for development and small projects.

## Production Checklist

- [ ] Backend service deployed on Railway
- [ ] Frontend service deployed on Railway
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] Health check endpoint working
- [ ] Frontend can communicate with backend
- [ ] Database initialized
- [ ] Telemetry collector running (check logs)
- [ ] Both services have public domains
- [ ] Continuous deployment enabled

## Benefits of Unified Deployment

✅ **Single Platform**: Manage both services in one place
✅ **Simplified CORS**: Both services on same platform, easier configuration
✅ **Unified Logs**: View logs for both services in one dashboard
✅ **Cost Effective**: One platform, one bill
✅ **Easy Updates**: Update both services together
✅ **Better Integration**: Services can communicate internally

---

**Need Help?** Check Railway docs: https://docs.railway.app/

