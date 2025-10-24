import aiofiles
import os
import time
from pathlib import Path
from fastapi import UploadFile
import uuid
from typing import List
import asyncio

class FileHandler:
    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.static_dir = Path("static/audio")
        self.temp_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_ttl = int(os.getenv("FILE_TTL", 1800))  # 30 minutes
    
    async def save_temp_file(self, upload_file: UploadFile) -> str:
        """Save uploaded file to temp directory"""
        file_id = str(uuid.uuid4())[:8]
        file_extension = Path(upload_file.filename).suffix if upload_file.filename else '.tmp'
        temp_filename = f"temp_{file_id}{file_extension}"
        temp_path = self.temp_dir / temp_filename
        
        async with aiofiles.open(temp_path, "wb") as f:
            content = await upload_file.read()
            await f.write(content)
        
        return str(temp_path)
    
    async def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up specific temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")
    
    async def cleanup_old_files(self):
        """Clean up old files based on TTL"""
        current_time = time.time()
        
        # Clean temp files
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > self.file_ttl:
                    try:
                        file_path.unlink()
                        print(f"🗑️ Cleaned up old temp file: {file_path.name}")
                    except Exception as e:
                        print(f"Warning: Could not delete {file_path}: {e}")
        
        # Clean old audio files (longer TTL)
        audio_ttl = self.file_ttl * 2  # 1 hour for generated audio
        for file_path in self.static_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > audio_ttl:
                    try:
                        file_path.unlink()
                        print(f"🗑️ Cleaned up old audio file: {file_path.name}")
                    except Exception as e:
                        print(f"Warning: Could not delete {file_path}: {e}")
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return str(int(time.time()))
