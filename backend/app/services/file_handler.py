"""
File upload and handling service.
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Tuple
import aiofiles
from fastapi import UploadFile, HTTPException

from app.config import settings


class FileHandler:
    """Handles file uploads and management."""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.temp_dir = settings.temp_dir
        self.max_size = settings.max_upload_size
        self.allowed_extensions = settings.allowed_extensions
    
    async def save_upload(self, files: List[UploadFile]) -> Tuple[str, Path]:
        """
        Save uploaded files to a unique directory.
        
        Args:
            files: List of uploaded files
            
        Returns:
            Tuple of (upload_id, upload_path)
        """
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        upload_path = self.upload_dir / upload_id
        upload_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        try:
            for file in files:
                # Validate file
                self._validate_file(file)
                
                # Save file
                file_path = await self._save_file(file, upload_path)
                saved_files.append(file_path)
            
            return upload_id, upload_path
            
        except Exception as e:
            # Cleanup on error
            if upload_path.exists():
                shutil.rmtree(upload_path)
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file to validate
            
        Raises:
            HTTPException: If validation fails
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            )
    
    async def _save_file(self, file: UploadFile, upload_path: Path) -> Path:
        """
        Save a single file to disk.
        
        Args:
            file: File to save
            upload_path: Directory to save to
            
        Returns:
            Path to saved file
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(file.filename or "unnamed")
        file_path = upload_path / safe_filename
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file in chunks
        async with aiofiles.open(file_path, 'wb') as f:
            total_size = 0
            while chunk := await file.read(8192):  # 8KB chunks
                total_size += len(chunk)
                if total_size > self.max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {self.max_size / (1024*1024):.1f}MB"
                    )
                await f.write(chunk)
        
        return file_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace potentially dangerous characters
        dangerous_chars = ['..', '/', '\\', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def get_upload_path(self, upload_id: str) -> Path:
        """
        Get path for an upload ID.
        
        Args:
            upload_id: Upload identifier
            
        Returns:
            Path to upload directory
        """
        upload_path = self.upload_dir / upload_id
        if not upload_path.exists():
            raise HTTPException(status_code=404, detail=f"Upload {upload_id} not found")
        return upload_path
    
    def list_files(self, upload_path: Path) -> List[Path]:
        """
        List all files in an upload directory recursively.
        
        Args:
            upload_path: Path to upload directory
            
        Returns:
            List of file paths
        """
        files = []
        for item in upload_path.rglob('*'):
            if item.is_file():
                files.append(item)
        return files
    
    def cleanup_upload(self, upload_id: str) -> None:
        """
        Remove uploaded files.
        
        Args:
            upload_id: Upload identifier
        """
        upload_path = self.upload_dir / upload_id
        if upload_path.exists():
            shutil.rmtree(upload_path)
    
    def read_file_content(self, file_path: Path) -> str:
        """
        Read file content as text.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return ""
        except Exception:
            return ""
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'path': str(file_path),
            'size': stat.st_size,
            'extension': file_path.suffix,
            'modified': stat.st_mtime,
        }


# Global instance
file_handler = FileHandler()

# Made with Bob
