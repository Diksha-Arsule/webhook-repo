# GitHub Webhook Receiver

A Flask application that receives GitHub webhook events (push, pull request, merge) and stores them in MongoDB.

## Features

✅ Receives and processes GitHub webhooks (PUSH, PULL REQUEST, MERGE events)
✅ Stores events in MongoDB Atlas
✅ Real-time event dashboard with auto-refresh
✅ Health check endpoint for monitoring
✅ Comprehensive error handling and logging
✅ Production-ready with proper security practices

## Prerequisites

- Python 3.8+
- MongoDB Atlas account (or local MongoDB)
- GitHub repository with admin access

## Local Setup

### 1. Clone and Setup Environment

```bash
git clone <your-repo>
cd webhook-repo
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your MongoDB URI:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp
PORT=5000
```

### 4. Run Locally

```bash
python app.py
```

Visit `http://localhost:5000` to see the dashboard.

Test the webhook endpoint:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"pusher":{"name":"testuser"},"ref":"refs/heads/main","after":"abc123"}'
```

## Deployment

### Heroku Deployment

1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Set Environment Variables:**
```bash
heroku config:set MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp"
```

3. **Deploy:**
```bash
git push heroku main
```

### Azure App Service Deployment

1. **Create App Service:**
```bash
az webapp create --resource-group <group> --plan <plan> --name <app-name> --runtime PYTHON|3.9
```

2. **Set Environment Variables:**
```bash
az webapp config appsettings set --resource-group <group> --name <app-name> --settings MONGODB_URI="your-uri"
```

3. **Deploy:**
```bash
az webapp deployment source config-zip --resource-group <group> --name <app-name> --src package.zip
```

### AWS Elastic Beanstalk Deployment

1. **Initialize EB:**
```bash
eb init -p python-3.9 webhook-app
```

2. **Create environment:**
```bash
eb create webhook-env
```

3. **Set environment variables:**
```bash
eb setenv MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/?appName=YourApp"
```

4. **Deploy:**
```bash
eb deploy
```

## GitHub Webhook Setup

1. Go to your GitHub repository → Settings → Webhooks
2. Click "Add webhook"
3. Set **Payload URL** to: `https://your-deployed-app.com/webhook`
4. Select event types:
   - [x] Push events
   - [x] Pull requests
5. Click "Add webhook"

## API Endpoints

### GET `/`
Returns the dashboard HTML page.

### GET `/events`
Returns the latest events (JSON array).
```bash
curl http://localhost:5000/events
```

### GET `/health`
Health check endpoint.
```bash
curl http://localhost:5000/health
```

### POST `/webhook`
Receives GitHub webhook events (called by GitHub).

## MongoDB Setup (MongoDB Atlas)

1. Create free cluster at https://www.mongodb.com/cloud/atlas
2. Create database user with username and password
3. Get connection string (URI)
4. Add `.mongodb.net` to IP whitelist if needed
5. Use the URI as `MONGODB_URI` environment variable

Connection string format:
```
mongodb+srv://username:password@cluster.mongodb.net/database?appName=YourApp
```

## Troubleshooting

### "MONGODB_URI environment variable not set"
**Solution:** Set the `MONGODB_URI` environment variable in your deployment platform.

### "Connection refused" on MongoDB
**Solution:** 
- Check if MongoDB is running (local)
- Verify IP whitelist in MongoDB Atlas (deployed)
- Ensure connection string is correct

### Webhook not receiving events
**Solution:**
- Verify webhook URL is correct in GitHub Settings
- Check health endpoint: `/health`
- View logs on your deployment platform
- Ensure GitHub has permission to send requests

### Events not appearing in dashboard
**Solution:**
- Check `/health` endpoint for database connection
- Verify webhook events in GitHub repository settings
- Check browser console for JavaScript errors

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit `.env` file** - Use `.gitignore`
2. **Keep MongoDB credentials safe** - Use environment variables
3. **Enable HTTPS** on webhook URL in production
4. **Whitelist GitHub IP addresses** in firewall if needed
5. **Use strong MongoDB Atlas passwords**
6. **Rotate credentials regularly**

## Performance Optimization

- Events are limited to 100 max per request
- Automatic pagination with 20 events by default
- Indexes recommended on `{author}` and `{timestamp}` for large datasets

## License

MIT License - Feel free to use and modify.
