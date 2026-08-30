# Deploy to Railway

Railway supports Docker on the free tier, making it perfect for this project with OCR dependencies.

## Prerequisites

- GitHub account with MitraMetrology repo
- Railway account (sign up at https://railway.app - free $5 credit/month)

## Quick Deployment (5 minutes)

### Step 1: Create Railway Project

1. Go to https://railway.app/new
2. Click **Deploy from GitHub repo**
3. Connect your GitHub account if needed
4. Select `namangaur28/MitraMetrology`
5. Railway will detect the Dockerfile automatically

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **+ New**
2. Select **Database** → **Add PostgreSQL**
3. Wait 30 seconds for it to provision
4. Railway automatically creates a `DATABASE_URL` variable

### Step 3: Deploy Backend

1. Click on the **MitraMetrology** service (already created from Step 1)
2. Go to **Variables** tab
3. Add these environment variables:

```
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

Note: `DATABASE_URL` is auto-added when you link the Postgres database

4. Go to **Settings** tab
5. Under **Networking**, click **Generate Domain**
6. Copy the domain (e.g., `mitrametrology-production.up.railway.app`)
7. Under **Deploy**, set:
   - **Dockerfile Path:** `docker/Dockerfile.backend`
   - **Docker Build Context:** `.` (root)
8. Click **Deploy** (top right)

### Step 4: Deploy Frontend

1. Click **+ New** in your project
2. Select **GitHub Repo** → `namangaur28/MitraMetrology`
3. Railway creates a new service
4. Go to **Settings** → Rename to `frontend`
5. Under **Build**, set:
   - **Build Command:** `cd frontend && npm ci && npm run build`
   - **Start Command:** `cd frontend && npx serve -s dist -l $PORT`
6. Go to **Variables** tab, add:
   ```
   VITE_API_URL=https://<your-backend-domain>.railway.app/api
   ```
   (Replace with domain from Step 3)
7. Under **Networking**, click **Generate Domain**
8. Click **Deploy**

### Step 5: Access Your App

After 5-10 minutes:
- **Frontend:** `https://<frontend-domain>.railway.app`
- **Backend API:** `https://<backend-domain>.railway.app/api`
- **API Docs:** `https://<backend-domain>.railway.app/docs`

---

## Alternative: Railway CLI (Advanced)

If you prefer command line:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to PostgreSQL
railway add --database postgres

# Deploy backend
railway up --service backend

# Deploy frontend
railway up --service frontend
```

---

## Configuration Details

### Backend Service

**Dockerfile:** `docker/Dockerfile.backend`
- Base: Python 3.11-slim
- Includes: Tesseract OCR, OpenCV, all Python dependencies
- Exposes: Port 8000
- Auto-detected by Railway

**Environment Variables:**
- `DATABASE_URL` - Auto-set by Railway Postgres
- `PORT` - Auto-set by Railway (use in start command)
- All other vars from `.env.example`

**Resources (Free Tier):**
- 512MB RAM
- 1GB disk
- $5 credit/month (~500 hours)

### Frontend Service

**Build:** Vite production build
**Serve:** Using `serve` package
**Static files:** `frontend/dist`

**Environment Variables:**
- `VITE_API_URL` - Backend API URL
- `PORT` - Auto-set by Railway

### Database

**PostgreSQL 15**
- 1GB storage (free tier)
- Automatic backups
- Connection pooling
- `DATABASE_URL` auto-injected into backend

---

## Cost Breakdown

**Free Tier ($5/month credit):**
- PostgreSQL: ~$1/month
- Backend: ~$3/month (always on)
- Frontend: ~$1/month

**Total: ~$5/month = FREE with monthly credit**

**Usage tips to stay free:**
- Backend sleep after 1 hour idle (enable in settings)
- Remove unused deployments
- Monitor usage in dashboard

**If you exceed free tier:**
- First bill: ~$5-10/month
- Hobby plan: $5/month flat + usage

---

## Troubleshooting

### Backend won't start

**Check logs:**
```bash
railway logs --service backend
```

**Common issues:**
- Database not linked: Go to Variables, ensure `DATABASE_URL` exists
- Port mismatch: Start command must use `$PORT`, not hardcoded 8000
- Missing dependencies: Check Dockerfile builds successfully

### Frontend can't reach backend

**CORS Error:**
- Check `VITE_API_URL` matches backend domain
- Verify backend is running (check health endpoint)
- Check backend CORS settings in `app/main.py`

**Build Failed:**
- Check `package.json` in frontend folder
- Ensure `npm run build` works locally
- Check build logs in Railway dashboard

### Database connection failed

**Error: "could not connect to server"**
- Wait 2 minutes after creating database (provisioning time)
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Verify database service is running (green dot in dashboard)

### OCR not working

Railway supports Docker fully, so Tesseract should work. If not:
- Check backend logs for OCR errors
- Verify Dockerfile includes `tesseract-ocr` installation
- Test with simple image first

---

## Monitoring & Logs

### View Logs
- Dashboard → Select Service → **Deployments** → Click latest
- Or use CLI: `railway logs --service <name>`

### Health Checks
Backend auto-checks `/api/health` every 30 seconds

### Metrics
- CPU, Memory, Network usage in **Metrics** tab
- Deployment history in **Deployments** tab

---

## Production Checklist

Before sharing your deployed app:

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads without errors
- [ ] Can upload images and get compliance results
- [ ] Database persists data between requests
- [ ] API docs accessible at `/docs`
- [ ] CORS allows frontend domain
- [ ] Environment variables set correctly
- [ ] Custom domain configured (optional)

---

## Updating Your Deployment

Railway auto-deploys on every push to `main`:

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

Railway detects the push and rebuilds automatically.

**Disable auto-deploy:**
Settings → **Deploy** → Toggle off "Auto Deploy"

---

## Custom Domain (Optional)

1. Go to service **Settings** → **Networking**
2. Click **Custom Domain**
3. Add your domain (e.g., `mitrametrology.yourdomain.com`)
4. Update DNS:
   - Type: CNAME
   - Name: mitrametrology
   - Value: `<railway-subdomain>.railway.app`
5. Wait for DNS propagation (5-60 minutes)

---

## Scaling Beyond Free Tier

**If you outgrow free tier:**

1. **Hobby Plan** ($5/month):
   - More resources
   - Custom domains
   - Priority support

2. **Pro Plan** ($20/month):
   - Team collaboration
   - More compute
   - Advanced metrics

3. **Optimize usage:**
   - Enable sleep mode for backend
   - Use CDN for frontend (Cloudflare)
   - Optimize images before upload

---

## Migrating from Railway

If you need to move later:

**Backup database:**
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

**Export environment variables:**
Railway Dashboard → Variables → Copy all

**Deploy elsewhere:**
Use the same Dockerfiles and env vars

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/namangaur28/MitraMetrology/issues

---

## Comparison: Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Docker Support (Free) | ✅ Yes | ❌ No |
| PostgreSQL (Free) | ✅ 1GB | ✅ 1GB |
| Always On | ✅ Yes | ❌ Spins down |
| Build Time | ~5 min | ~7 min |
| Auto-deploy | ✅ Yes | ✅ Yes |
| Custom Domains | ✅ Yes | ✅ Yes |
| Free Tier | $5 credit/mo | 750 hrs/mo |

**For this project:** Railway is better because Docker support is required for Tesseract OCR.
