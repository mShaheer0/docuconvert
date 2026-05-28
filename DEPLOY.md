# Digital Ocean Deployment Guide

## Prerequisites
- Digital Ocean account with $200 credits
- GitHub repo with this code
- SSH access to terminal

---

## Step 1: Create Digital Ocean Droplet

1. **Log in** to Digital Ocean
2. **Create Droplet**:
   - **Image**: Ubuntu 22.04 x64
   - **Size**: Basic - $12/month (2GB RAM, 2vCPU, 50GB SSD)
   - **Region**: Choose closest to users (e.g., New York, San Francisco)
   - **VPC Network**: Default
   - **Authentication**: Add SSH key (or password)
   - **Hostname**: `docuconvert`
   - **Enable backups**: YES ($2.40/month for safety)

3. **Note the IP address** (you'll need it)

---

## Step 2: Set Up Droplet (SSH into it)

```bash
ssh root@YOUR_DROPLET_IP
```

### Install Docker and Docker Compose

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
apt install -y docker.io docker-compose

# Start Docker
systemctl start docker
systemctl enable docker

# Add your user to docker group (optional)
usermod -aG docker root
```

### Clone Repository

```bash
cd /
git clone https://github.com/mShaheer0/docuconvert.git app
cd /app
```

### Build and Run

```bash
# Test locally first
docker-compose up -d

# Check if it's running
docker-compose ps

# Check logs
docker-compose logs -f
```

Visit: `http://YOUR_DROPLET_IP`

---

## Step 3: Set Up GitHub Actions for Auto-Deploy

### Generate SSH Key on Droplet

```bash
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N ""
cat ~/.ssh/github_deploy
```

Copy the **private key** output.

### Add Secrets to GitHub

1. Go to **Settings → Secrets and variables → Actions**
2. Add 3 new **Repository Secrets**:

| Name | Value |
|------|-------|
| `DO_SSH_KEY` | Paste the private key from above |
| `DO_DROPLET_IP` | Your Droplet's IP (e.g., `192.168.1.1`) |
| `DO_SSH_USER` | `root` |

### Test the Workflow

```bash
# On your local machine, make a small change and push
git add .
git commit -m "Test deployment"
git push origin main
```

Check **Actions tab** in GitHub → watch deployment happen automatically! 🚀

---

## Step 4: Monitor & Maintain

### Check App Status
```bash
ssh root@YOUR_DROPLET_IP
cd /app
docker-compose ps
docker-compose logs -f app  # View live logs
```

### View Nginx Logs
```bash
docker-compose exec app cat /var/log/nginx/access.log
```

### Restart App
```bash
cd /app
docker-compose restart
```

### Update Code Manually (optional)
```bash
cd /app
git pull origin main
docker-compose down
docker-compose up -d
```

---

## Step 5: Configure Domain (Optional)

1. **Buy domain** (Namecheap, GoDaddy, etc.)
2. **Point to Droplet IP** via A record:
   ```
   @ (root)  →  YOUR_DROPLET_IP
   www       →  YOUR_DROPLET_IP
   ```
3. **Update nginx.conf** server_name:
   ```nginx
   server_name yourdomain.com www.yourdomain.com;
   ```
4. **Restart app**:
   ```bash
   docker-compose restart
   ```

---

## Step 6: Enable HTTPS (Optional but Recommended)

### Install Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

### Get Certificate

```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

### Update nginx.conf

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Restart
```bash
docker-compose restart
```

---

## Troubleshooting

### App won't start?
```bash
docker-compose logs app
# Check for Python errors in logs
```

### Port 80 already in use?
```bash
lsof -i :80
kill -9 PID
```

### Out of disk space?
```bash
df -h
docker system prune -a  # Clean up old images
```

### Need to rebuild?
```bash
docker-compose down
docker system prune -a
docker-compose up --build -d
```

---

## Cost Check

- **Droplet**: $12/month
- **Backups**: $2.40/month
- **Data transfer**: ~$1-2/month (first 1TB free)
- **Total**: ~$15/month = **13+ months of credits** ✅

---

## Deployment Checklist

- [ ] Droplet created and running
- [ ] Docker installed on Droplet
- [ ] Repository cloned
- [ ] docker-compose up works locally
- [ ] GitHub Secrets configured (DO_SSH_KEY, DO_DROPLET_IP, DO_SSH_USER)
- [ ] GitHub Actions workflow tested
- [ ] Push to main triggers auto-deployment
- [ ] Backups enabled
- [ ] Domain configured (optional)
- [ ] HTTPS enabled (optional)

---

## Next Steps

1. **Monitor performance**: Check Droplet stats in DO dashboard
2. **Make changes**: Push code → GitHub Actions handles deployment
3. **Plan for growth**: If traffic increases, upgrade Droplet or add load balancer

---

**Questions?** Check Docker logs or GitHub Actions logs for errors!
