"""
Streaming Token Logger for Qwen Agentic Server

Provides real-time logging of streaming LLM output for debugging runaway generation,
infinite loops, and monitoring active inference sessions.
"""

import os
import time
import threading
from collections import defaultdict
from typing import Dict


class StreamingLogger:
    """Handles real-time streaming token logging per session"""
    
    def __init__(self, config: Dict[str, any] = None):
        """Initialize streaming logger with configuration"""
        self.config = config or {}
        streaming_config = self.config.get('streaming_logs', {})
        
        self.enabled = streaming_config.get('enabled', True)
        self.flush_interval = streaming_config.get('flush_interval_seconds', 2)
        
        if not self.enabled:
            return
            
        # Setup directory (flat structure - no subfolders)
        self.base_dir = 'logs/streaming'
        
        # Create directory
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Session management
        self.session_buffers = defaultdict(list)  # session_id -> list of chunks
        self.session_files = {}  # session_id -> file handle
        self.last_flush = defaultdict(float)  # session_id -> last flush timestamp
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Background flush thread
        self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self.flush_thread.start()
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Get file path for session log"""
        return os.path.join(self.base_dir, f'{session_id}.log')
    
    def _ensure_session_file(self, session_id: str):
        """Ensure session file is open and ready"""
        if session_id not in self.session_files:
            file_path = self._get_session_file_path(session_id)
            self.session_files[session_id] = open(file_path, 'a', encoding='utf-8')
    
    def _flush_session(self, session_id: str, force: bool = False):
        """Flush buffered chunks for a session to disk"""
        if not self.enabled:
            return
            
        current_time = time.time()
        
        # Check if we need to flush (based on time interval or force)
        if not force and current_time - self.last_flush[session_id] < self.flush_interval:
            return
            
        if session_id in self.session_buffers and self.session_buffers[session_id]:
            with self.lock:
                chunks = self.session_buffers[session_id]
                if chunks:
                    self._ensure_session_file(session_id)
                    
                    # Write all buffered chunks
                    content = ''.join(chunks)
                    self.session_files[session_id].write(content)
                    self.session_files[session_id].flush()  # Ensure immediate write to disk
                    
                    # Clear buffer and update flush time
                    self.session_buffers[session_id] = []
                    self.last_flush[session_id] = current_time
    
    def _flush_worker(self):
        """Background worker to flush buffers periodically"""
        while True:
            time.sleep(self.flush_interval)
            if not self.enabled:
                continue
                
            # Flush all active sessions
            with self.lock:
                session_ids = list(self.session_buffers.keys())
            
            for session_id in session_ids:
                self._flush_session(session_id)
    
    def append_chunk(self, session_id: str, content: str):
        """Add a streaming chunk to the session log"""
        if not self.enabled or not session_id or not content:
            return
            
        with self.lock:
            self.session_buffers[session_id].append(content)
    
    def complete_session(self, session_id: str):
        """Mark session as complete and delete streaming log file"""
        if not self.enabled or session_id not in self.session_files:
            return
            
        # Final flush
        self._flush_session(session_id, force=True)
        
        with self.lock:
            # Close and delete session file
            if session_id in self.session_files:
                self.session_files[session_id].close()
                del self.session_files[session_id]
            
            # Delete the streaming log file
            file_path = self._get_session_file_path(session_id)
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted streaming log: {file_path}")
            except Exception as e:
                print(f"Failed to delete streaming log for {session_id}: {e}")
            
            # Clean up session data
            if session_id in self.session_buffers:
                del self.session_buffers[session_id]
            if session_id in self.last_flush:
                del self.last_flush[session_id]
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Delete old session files (in case of crashes or orphaned sessions)"""
        if not self.enabled:
            return
            
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        try:
            for filename in os.listdir(self.base_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(self.base_dir, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        # Delete old session files directly
                        os.remove(file_path)
                        print(f"Cleaned up old session file: {file_path}")
        except Exception as e:
            print(f"Failed to cleanup old sessions: {e}")


# Global streaming logger instance
_streaming_logger_instance = None

def get_streaming_logger() -> StreamingLogger:
    """Get the global streaming logger instance"""
    global _streaming_logger_instance
    if _streaming_logger_instance is None:
        # Load config from main logging config
        try:
            import json
            with open('logging_config.json', 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load logging_config.json for streaming logger: {e}")
            config = {}
        
        _streaming_logger_instance = StreamingLogger(config)
    
    return _streaming_logger_instance