# Quick Start Guide

## 🎯 Get Started in 3 Steps

### Step 1: Set Up Google Drive Service Account (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Drive API**
4. Create a **Service Account** and download the JSON key file
5. Share your Google Drive folder with the service account email (found in the JSON file)

### Step 2: Run the Application

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
\`\`\`

The application will open in your browser at `http://localhost:8501`

### Step 3: Configure in the Sidebar

1. Upload your service account JSON file in the sidebar
2. (Optional) Enter your API key from [kie.ai](https://kie.ai/api-key) for image editing features
3. Start uploading and managing your media files!

## 📱 Application Features

The application includes **7 pages** with comprehensive functionality:

**Home** - Dashboard with overview and quick start guide

**Upload Media** - Upload images and videos to Google Drive with auto-save functionality

**View Gallery** - Browse and view all media files with filtering options

**API Testing** - Test image editing API with various parameters and auto-save results

**Settings** - Configure application settings and manage folders

**Batch Operations** - Perform batch upload, download, delete, move, copy, and rename operations

**File Manager** - Advanced file management interface with navigation and file viewer

## 🔑 Key Features

- **Google Drive Integration** with service account authentication
- **Multi-page Streamlit application** with intuitive navigation
- **Auto-save functionality** for uploaded media and API results
- **Media viewer** for images and videos directly in Streamlit
- **Batch operations** for efficient file management
- **API integration** for image editing with customizable parameters
- **Folder management** with custom folder support
- **File manager** with advanced features like preview and batch selection

## 📂 Default Folder

By default, the application creates a folder named **"StreamlitMedia"** in your Google Drive. You can change this in the sidebar or Settings page.

## 🆘 Need Help?

Check the **USAGE_GUIDE.md** for detailed instructions and troubleshooting tips.

## 🌐 Live Demo

If the application is already running, access it at:
**https://8501-iqd1dy2j14z53e5qre1r2-8d9cb64f.manusvm.computer**

---

**Enjoy managing your media with Google Drive! 🚀**
