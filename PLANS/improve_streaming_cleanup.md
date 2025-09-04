# Improve Streaming Logger Cleanup - Time-Based Approach

## Problem Statement

The current streaming logger immediately deletes session files when sessions complete. While this works fine from an I/O perspective, it could be improved to:
- **Provide debugging window**: Keep completed session files around for investigation
- **Batch I/O operations**: Reduce filesystem operation frequency
- **Non-blocking completion**: Remove file deletion from session completion path
- **Configurable retention**: Allow admins to control how long files are kept

## Current Behavior

```python
def complete_session(self, session_id: str):
    # ... flush and close file ...
    os.remove(file_path)  # Immediate deletion
    print(f"Deleted streaming log: {file_path}")
```

**Issues:**
- No debugging window - files disappear immediately when session ends
- File deletion blocks session completion (minimal, but still I/O)
- No opportunity to investigate completed sessions

## Proposed Solution: Time-Based Cleanup

### Core Concept
**Decouple session completion from file deletion** - let completed files sit in the directory for a configurable period (default 10 minutes), then clean them up via background process.

### Implementation Details

#### 1. Modified Session Completion
```python
def complete_session(self, session_id: str):
    """Mark session as complete but leave file for debugging window"""
    if not self.enabled or session_id not in self.session_files:
        return
        
    # Final flush and close file
    self._flush_session(session_id, force=True)
    
    with self.lock:
        # Close file handle but KEEP the file on disk
        if session_id in self.session_files:
            self.session_files[session_id].close()
            del self.session_files[session_id]  # Remove from active tracking
        
        # Clean up in-memory session data
        if session_id in self.session_buffers:
            del self.session_buffers[session_id]
        if session_id in self.last_flush:
            del self.last_flush[session_id]
    
    print(f"Session {session_id} completed, file kept for debugging")
```

**Key change:** Remove `os.remove()` call - file stays on disk but session is no longer tracked in `self.session_files`.

#### 2. Enhanced Background Worker
```python
def _flush_worker(self):
    """Background worker for buffer flushing and file cleanup"""
    cleanup_interval = 60  # Clean up every 60 seconds (configurable)
    last_cleanup = 0
    
    while True:
        time.sleep(self.flush_interval)  # Still flush every 2 seconds
        
        if not self.enabled:
            continue
        
        # Regular buffer flushing for active sessions
        with self.lock:
            active_sessions = list(self.session_buffers.keys())
        
        for session_id in active_sessions:
            self._flush_session(session_id)
        
        # Periodic cleanup of completed files
        current_time = time.time()
        if current_time - last_cleanup > cleanup_interval:
            self._cleanup_completed_files()
            last_cleanup = current_time

def _cleanup_completed_files(self, retention_minutes: int = 10):
    """Delete completed session files older than retention period"""
    if not self.enabled:
        return
        
    cutoff_time = time.time() - (retention_minutes * 60)
    deleted_count = 0
    
    try:
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(self.base_dir, filename)
                session_id = filename.replace('.log', '')
                
                # Skip files that are still actively being written to
                if session_id in self.session_files:
                    continue  # This session is still active
                
                # Delete old completed files
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} completed session files")
            
    except Exception as e:
        print(f"Failed to cleanup completed files: {e}")
```

#### 3. Configuration Options
Add to `logging_config.json`:
```json
{
  "streaming_logs": {
    "enabled": true,
    "flush_interval_seconds": 2,
    "cleanup_interval_seconds": 60,
    "file_retention_minutes": 10,
    "max_session_age_hours": 24
  }
}
```

**Configuration Parameters:**
- `cleanup_interval_seconds`: How often to run cleanup (default: 60s)
- `file_retention_minutes`: How long to keep completed files (default: 10min)
- `max_session_age_hours`: Emergency cleanup for very old files (default: 24h)

### Active Session Detection Logic

**Key insight:** `self.session_files` tracks actively streaming sessions.

```python
# Active session - file handle is open and being written to
session_id in self.session_files  # True

# Completed session - file handle closed, but file still on disk  
session_id not in self.session_files  # True - safe to delete if old enough
```

This prevents cleanup from accidentally deleting files that are still being streamed to.

### Benefits

#### 1. Debugging Window
```bash
# Session completes at 14:30
ls logs/streaming/
# sess_abc123.log  # Still available for investigation!

# Session file remains until 14:40 (10-minute window)
tail logs/streaming/sess_abc123.log  # Can examine what was generated

# At 14:40, background cleanup removes it automatically
```

#### 2. Batch I/O Efficiency
- **Single cleanup sweep** every 60 seconds
- **Multiple file deletions** batched together  
- **Reduced filesystem churn** compared to immediate deletion
- **Non-blocking session completion** - no I/O during session end

#### 3. Operational Benefits
- **Zero-downtime debugging** - can examine recent sessions
- **Configurable retention** - adjust based on debugging needs
- **Automatic cleanup** - no manual intervention needed
- **Emergency cleanup** - prevents disk space issues from failed cleanup

### Directory State Examples

#### During Normal Operation
```
logs/streaming/
├── sess_active1.log     # Currently streaming (in self.session_files)
├── sess_active2.log     # Currently streaming (in self.session_files)  
├── sess_completed1.log  # Completed 3 mins ago (debugging window)
├── sess_completed2.log  # Completed 7 mins ago (debugging window)
└── sess_completed3.log  # Completed 12 mins ago (will be cleaned next cycle)
```

#### After Cleanup Cycle
```
logs/streaming/
├── sess_active1.log     # Still streaming
├── sess_active2.log     # Still streaming
├── sess_completed1.log  # Still in 10-min window
└── sess_completed2.log  # Still in 10-min window
# sess_completed3.log deleted - exceeded 10-min retention
```

### Implementation Steps

#### Phase 1: Basic Time-Based Cleanup
1. **Remove immediate deletion** from `complete_session()`
2. **Add cleanup logic** to `_flush_worker()`  
3. **Add configuration** for cleanup timing
4. **Test with short retention** (2-3 minutes) to verify behavior

#### Phase 2: Enhanced Configuration
1. **Load cleanup settings** from `logging_config.json`
2. **Add validation** for configuration parameters
3. **Add cleanup statistics** logging
4. **Test with production-like loads**

#### Phase 3: Operational Improvements  
1. **Add cleanup metrics** (files cleaned, errors, timing)
2. **Emergency cleanup** for disk space protection
3. **Graceful degradation** if cleanup fails
4. **Documentation** for operators

### Testing Strategy

#### Unit Tests
- **Cleanup timing logic** - verify files deleted at correct intervals
- **Active session detection** - ensure active files never deleted
- **Configuration loading** - test parameter validation
- **Error handling** - cleanup failures, missing directories, etc.

#### Integration Tests
- **Real session lifecycle** - stream → complete → cleanup
- **Multiple concurrent sessions** - ensure proper tracking
- **Background worker behavior** - timing, batching, error recovery
- **Disk space scenarios** - large numbers of files

#### Load Testing
- **High session turnover** - many sessions completing rapidly
- **Long-running sessions** - ensure active detection works
- **Cleanup performance** - large numbers of completed files
- **Configuration changes** - runtime parameter updates

### Migration Considerations

#### Backward Compatibility
- **Configuration optional** - falls back to current immediate deletion
- **Existing deployments** - no breaking changes to API
- **Gradual rollout** - can be enabled per deployment

#### Rollback Plan
- **Feature flag** in configuration to disable time-based cleanup
- **Falls back** to immediate deletion if background worker fails
- **No data loss** - worst case is files not being cleaned up

### Success Metrics

#### Functionality
- ✅ **Debugging capability**: Completed session files available for investigation
- ✅ **Automatic cleanup**: Files cleaned up without manual intervention  
- ✅ **Zero active file deletion**: Never delete files being actively written
- ✅ **Configurable retention**: Operators can adjust timing based on needs

#### Performance
- **Reduced I/O frequency**: Batch deletions vs per-session deletions
- **Non-blocking completion**: Session completion doesn't wait for file deletion
- **Bounded disk usage**: Files cleaned up before accumulating indefinitely

#### Operations
- **Simple configuration**: Clear parameters for retention timing
- **Observable behavior**: Logging shows cleanup activity and statistics
- **Error resilience**: Cleanup failures don't impact active sessions

---

**Priority:** Medium - Operational improvement that enhances debugging capability  
**Complexity:** Low-Medium - Straightforward background processing with timing logic  
**Timeline:** Can be implemented immediately, minimal risk to existing functionality  
**Dependencies:** None - purely additive enhancement to existing streaming logger