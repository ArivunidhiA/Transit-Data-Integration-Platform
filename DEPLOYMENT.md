# Deployment Guide

This guide will walk you through deploying the MBTA Transit Telemetry Platform to production.

## Prerequisites

1. GitHub account and repository
2. Render account (free tier) for backend
3. Netlify account (free tier) for frontend
4. MBTA API key ([Get one here](https://api-v3.mbta.com/register))

## Step 1: Backend Deployment (Render)

### Option A: Using Render Dashboard

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

2. **Configure Service**
   - **Name**: `mbta-telemetry-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   MBTA_API_KEY=your_mbta_api_key_here
   DATABASE_URL=sqlite:///./data/mbta_telemetry.db
   CORS_ORIGINS=https://your-frontend.netlify.app,http://localhost:3000
   LOG_LEVEL=INFO
   ```

4. **Advanced Settings**
   - **Health Check Path**: `/health`
   - **Health Check Interval**: 60 seconds
   - **Auto-Deploy**: Yes (deploy on push to main branch)

5. **Create Service**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://mbta-telemetry-backend.onrender.com`)

### Option B: Using render.yaml

1. The `backend/render.yaml` file is already configured
2. Simply push your code to GitHub
3. Render will automatically detect and deploy using the YAML configuration

## Step 2: Frontend Deployment (Netlify)

### Option A: Using Netlify Dashboard

1. **Create New Site**
   - Go to [Netlify Dashboard](https://app.netlify.com/)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository
   - Select the repository

2. **Configure Build Settings**
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`

3. **Set Environment Variables**
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

4. **Deploy**
   - Click "Deploy site"
   - Wait for deployment to complete
   - Note your frontend URL (e.g., `https://your-app.netlify.app`)

### Option B: Using Netlify CLI

```bash
cd frontend
npm install
npm run build

# Install Netlify CLI
npm install -g netlify-cli

# Login and deploy
netlify login
netlify deploy --prod
```

## Step 3: Update CORS Configuration

After deploying the frontend, update the backend CORS_ORIGINS environment variable:

1. Go to Render Dashboard → Your Backend Service → Environment
2. Update `CORS_ORIGINS` to include your Netlify URL:
   ```
   CORS_ORIGINS=https://your-frontend.netlify.app,http://localhost:3000
   ```
3. Redeploy the backend service

## Step 4: Verify Deployment

### Backend Health Check

Visit your backend URL + `/health`:
```
https://your-backend.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  ...
}
```

### Frontend Verification

1. Visit your Netlify URL
2. Check that the Overview page loads
3. Verify API calls are working (check browser console)
4. Test the Live Map page

## Step 5: Enable Continuous Deployment

Both Render and Netlify automatically deploy on push to the main branch by default.

### Render
- Automatic deploys are enabled by default
- Health checks will restart the service if it fails

### Netlify
- Automatic deploys are enabled by default
- Preview deployments are created for pull requests

## Troubleshooting

### Backend Issues

**Service keeps restarting:**
- Check logs in Render dashboard
- Verify MBTA_API_KEY is set correctly
- Ensure database directory permissions

**Database errors:**
- SQLite databases persist on Render, but may reset on service restart
- For production, consider upgrading to PostgreSQL

**CORS errors:**
- Verify CORS_ORIGINS includes your frontend URL
- Check that the frontend URL matches exactly (no trailing slash)

### Frontend Issues

**API connection errors:**
- Verify VITE_API_URL is set correctly in Netlify environment variables
- Check that backend is accessible and healthy
- Verify CORS is configured correctly

**Build failures:**
- Check build logs in Netlify dashboard
- Ensure all dependencies are in package.json
- Verify Node.js version (should be 18+)

**404 errors on routes:**
- Verify `netlify.toml` has the redirect rule configured
- Check that build output is in the `dist` directory

## Monitoring

### Render
- View logs in the Render dashboard
- Set up alerts for health check failures
- Monitor resource usage

### Netlify
- View build logs and deploy history
- Monitor analytics and performance
- Set up form notifications if needed

## Custom Domain (Optional)

### Render
1. Go to Settings → Custom Domains
2. Add your domain
3. Follow DNS configuration instructions

### Netlify
1. Go to Site settings → Domain management
2. Add custom domain
3. Configure DNS records as instructed

## Cost Considerations

### Free Tier Limits

**Render:**
- Web services may sleep after 15 minutes of inactivity
- Database storage: 1GB
- Bandwidth: 100GB/month

**Netlify:**
- Build minutes: 300/month
- Bandwidth: 100GB/month
- Form submissions: 100/month

For production use, consider upgrading to paid plans for:
- Always-on services (no sleep)
- More build minutes
- Higher bandwidth limits
- Better performance

## Production Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Netlify
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] Health check endpoint working
- [ ] Frontend can communicate with backend
- [ ] Database initialized
- [ ] Telemetry collector running (check logs)
- [ ] Custom domains configured (optional)
- [ ] Monitoring and alerts set up (optional)
