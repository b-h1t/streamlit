# Document Assignment & Labelling - Azure Streamlit App

A Streamlit web application for document classification using Azure AI services. This app classifies legal documents into categories like Summons, Judgments, and other legal document types using Azure Document Intelligence and Language Models.

## Features

- **Document Upload**: Upload PDF and image files for analysis
- **Azure Document Intelligence**: OCR text extraction using Azure's prebuilt-read model
- **AI Classification**: Document classification using Azure Language Models (Phi-4, GPT-4o-mini, Mistral)
- **Azure Blob Storage**: Secure file storage and feedback logging
- **Interactive UI**: User-friendly interface with feedback collection

## Azure Services Used

- **Azure App Service**: Web hosting
- **Azure Blob Storage**: File storage
- **Azure Document Intelligence**: OCR and text extraction
- **Azure AI Studio**: Language models for classification

## Prerequisites

1. **Azure CLI** installed and configured
2. **Azure Subscription** with appropriate permissions
3. **Azure Resources**:
   - Storage Account with Blob Storage
   - Document Intelligence resource
   - AI Studio resource with deployed models

## Quick Deployment to Azure

### 1. Prepare Your Environment

```bash
# Clone or download this repository
cd streamlit

# Install Azure CLI (if not already installed)
# macOS: brew install azure-cli
# Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
# Linux: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux
```

### 2. Create Deployment Package

```bash
# Create the deployment zip file
./create-deployment-package.sh
```

### 3. Deploy to Azure

**🚨 If you get quota errors (Free VMs: 0), try these alternatives:**

**Option A: Container Instances (Recommended - No quota issues)**
```bash
# Deploy using Azure Container Instances
./deploy-container.sh
```

**Option B: Local Development with ngrok (Immediate testing)**
```bash
# Run locally and expose via ngrok
./deploy-local.sh
```

**Option C: Check all available options**
```bash
# See all deployment alternatives
./deploy-workaround.sh
```

**Option D: Free Tier (if you have quota)**
```bash
# Deploy using free F1 tier
./deploy-free.sh
```

**Option E: Basic Tier (if you have quota)**
```bash
# Deploy using B1 tier
./deploy.sh
```

### 4. Configure Secrets

After deployment, configure the following secrets in Azure App Service:

1. Go to **Azure Portal** > **App Services** > **your-app-name** > **Configuration** > **Application settings**
2. Add these secrets:

```
AZURE_CONNECTION_STRING=your_storage_connection_string
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_di_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_di_key
AZURE_LLM_ENDPOINT=your_llm_endpoint
AZURE_LLM_API_KEY=your_llm_api_key
```

3. **Restart** the app after adding secrets

## Manual Deployment Steps

If you prefer manual deployment:

### 1. Create Azure Resources

```bash
# Create resource group
az group create --name streamlit-rg --location "East US"

# Create storage account
az storage account create \
    --name yourstorageaccount \
    --resource-group streamlit-rg \
    --location "East US" \
    --sku Standard_LRS

# Create Document Intelligence resource
az cognitiveservices account create \
    --name your-document-intelligence \
    --resource-group streamlit-rg \
    --location "East US" \
    --kind FormRecognizer \
    --sku S0

# Create App Service plan
az appservice plan create \
    --name streamlit-plan \
    --resource-group streamlit-rg \
    --sku B1 \
    --is-linux

# Create web app
az webapp create \
    --name your-streamlit-app \
    --resource-group streamlit-rg \
    --plan streamlit-plan \
    --runtime "PYTHON|3.11" \
    --startup-file "startup.py"
```

### 2. Deploy Application

```bash
# Create deployment package
./create-deployment-package.sh

# Deploy using Azure CLI
az webapp deployment source config-zip \
    --name your-streamlit-app \
    --resource-group streamlit-rg \
    --src app.zip
```

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Create a `.streamlit/secrets.toml` file:

```toml
AZURE_CONNECTION_STRING = "your_connection_string"
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = "your_di_endpoint"
AZURE_DOCUMENT_INTELLIGENCE_KEY = "your_di_key"
AZURE_LLM_ENDPOINT = "your_llm_endpoint"
AZURE_LLM_API_KEY = "your_llm_api_key"
```

### 3. Run Locally

```bash
streamlit run streamlit.py
```

## Configuration

The application uses several configuration files:

- **`config.py`**: Application constants and configuration
- **`.streamlit/config.toml`**: Streamlit server configuration
- **`requirements.txt`**: Python dependencies
- **`startup.py`**: Azure App Service startup script

## Supported Document Types

- **Summons**: Court-issued documents with claim forms
- **Judgment**: Official court decisions
- **Solicitor_TP_S152**: Section 152 or Road Traffic Act documents
- **Chaser**: Follow-up communications
- **Other**: Documents that don't fit other categories

## Monitoring and Logs

### View Application Logs

```bash
az webapp log tail --name your-app-name --resource-group streamlit-rg
```

### Monitor in Azure Portal

1. Go to **App Service** > **Monitoring** > **Log stream**
2. Check **Application Insights** for detailed analytics

## Troubleshooting

### Common Issues

1. **Quota Limit Exceeded**: 
   - Error: "Current Limit (Free VMs): 0, Amount required: 1"
   - **Immediate Solution**: Use Container Instances: `./deploy-container.sh`
   - **Quick Testing**: Use local + ngrok: `./deploy-local.sh`
   - **Alternative**: Request quota increase: `./request-quota-increase.sh`

2. **App won't start**: Check that all secrets are configured correctly
3. **Import errors**: Ensure all dependencies are in `requirements.txt`
4. **Azure service errors**: Verify resource permissions and endpoints

### Debug Mode

Enable debug logging by setting environment variables:

```bash
az webapp config appsettings set \
    --name your-app-name \
    --resource-group streamlit-rg \
    --settings STREAMLIT_LOGGER_LEVEL=debug
```

## Cost Optimization

- Use **B1** App Service plan for development
- Consider **F1** (free tier) for testing (with limitations)
- Monitor Azure costs in the portal
- Use **Standard** storage for production workloads

## Security Considerations

- Store all secrets in Azure App Service configuration
- Use managed identities where possible
- Enable HTTPS only
- Regular security updates for dependencies

## Support

For issues and questions:
1. Check Azure App Service logs
2. Review Streamlit documentation
3. Check Azure service status
4. Review this README for common solutions
