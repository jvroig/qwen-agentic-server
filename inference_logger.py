"""
Inference Logging Module for Qwen Agentic Server

Provides structured logging for inference operations including:
- Request/response tracking
- Tool execution logging  
- Session management
- Thinking tag cleaning verification
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional


class InferenceLogger:
    """Handles structured logging for inference operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize logger with configuration from logging_config.json"""
        self.config = config.get('logging', {})
        self.enabled = self.config.get('enabled', True)
        
        if not self.enabled:
            return
            
        # Setup log directories
        self.log_directory = self.config.get('destinations', {}).get('directory', 'logs/')
        self.inference_dir = os.path.join(self.log_directory, 'inference')
        self.errors_dir = os.path.join(self.log_directory, 'errors')
        
        # Create directories if they don't exist
        os.makedirs(self.inference_dir, exist_ok=True)
        os.makedirs(self.errors_dir, exist_ok=True)
        
        # Logging preferences
        self.to_console = self.config.get('destinations', {}).get('to_console', True)
        self.to_file = self.config.get('destinations', {}).get('to_file', True)
        
        # Privacy controls
        privacy_config = self.config.get('privacy', {})
        self.truncate_long = privacy_config.get('truncate_long_messages', False)
        self.max_length = privacy_config.get('max_message_length', 10000)
        
        # Payload logging controls
        payload_config = self.config.get('payloads', {})
        self.log_request_payloads = payload_config.get('request_payloads', True)
        self.log_user_messages = payload_config.get('user_messages', True) 
        self.log_assistant_responses = payload_config.get('assistant_responses', True)
        
        # Session tracking
        self.session_data = {}  # session_id -> session info
        
    def _get_daily_log_file(self) -> str:
        """Get path to today's inference log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.inference_dir, f'{today}.jsonl')
        
    def _truncate_if_needed(self, text: str) -> str:
        """Truncate text if privacy settings require it"""
        if not self.truncate_long or len(text) <= self.max_length:
            return text
        return text[:self.max_length] + "...[truncated]"
        
    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file and/or console"""
        if not self.enabled:
            return
            
        log_json = json.dumps(log_entry, ensure_ascii=False)
        
        # Console logging
        if self.to_console:
            print(f"[LOG] {log_json}")
            
        # File logging
        if self.to_file:
            try:
                log_file = self._get_daily_log_file()
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_json + '\n')
            except Exception as e:
                print(f"Failed to write log file: {e}")
    
    def log_inference_start(self, session_id: str, client_ip: str, payload: Dict[str, Any], model_name: str):
        """Log the start of an inference session"""
        if not self.enabled:
            return
            
        # Initialize session tracking
        self.session_data[session_id] = {
            'start_time': time.time(),
            'inference_rounds': 0,
            'tools_used': set(),
            'total_tokens': 0
        }
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event_type': 'inference_start',
            'client_ip': client_ip,
            'model': model_name
        }
        
        # Add payload if logging is enabled
        if self.log_request_payloads:
            # Filter payload based on privacy settings
            filtered_payload = {}
            
            if 'messages' in payload and self.log_user_messages:
                messages = payload['messages']
                if self.truncate_long:
                    messages = [
                        {**msg, 'content': self._truncate_if_needed(msg.get('content', ''))}
                        for msg in messages
                    ]
                filtered_payload['messages'] = messages
                
            # Always log temperature and token settings
            for key in ['temperature', 'max_output_tokens']:
                if key in payload:
                    filtered_payload[key] = payload[key]
                    
            log_entry['payload'] = filtered_payload
        
        self._write_log(log_entry)
    
    def log_assistant_response(self, session_id: str, inference_round: int, raw_response: str, 
                             cleaned_response: str, streaming_chunks: int = 0):
        """Log assistant response with thinking tag cleaning info"""
        if not self.enabled or not self.log_assistant_responses:
            return
            
        # Update session tracking
        if session_id in self.session_data:
            self.session_data[session_id]['inference_rounds'] = inference_round
            
        thinking_tags_found = raw_response != cleaned_response
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event_type': 'assistant_response', 
            'inference_round': inference_round,
            'thinking_tags_found': thinking_tags_found,
            'response_length': len(cleaned_response),
            'streaming_chunks': streaming_chunks
        }
        
        # Add response content if logging is enabled
        if self.log_assistant_responses:
            log_entry['raw_response'] = self._truncate_if_needed(raw_response)
            log_entry['cleaned_response'] = self._truncate_if_needed(cleaned_response)
        
        self._write_log(log_entry)
    
    def log_tool_execution(self, session_id: str, tool_name: str, tool_input: Dict[str, Any], 
                          tool_result: str, execution_time_ms: float, success: bool):
        """Log tool execution details"""
        if not self.enabled:
            return
            
        # Update session tracking
        if session_id in self.session_data:
            self.session_data[session_id]['tools_used'].add(tool_name)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event_type': 'tool_execution',
            'tool_name': tool_name,
            'tool_input': tool_input,
            'execution_time_ms': execution_time_ms,
            'success': success
        }
        
        # Truncate tool result if needed
        if tool_result:
            log_entry['tool_result'] = self._truncate_if_needed(tool_result)
        
        self._write_log(log_entry)
    
    def log_session_complete(self, session_id: str, final_status: str = "completed"):
        """Log session completion with summary statistics"""
        if not self.enabled or session_id not in self.session_data:
            return
            
        session_info = self.session_data[session_id]
        end_time = time.time()
        duration = end_time - session_info['start_time']
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event_type': 'session_complete',
            'total_rounds': session_info['inference_rounds'],
            'tools_used': list(session_info['tools_used']),
            'total_tokens': session_info.get('total_tokens', 0),
            'duration_seconds': round(duration, 3),
            'final_status': final_status
        }
        
        self._write_log(log_entry)
        
        # Clean up session data
        del self.session_data[session_id]
    
    def log_error(self, session_id: str, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors during inference"""
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event_type': 'error',
            'error_type': error_type,
            'error_message': error_message
        }
        
        if context:
            log_entry['context'] = context
            
        self._write_log(log_entry)
        
        # Also write to error log file
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            error_file = os.path.join(self.errors_dir, f'{today}.log')
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(f"[{log_entry['timestamp']}] {session_id}: {error_type} - {error_message}\n")
        except Exception as e:
            print(f"Failed to write error log: {e}")


# Global logger instance
_logger_instance = None

def get_logger() -> InferenceLogger:
    """Get the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        # Load config
        try:
            with open('logging_config.json', 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load logging_config.json: {e}")
            config = {'logging': {'enabled': False}}
        
        _logger_instance = InferenceLogger(config)
    
    return _logger_instance