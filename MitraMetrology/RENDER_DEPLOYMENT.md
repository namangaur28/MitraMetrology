# Deploy to Render

This guide walks you through deploying MitraMetrology to Render using their Blueprint (Infrastructure as Code).

## Prerequisites

- GitHub account with the MitraMetrology repo
- Render account (sign up at https://render.com - free)

## Deployment Steps

### Option 1: Automated Blueprint Deployment (Recommended)

1. **Connect GitHub to Render**
   - Go to https://dashboard.render.com
   - Click **New +** → **Blueprint**
   - Connect your GitHub account if not already connected
   - Select repository: `namangaur28/MitraMetrology`
   - Render will detect `render.yaml` automatically

2. **Review Services**
   Render will create 3 services:
   - **PostgreSQL Database** (mitrametrology-db)
   - **Backend API** (mitrametrology-backend)
   - **Frontend Static Site** (mitrametrology-frontend)

3. **Deploy**
   - Click **Apply**
   - Wait 5-10 minutes for all services to build and deploy
   - Database creates first, then backend, then frontend

4. **Get Your URLs**
   - Frontend: `https://mitrametrology-frontend.onrender.com`
   - Backend API: `https://mitrametrology-backend.onrender.com`
   - API Docs: `https://mitrametrology-backend.onrender.com/docs`

### Option 2: Manual Deployment

If Blueprint doesn't work, deploy services individually:

#### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **New +** → **PostgreSQL**
3. Name: `mitrametrology-db`
4. Database: `mitrametrology_db`
5. User: `mitrauser`
6. Region: Singapore (or nearest)
7. Plan: **Free**
8. Click **Create Database**
9. **Copy the Internal Database URL** (starts with `postgresql://`)

#### Step 2: Deploy Backend API

1. Click **New +** → **Web Service**
2. Connect repository: `namangaur28/MitraMetrology`
3. Name: `mitrametrology-backend`
4. Region: Singapore
5. Branch: `main`
6. Root Directory: leave blank
7. Environment: **Docker**
8. Dockerfile Path: `./docker/Dockerfile.backend`
9. Docker Context: `.`
10. Plan: **Free**

**Environment Variables:**
Add these in the Environment section:

```
DATABASE_URL=<paste Internal Database URL from Step 1>
ENVIRONMENT=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png
IMG_MAX_WIDTH=1920
IMG_MAX_HEIGHT=1080
IMG_QUALITY=85
OCR_LANGUAGE=en
```

11. Health Check Path: `/api/health`
12. Click **Create Web Service**
13. Wait 5-7 minutes for build to complete
14. **Copy the backend URL** (e.g., `https://mitrametrology-backend.onrender.com`)

#### Step 3: Deploy Frontend

1. Click **New +** → **Static Site**
2. Connect repository: `namangaur28/MitraMetrology`
3. Name: `mitrametrology-frontend`
4. Branch: `main`
5. Root Directory: `frontend`
6. Build Command: `npm ci && npm run build`
7. Publish Directory: `dist`

**Environment Variables:**
```
VITE_API_URL=<paste backend URL from Step 2>/api
```

Example: `VITE_API_URL=https://mitrametrology-backend.onrender.com/api`

8. Click **Create Static Site**
9. Wait 3-5 minutes for build

#### Step 4: Update Backend CORS (if needed)

If you get CORS errors, add your frontend URL to backend's allowed origins:

1. Go to backend service settings
2. Add environment variable:
   ```
   CORS_ORIGINS=https://mitrametrology-frontend.onrender.com
   ```
3. The backend `main.py` already has CORS configured for all origins in production

---

## Important Notes

### Free Tier Limitations

- **Backend spins down after 15 minutes of inactivity**
  - First request after idle will take 30-60 seconds to wake up
  - Subsequent requests are fast
  
- **Database**
  - 1GB storage limit
  - Expires after 90 days (but you can create a new one)

- **Monthly Limits**
  - 750 hours per month for web services
  - 100GB bandwidth

### Storage Considerations

The current setup stores uploaded images in-memory/ephemeral storage on Render's free tier. For production, consider:

1. **Option A: External Storage (Recommended)**
   - Use Cloudinary, AWS S3, or Google Cloud Storage
   - Update `image_processor.py` to upload to cloud storage
   - Store only URLs in database

2. **Option B: Database Storage**
   - Store base64-encoded images in PostgreSQL (not ideal for large files)

### Environment Variables

Backend environment variables are set in `render.yaml`:
- `DATABASE_URL` - automatically set by Render from the database
- `ENVIRONMENT=production` - disables debug mode
- `DEBUG=False` - no debug traces in responses
- Other settings match `.env.example`

Frontend only needs:
- `VITE_API_URL` - points to backend API endpoint

### Monitoring

- Check service logs: Dashboard → Select Service → Logs
- Health check: `https://your-backend.onrender.com/api/health`
- API docs: `https://your-backend.onrender.com/docs`

### Troubleshooting

**Backend won't start:**
- Check logs for database connection errors
- Verify `DATABASE_URL` is set correctly
- Ensure Tesseract dependencies installed (they are in Dockerfile)

**Frontend can't connect to backend:**
- Verify `VITE_API_URL` matches backend URL + `/api`
- Check CORS settings in backend
- Try accessing backend directly: `https://backend-url.onrender.com/api/health`

**Slow first load:**
- Normal on free tier - service is waking up
- Subsequent requests will be fast

**Build fails:**
- Check build logs
- Ensure all dependencies in `requirements.txt` and `package.json`
- Docker builds can take 5-10 minutes on free tier

---

## Post-Deployment

### Update GitHub Repository

After confirming deployment works:

```bash
git add render.yaml RENDER_DEPLOYMENT.md
git commit -m "Add Render deployment configuration"
git push origin main
```

Render will auto-redeploy on every push to `main` branch.

### Set Up Monitoring (Optional)

Enable Render's:
- Email notifications for deploy failures
- Slack integration for build status
- Custom health check alerts

Go to: Dashboard → Service → Settings → Notifications

---

## Cost Estimate

**Current Setup (Free Tier):**
- PostgreSQL: Free (1GB, 90 days)
- Backend: Free (750 hours/month)
- Frontend: Free (100GB bandwidth)

**Total: $0/month**

**If You Outgrow Free Tier:**
- PostgreSQL: $7/month (10GB, persistent)
- Backend: $7/month (always on, no spin-down)
- Frontend: Still free

**Estimated: $14/month for production-ready hosting**

---

## Alternative Platforms

If Render doesn't work well:

1. **Railway** - Similar to Render, generous free tier
2. **Fly.io** - Docker-first, good for FastAPI
3. **Vercel (Frontend) + Railway (Backend)** - Split deployment
4. **Heroku** - No free tier anymore, starts at $5/month per service

---

## Support

For issues:
1. Check Render's status: https://status.render.com
2. Render community: https://community.render.com
3. GitHub Issues: https://github.com/namangaur28/MitraMetrology/issues
