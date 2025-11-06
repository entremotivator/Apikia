# Streamlit Google Drive Media Manager - Usage Guide

## 🌐 Application URL

Your application is now running and accessible at:
**https://8501-iqd1dy2j14z53e5qre1r2-8d9cb64f.manusvm.computer**

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Page Overview](#page-overview)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### Step 1: Set Up Google Drive Service Account

1. **Create a Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Drive API**
   - In the Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

3. **Create Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Enter a name and description
   - Click "Create and Continue"
   - Skip the optional steps and click "Done"

4. **Generate JSON Key**
   - Click on the created service account
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Click "Create"
   - The JSON file will be downloaded automatically

5. **Share Google Drive Folder**
   - Create a folder in your Google Drive (or use an existing one)
   - Right-click the folder and select "Share"
   - Add the service account email (found in the JSON file, looks like: `your-service@project-id.iam.gserviceaccount.com`)
   - Give it "Editor" permissions
   - Click "Share"

### Step 2: Configure the Application

1. **Upload Service Account JSON**
   - Open the application
   - In the sidebar, find "Google Drive Authentication"
   - Click "Browse files" under "Upload Service Account JSON"
   - Select your downloaded JSON file
   - Wait for the success message

2. **Configure API Key (Optional)**
   - In the sidebar, find "API Configuration"
   - Enter your API key from [kie.ai](https://kie.ai/api-key)
   - The API key is used for image editing features

## ⚙️ Configuration

### Sidebar Configuration

The sidebar contains all the essential configuration options:

- **Google Drive Authentication**: Upload your service account JSON file
- **API Configuration**: Enter your API key for image editing
- **Google Drive Settings**: Configure the default folder name
- **Status Indicators**: Check if Drive and API are properly configured

### Default Folder

The application uses a default folder named "StreamlitMedia" in your Google Drive. You can change this in the sidebar or in the Settings page.

## 📄 Page Overview

### 1. Home (Main Page)

The home page provides:
- Welcome message and feature overview
- Quick start guide
- System information
- Status indicators

### 2. 📤 Upload Media

Upload images and videos to Google Drive:
- **Supported Image Formats**: JPG, JPEG, PNG, WEBP, GIF, BMP
- **Supported Video Formats**: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
- **Features**:
  - Multiple file upload
  - Custom folder selection
  - Add timestamp to filenames
  - Progress tracking
  - Auto-save to Google Drive

### 3. 🖼️ View Gallery

Browse and view your media files:
- **Filter Options**:
  - Filter by media type (All, Images, Videos)
  - Select folder (Default or Custom)
- **Features**:
  - Grid layout for images
  - Video player for videos
  - File details (size, type, creation date)
  - Delete files
  - Open in Google Drive
  - Statistics display

### 4. 🎨 API Testing

Test the image editing API:
- **Image Sources**:
  - URL
  - Upload from computer
  - From Google Drive
- **Edit Parameters**:
  - Prompt and negative prompt
  - Image size selection
  - Acceleration options
  - Inference steps
  - Guidance scale
  - Output format
  - Safety checker
  - Custom seed
- **Features**:
  - Real-time task status
  - Result preview
  - Download results
  - Auto-save to Google Drive

### 5. ⚙️ Settings

Configure application settings:
- **Google Drive Settings**:
  - View current configuration
  - Update default folder name
  - Create new folders
  - List all folders
  - Storage statistics
- **API Settings**:
  - View API information
  - Test API connection
- **Application Information**:
  - Version and features
  - Debug information
- **Reset Options**:
  - Clear credentials
  - Clear API key

### 6. 📦 Batch Operations

Perform batch operations on files:
- **Batch Upload**: Upload multiple files at once
- **Batch Download**: Download multiple files
- **Batch Delete**: Delete multiple files
- **Move Files**: Move files between folders
- **Copy Files**: Copy files between folders
- **Rename Files**: Batch rename with prefix/suffix

### 7. 📂 File Manager

Advanced file management interface:
- **Navigation**: Browse folders and files
- **Actions**:
  - Create new folders
  - Upload files
  - Delete selected files
  - Download selected files
- **File List**:
  - Checkbox selection
  - File details (name, type, size, created date)
  - Quick actions (view, delete)
- **File Viewer**:
  - Preview images
  - Play videos
  - View text files
  - Download files

## 🔧 Common Tasks

### Upload Images and Videos

1. Navigate to "Upload Media" page
2. Click "Choose image files" or "Choose video files"
3. Select one or more files
4. (Optional) Enter a custom folder name
5. (Optional) Enable "Add timestamp to filename"
6. Click "Upload to Google Drive"
7. Wait for the upload to complete

### View Your Media

1. Navigate to "View Gallery" page
2. (Optional) Filter by media type or folder
3. Click "Refresh Gallery" to reload
4. Click on image thumbnails to view
5. Expand "Details" for more information
6. Click "Open in Drive" to view in Google Drive
7. Click "Delete" to remove files

### Edit Images with API

1. Navigate to "API Testing" page
2. Select image source (URL, Upload, or Google Drive)
3. Enter your prompt
4. (Optional) Adjust advanced settings
5. (Optional) Enable "Auto-save results to Google Drive"
6. Click "Generate Image"
7. Wait for the results
8. Download or view the generated images

### Manage Files

1. Navigate to "File Manager" page
2. Use the navigation bar to browse folders
3. Select files using checkboxes
4. Use the action toolbar to:
   - Create new folders
   - Upload files
   - Delete selected files
   - Download selected files
5. Click "View" (👁️) to preview files

### Batch Operations

1. Navigate to "Batch Operations" page
2. Select an operation type
3. Follow the on-screen instructions
4. Select files or folders as needed
5. Execute the operation
6. Monitor progress

## 🔍 Troubleshooting

### "Please upload your Google Drive service account JSON file"

**Solution**: 
- Upload your service account JSON file in the sidebar
- Make sure the file is valid JSON
- Check that the service account has proper permissions

### "Failed to create/find folder"

**Solution**:
- Verify that the service account email has been shared with the folder
- Check that the service account has "Editor" permissions
- Make sure the Google Drive API is enabled in your Google Cloud project

### "API connection failed"

**Solution**:
- Verify your API key is correct
- Check your internet connection
- Ensure you have sufficient API credits
- Visit [kie.ai](https://kie.ai/api-key) to check your API key status

### "Failed to load image/video"

**Solution**:
- Check your internet connection
- Verify the file exists in Google Drive
- Try refreshing the page
- Check file permissions

### Files not appearing in gallery

**Solution**:
- Click "Refresh Gallery" button
- Check that you're viewing the correct folder
- Verify files were uploaded successfully
- Check the filter settings (All/Images/Videos)

### Upload fails

**Solution**:
- Check file size (large files may take longer)
- Verify file format is supported
- Check Google Drive storage quota
- Ensure stable internet connection

## 📝 Notes

- **File Storage**: All files are stored in your Google Drive, not on the application server
- **Privacy**: Your service account credentials are only stored in your browser session
- **API Usage**: Image editing API calls consume credits from your kie.ai account
- **Auto-Save**: When enabled, API results are automatically saved to your Google Drive
- **Session State**: Configuration is lost when you close the browser tab (you'll need to re-upload credentials)

## 🆘 Support

For issues related to:
- **Google Drive API**: Visit [Google Cloud Console](https://console.cloud.google.com/)
- **Image Edit API**: Visit [kie.ai Support](https://kie.ai/api-key)
- **Application Issues**: Check the debug information in the Settings page

## 🎉 Tips for Best Experience

1. **Keep credentials secure**: Never share your service account JSON file
2. **Use custom folders**: Organize your media by creating custom folders
3. **Add timestamps**: Enable timestamp option to avoid filename conflicts
4. **Batch operations**: Use batch operations for managing multiple files efficiently
5. **Auto-save API results**: Enable auto-save to keep all generated images in one place
6. **Regular backups**: Google Drive automatically backs up your files
7. **Monitor storage**: Check storage statistics in the Settings page

Enjoy using the Streamlit Google Drive Media Manager! 🚀
