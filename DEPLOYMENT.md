# Deployment Guide - Render.com

## 🚀 Deploy to Render.com (Free)

### Prerequisites
- GitHub account
- Render.com account (free)

### Step-by-Step Instructions

#### 1. Push to GitHub

If you haven't already, push this project to GitHub:

```bash
cd /Users/charly.leporc/Documents/LT-evaluation
git init
git add .
git commit -m "Initial commit - Lactate Threshold Calculator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/LT-evaluation.git
git push -u origin main
```

#### 2. Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**
   - Click "Connect account" if first time
   - Find and select your `LT-evaluation` repository

4. **Configure the service:**
   - **Name:** `lactate-threshold-calculator` (or your choice)
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn flask_app:app`
   - **Plan:** Free

5. **Click "Create Web Service"**

6. **Wait for deployment** (2-5 minutes)
   - You'll see build logs
   - When complete, you'll get a URL like: `https://lactate-threshold-calculator.onrender.com`

#### 3. Test Your Deployment

Visit your Render URL and test uploading a CSV file!

---

## 📝 Embed in Squarespace

Once deployed, add this to your Squarespace page:

### Option A: Full Embed (Recommended)

1. **Edit your Squarespace page**
2. **Add a Code Block** (in the editor, click "+" → "Code")
3. **Paste this HTML:**

```html
<div style="width: 100%; height: 900px; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <iframe 
        src="https://YOUR-APP-NAME.onrender.com" 
        width="100%" 
        height="100%" 
        frameborder="0"
        style="border: none;">
    </iframe>
</div>
```

Replace `YOUR-APP-NAME` with your actual Render app name!

### Option B: Button Link

Add a button that links to: `https://YOUR-APP-NAME.onrender.com`

---

## ⚙️ Important Notes

### Cold Starts (Free Tier)
Render's free tier "spins down" after 15 minutes of inactivity. First visit after idle may take 30-60 seconds to load. This is normal!

To keep it "warm":
- Use a service like [cron-job.org](https://cron-job.org) to ping it every 10 minutes
- Upgrade to paid tier ($7/month) for always-on service

### Custom Domain (Optional)
On Render's paid plan, you can use your own domain like `calculator.yourdomain.com`

---

## 🐛 Troubleshooting

### Build Failed?
Check the build logs on Render. Common issues:
- Missing dependencies → Already fixed in `requirements.txt`
- Wrong Python version → Specified in `runtime.txt`

### App doesn't load?
- Check Render logs (click "Logs" tab)
- Verify the URL is correct
- Wait 60 seconds if it's been idle (cold start)

### CORS errors in embed?
Add this to `flask_app.py` if needed:
```python
from flask_cors import CORS
CORS(app)
```
And add `flask-cors` to `requirements.txt`

---

## 🔄 Update Your App

After making changes:

```bash
git add .
git commit -m "Update description"
git push
```

Render auto-deploys! Watch the logs to see it update.

---

## 💡 Tips

1. **Monitor usage** - Render free tier has 750 hours/month (enough for 24/7)
2. **Check logs** - Render dashboard → Your service → Logs tab
3. **Environment variables** - Can add in Render dashboard if needed

---

Need help? Check [Render's docs](https://render.com/docs) or let me know!
