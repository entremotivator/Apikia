"""Google Drive Helper Module for Streamlit App"""

import io
import json
import os
from typing import Optional, List, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError


class GoogleDriveManager:
    """Manages Google Drive operations using service account credentials"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_json: dict):
        """
        Initialize Google Drive Manager
        
        Args:
            credentials_json: Service account credentials as dictionary
        """
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_json, scopes=self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.default_folder_name = "StreamlitMedia"
        self.default_folder_id = None
    
    def get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """
        Get existing folder or create new one
        
        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID
        """
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def ensure_default_folder(self) -> str:
        """
        Ensure default folder exists and return its ID
        
        Returns:
            Default folder ID
        """
        if not self.default_folder_id:
            self.default_folder_id = self.get_or_create_folder(self.default_folder_name)
        return self.default_folder_id
    
    def upload_file(self, file_path: str, file_name: Optional[str] = None, 
                   folder_id: Optional[str] = None, mime_type: Optional[str] = None) -> Optional[Dict]:
        """
        Upload file to Google Drive
        
        Args:
            file_path: Path to the file
            file_name: Name for the file in Drive (defaults to original name)
            folder_id: Folder ID to upload to (defaults to default folder)
            mime_type: MIME type of the file
            
        Returns:
            File metadata dictionary or None if failed
        """
        try:
            if not folder_id:
                folder_id = self.ensure_default_folder()
            
            if not file_name:
                file_name = os.path.basename(file_path)
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink, webContentLink, createdTime'
            ).execute()
            
            return file
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def upload_file_from_bytes(self, file_bytes: bytes, file_name: str, 
                               folder_id: Optional[str] = None, mime_type: Optional[str] = None) -> Optional[Dict]:
        """
        Upload file from bytes to Google Drive
        
        Args:
            file_bytes: File content as bytes
            file_name: Name for the file in Drive
            folder_id: Folder ID to upload to (defaults to default folder)
            mime_type: MIME type of the file
            
        Returns:
            File metadata dictionary or None if failed
        """
        try:
            if not folder_id:
                folder_id = self.ensure_default_folder()
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink, webContentLink, createdTime'
            ).execute()
            
            return file
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def list_files(self, folder_id: Optional[str] = None, mime_type_filter: Optional[str] = None) -> List[Dict]:
        """
        List files in a folder
        
        Args:
            folder_id: Folder ID to list files from (defaults to default folder)
            mime_type_filter: Filter by MIME type (e.g., 'image/', 'video/')
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            if not folder_id:
                folder_id = self.ensure_default_folder()
            
            query = f"'{folder_id}' in parents and trashed=false"
            
            if mime_type_filter:
                query += f" and mimeType contains '{mime_type_filter}'"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink, webContentLink, createdTime, size)',
                orderBy='createdTime desc'
            ).execute()
            
            return results.get('files', [])
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download file from Google Drive
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            File content as bytes or None if failed
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            downloader = MediaIoBaseDownload(file_bytes, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return file_bytes.getvalue()
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from Google Drive
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """
        Get file metadata
        
        Args:
            file_id: ID of the file
            
        Returns:
            File metadata dictionary or None if failed
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, webViewLink, webContentLink, createdTime, size'
            ).execute()
            
            return file
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
