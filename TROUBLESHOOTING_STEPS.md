# Troubleshooting: Still Seeing Default Page

## Current Issue
You're still seeing the Azure default page instead of your Streamlit application.

## Step-by-Step Debug Process

### Step 1: Test Basic Python Execution

**Current Setup:** Use `test_app.py` to verify Python is working

1. **Deploy** your application
2. **Set Startup Command** to: `python test_app.py`
3. **Visit** your Azure Web App URL
4. **Expected Result:** You should see "✅ Azure Python Test Successful!" page

**If this works:** Python is working, issue is with Streamlit
**If this fails:** Issue is with Python execution or deployment

### Step 2: Test Streamlit Direct Execution

If Step 1 works, try the direct Streamlit approach:

1. **Set Startup Command** to: `python streamlit_direct.py`
2. **Visit** your Azure Web App URL
3. **Expected Result:** You should see your Streamlit application

### Step 3: Test Original run.sh Approach

If Step 2 works, try the original approach:

1. **Set Startup Command** to: `run.sh`
2. **Visit** your Azure Web App URL
3. **Expected Result:** You should see your Streamlit application

### Step 4: Test Direct Command (Microsoft Recommended)

Based on Microsoft documentation comments, try this direct command:

1. **Set Startup Command** to: `python -m streamlit run streamlit.py --server.port 8000 --server.address 0.0.0.0`
2. **Visit** your Azure Web App URL
3. **Expected Result:** You should see your Streamlit application

## Common Issues and Solutions

### Issue: Still seeing default page after all tests
**Possible Causes:**
- Wrong App Service type (Windows instead of Linux)
- Wrong Python runtime version
- Files not deployed correctly
- Startup command not set properly

**Solutions:**
1. **Verify App Service Type:**
   - Go to Azure Portal → Your Web App → Overview
   - Check "Operating System" - should be "Linux"
   - If Windows, create new Linux App Service

2. **Verify Python Runtime:**
   - Go to Azure Portal → Your Web App → Configuration → General settings
   - Check "Stack" - should be "Python"
   - Check "Major version" - should be "3.10" or higher

3. **Verify File Deployment:**
   - Go to Azure Portal → Your Web App → Development Tools → Console
   - Run: `ls -la` to see deployed files
   - Verify `streamlit.py`, `config.py`, `requirements.txt` are present

4. **Verify Startup Command:**
   - Go to Azure Portal → Your Web App → Configuration → General settings
   - Check "Startup Command" is set correctly
   - Try different startup commands from the steps above

### Issue: "No module named streamlit"
**Solution:**
- Check that `requirements.txt` includes `streamlit>=1.28.0`
- Verify deployment completed successfully
- Check deployment logs for pip install errors

### Issue: Application Error
**Solution:**
- Check Azure logs: Monitoring → Log stream
- Look for specific error messages
- Verify all environment variables are set

## Alternative Deployment Methods

### Method 1: VS Code Deployment
1. Install Azure Extension Pack
2. Right-click project folder → "Deploy to Web App..."
3. Select Linux-based App Service
4. Wait for deployment
5. Set startup command in Azure Portal

### Method 2: Azure CLI Deployment
```bash
# Get deployment URL
az webapp deployment source config-local-git --name your-app-name --resource-group your-resource-group

# Deploy
git init
git add .
git commit -m "Initial commit"
git remote add azure <deployment-url>
git push azure main
```

### Method 3: Create New App Service
If current one is Windows-based:
```bash
# Create new Linux App Service
az group create --name your-resource-group --location "East US"
az appservice plan create --name your-plan --resource-group your-resource-group --sku B1 --is-linux
az webapp create --name your-app-name --resource-group your-resource-group --plan your-plan --runtime "python|3.10"
```

## Files to Verify

Ensure these files are in your deployment:
- `streamlit.py` (main application)
- `config.py` (configuration)
- `requirements.txt` (dependencies)
- `test_app.py` (for testing)
- `streamlit_direct.py` (alternative runner)
- `run.sh` (startup script)
- `.streamlit/config.toml` (Streamlit config)

## Next Steps

1. **Try Step 1** (test_app.py) first
2. **If that works**, try Step 2 (streamlit_direct.py)
3. **If that works**, try Step 3 (run.sh)
4. **If that works**, try Step 4 (direct command)
5. **Report results** for each step

## Expected Results

- **Step 1**: Should show test page with Python info
- **Step 2**: Should show Streamlit app
- **Step 3**: Should show Streamlit app
- **Step 4**: Should show Streamlit app

One of these should work!
