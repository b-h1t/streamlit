# Azure App Service Deployment Guide

This guide follows the exact [Microsoft documentation](https://learn.microsoft.com/en-us/answers/questions/1470782/how-to-deploy-a-streamlit-application-on-azure-app) for deploying Streamlit on Azure App Service.

## Prerequisites

- Azure subscription
- Azure CLI installed
- VS Code with Azure Extension Pack

## Step 1: Create Azure Resources

### 1.1 Login to Azure
```bash
az login
```

### 1.2 Create Resource Group
```bash
az group create --name your-resource-group --location "East US"
```

### 1.3 Create App Service Plan (B1 or higher)
```bash
az appservice plan create --name your-plan-name --resource-group your-resource-group --sku B1 --is-linux
```

### 1.4 Create Web App (Python 3.10+)
```bash
az webapp create --name your-app-name --resource-group your-resource-group --plan your-plan-name --runtime "python|3.10"
```

## Step 2: Deploy Application

### 2.1 Using VS Code (Recommended)
1. Install Azure Extension Pack in VS Code
2. Login to Azure in VS Code
3. Right-click project folder → "Deploy to Web App..."
4. Select your Azure subscription and Web App
5. Wait for deployment to complete

### 2.2 Using Azure CLI
```bash
# Get deployment URL
az webapp deployment source config-local-git --name your-app-name --resource-group your-resource-group

# Initialize Git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Add Azure remote
git remote add azure <deployment-url-from-above>

# Deploy
git push azure main
```

## Step 3: Configure Startup Command

### Option 1: Direct command (Recommended - Use This First!)
1. Go to Azure Portal → Your Web App → Settings → Configuration → General settings
2. Set **Startup Command** to: `python3 -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`
3. Click **Save**

**This is the most reliable method and bypasses all script path issues.**

### Option 2: Using startup.py
1. Go to Azure Portal → Your Web App → Settings → Configuration → General settings
2. Set **Startup Command** to: `python3 startup.py`
3. Click **Save**

### Option 3: Using startup.sh
1. Go to Azure Portal → Your Web App → Settings → Configuration → General settings
2. Set **Startup Command** to: `startup.sh`
3. Click **Save**

### Important Notes:
- **Use Option 1 (Direct command) first** - it's the most reliable
- Make sure you're using **Linux App Service** (not Windows)
- The startup command should be set in **General settings**, not **Application settings**

## Step 4: Set Environment Variables

In Azure Portal → Your Web App → Settings → Configuration → Application settings, add:

- `AZURE_CONNECTION_STRING` = your_azure_storage_connection_string
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` = your_document_intelligence_endpoint
- `AZURE_DOCUMENT_INTELLIGENCE_KEY` = your_document_intelligence_key
- `AZURE_LLM_ENDPOINT` = your_llm_endpoint
- `AZURE_LLM_API_KEY` = your_llm_api_key

## Step 5: Verify Deployment

1. Visit your Azure Web App URL
2. You should see the Streamlit Document Assignment & Labelling interface
3. Test file upload and classification functionality

## File Structure

```
/
├── app.py                    # Main Streamlit application
├── startup.py                # Azure startup script (Python)
├── startup.sh                # Azure startup script (Bash)
├── config.py                 # Configuration constants
├── run.sh                    # Linux startup script
├── requirements.txt          # Python dependencies
├── web.config               # Windows App Service config
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## Key Configuration

### run.sh
```bash
#!/bin/bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

### startup.py
```python
#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    os.environ['STREAMLIT_SERVER_PORT'] = '8000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    cmd = [sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8000', '--server.address', '0.0.0.0']
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    main()
```

### .streamlit/config.toml
- Port 8000 (Azure Linux App Service standard)
- CORS enabled
- Address 0.0.0.0 (bind to all interfaces)

### app.py
- Added `st.set_option('server.enableCORS', True)` as per Microsoft docs
- Environment variable fallback for Azure deployment

## Troubleshooting

### Common Issues

1. **"startup.sh: not found" or "run.sh: not found"**: 
   - **IMMEDIATE FIX**: Use the **Direct command** option: `python3 -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`
   - This bypasses all script path issues completely
   - Azure Oryx is looking for scripts in `/opt/startup/` but your files are in `/home/site/wwwroot`

2. **Still seeing default page**: 
   - Ensure you're using Linux App Service, not Windows
   - Check that the startup command is set correctly

3. **"No module named streamlit"**: 
   - Check requirements.txt and deployment logs
   - Ensure all dependencies are installed

4. **Application Error**: 
   - Verify startup command is set correctly
   - Check Azure logs for specific error messages

5. **CORS errors**: 
   - CORS is enabled in both config.toml and app.py

### Alternative Startup Command

If `run.sh` doesn't work, try this directly in the startup command field:
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

### Check Logs

- Azure Portal → Your Web App → Monitoring → Log stream
- Look for startup messages and error details

## Important Notes

- **Must use Linux App Service** (not Windows)
- **B1 SKU minimum** (free tier doesn't support Streamlit)
- **Python 3.10+** runtime
- **Port 8000** (Azure Linux standard)
- **CORS enabled** for Azure deployment
