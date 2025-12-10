# Render Deployment Troubleshooting

If you're getting the error: `ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

## Fix in Render Dashboard

The `render.yaml` file should handle this automatically, but if it's not working, manually configure in the Render dashboard:

### Step 1: Go to Your Service Settings

1. Open your Render service dashboard
2. Click **"Settings"** tab
3. Scroll to **"Build & Deploy"** section

### Step 2: Verify These Settings

Make sure these are set **exactly** as shown:

| Setting | Value |
|---------|-------|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Environment** | `Python 3` |

### Important Notes:

- **Root Directory must be `backend`** (not `/backend` or `./backend`)
- Build command runs **inside** the root directory, so it should be `pip install -r requirements.txt` (not `cd backend && ...`)
- Start command also runs inside root directory

### Step 3: Save and Redeploy

1. Click **"Save Changes"**
2. Go to **"Manual Deploy"** → **"Deploy latest commit"**

---

## Alternative: Create Service from render.yaml

If the dashboard settings aren't working:

1. **Delete** your current service in Render
2. **Create new service** → **"New" → "Blueprint"**
3. Render will auto-detect `render.yaml` and configure everything automatically

---

## Verify File Structure

Make sure your repository structure is:

```
Transit-Data-Integration-Platform/
├── backend/
│   ├── requirements.txt  ← This file must exist
│   ├── main.py
│   ├── database.py
│   └── ...
├── frontend/
└── render.yaml  ← This file should be in root
```

---

## Still Having Issues?

Check the build logs in Render to see exactly what directory it's running commands from.

