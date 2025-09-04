# Qwen Agentic Server - Inference Logging Plan

## Problem Statement

The qwen-agentic-server currently lacks comprehensive logging for inference operations, making it difficult to:
- **Debug issues**: Track conversation flows, tool executions, and errors
- **Verify features**: Confirm thinking tag cleaning is working correctly
- **Enterprise compliance**: Meet audit requirements for AI system usage
- **Performance monitoring**: Analyze response times, token usage, and tool efficiency
- **Security auditing**: Track API usage patterns and potential misuse

## Solution Overview

Implement a multi-tier logging system that scales from simple debugging logs to enterprise-grade audit trails.

### Phase 1: Basic Inference Logging (Immediate)
- Request/response logging for debugging
- Conversation flow tracking
- Thinking tag cleaning verification

### Phase 2: Enterprise Audit Logging (Future)
- Comprehensive audit trails with structured data
- Compliance-ready logs with retention policies
- Security and usage analytics

## Phase 1: Basic Inference Logging

### Core Logging Requirements

#### 1. Request Logging
```json
{
  "timestamp": "2025-01-15T14:30:15.123Z",
  "session_id": "sess_abc123",
  "event_type": "inference_start",
  "client_ip": "192.168.1.100",
  "payload": {
    "messages": [...],
    "temperature": 0.7,
    "max_output_tokens": 5000
  },
  "model": "qwen2.5-72b-instruct"
}
```

#### 2. Response Tracking
```json
{
  "timestamp": "2025-01-15T14:30:18.456Z",
  "session_id": "sess_abc123", 
  "event_type": "assistant_response",
  "inference_round": 1,
  "raw_response": "<think>I need to read the file</think>I'll analyze the data file",
  "cleaned_response": "I'll analyze the data file",
  "thinking_tags_found": true,
  "response_length": 156,
  "streaming_chunks": 23
}
```

#### 3. Tool Execution Logging
```json
{
  "timestamp": "2025-01-15T14:30:19.789Z",
  "session_id": "sess_abc123",
  "event_type": "tool_execution",
  "tool_name": "read_file",
  "tool_input": {"file_path": "/path/to/data.csv"},
  "tool_result": "File contents: ...",
  "execution_time_ms": 45,
  "success": true
}
```

#### 4. Session Completion
```json
{
  "timestamp": "2025-01-15T14:30:25.012Z",
  "session_id": "sess_abc123",
  "event_type": "session_complete", 
  "total_rounds": 3,
  "tools_used": ["read_file", "write_file"],
  "total_tokens": 1247,
  "duration_seconds": 9.889,
  "final_status": "completed"
}
```

### Implementation Details

#### Log File Structure
```
logs/
├── inference/
│   ├── 2025-01-15.jsonl          # Daily inference logs
│   ├── 2025-01-14.jsonl
│   └── ...
├── errors/
│   ├── 2025-01-15.log            # Error logs  
│   └── ...
└── audit/                        # Future: Enterprise logs
    └── ...
```

#### Configuration Options
```python
# Log levels
LOGGING_LEVEL = "INFO"  # DEBUG, INFO, WARN, ERROR

# Log destinations  
LOG_TO_FILE = True
LOG_TO_CONSOLE = True  # For development
LOG_DIRECTORY = "logs/"

# Retention policy
LOG_RETENTION_DAYS = 30  # Basic retention

# Privacy controls
LOG_FULL_MESSAGES = True      # Set False for privacy
LOG_THINKING_TAGS = True      # Verify cleaning works
LOG_TOOL_RESULTS = True       # May contain sensitive data
```

#### Code Integration Points

1. **Session Start** (qwen_api.py:query_endpoint)
   - Generate session_id
   - Log initial request

2. **Assistant Response** (qwen_api.py:inference_loop after line 143)
   - Log raw vs cleaned response
   - Track thinking tag cleaning effectiveness

3. **Tool Execution** (qwen_api.py:execute_tool)
   - Log tool calls and results
   - Track execution times

4. **Session End** (qwen_api.py:inference_loop when breaking)
   - Log session summary statistics

### Testing & Validation

#### Verification Scenarios
1. **Thinking Tag Cleaning**: Compare raw vs cleaned responses
2. **Multi-round Conversations**: Track conversation flow
3. **Tool Usage**: Verify tool execution logging
4. **Error Handling**: Ensure errors are properly logged

#### Log Analysis Scripts
```bash
# Check thinking tag cleaning effectiveness
grep "thinking_tags_found.*true" logs/inference/$(date +%Y-%m-%d).jsonl

# Tool usage statistics
jq '.tool_name' logs/inference/$(date +%Y-%m-%d).jsonl | sort | uniq -c

# Average session duration  
jq '.duration_seconds' logs/inference/$(date +%Y-%m-%d).jsonl | awk '{sum+=$1} END {print sum/NR}'
```

## Phase 2: Enterprise Audit Logging (Future)

### Advanced Features
- **Structured audit trails** with tamper-proof logging
- **Data classification** and PII detection
- **Compliance reporting** (SOC2, GDPR, HIPAA ready)
- **Real-time monitoring** and alerting
- **Log aggregation** and centralized management
- **Retention policies** with automatic archival

### Enterprise Log Format
```json
{
  "audit_id": "audit_789xyz",
  "timestamp": "2025-01-15T14:30:15.123Z",
  "user_id": "user_456",
  "organization_id": "org_123",
  "session_id": "sess_abc123",
  "classification": "internal",
  "pii_detected": false,
  "compliance_tags": ["gdpr", "soc2"],
  "data_retention_class": "standard_30_days",
  "geographic_region": "us-east-1",
  "model_version": "qwen2.5-72b-instruct-v1.2",
  "cost_tracking": {
    "input_tokens": 324,
    "output_tokens": 856,
    "tool_executions": 2,
    "estimated_cost_usd": 0.0234
  }
}
```

## Implementation Steps (Phase 1)

### Step 1: Basic Logging Infrastructure
1. Add Python logging configuration
2. Create log directory structure  
3. Implement session ID generation
4. Add basic request/response logging

### Step 2: Conversation Flow Logging
1. Log assistant responses (raw vs cleaned)
2. Add thinking tag cleaning verification
3. Track inference rounds and tool calls

### Step 3: Error and Performance Logging
1. Comprehensive error logging
2. Performance metrics (timing, token counts)
3. Tool execution tracking

### Step 4: Analysis Tools
1. Log parsing utilities
2. Basic analytics scripts
3. Thinking tag cleaning verification tools

### Step 5: Configuration and Documentation
1. Configurable logging levels and destinations
2. Documentation for log formats
3. Operational runbooks

## Success Criteria

### Phase 1 Goals
- ✅ **Debugging capability**: Easy to trace conversation flows and issues
- ✅ **Feature verification**: Confirm thinking tag cleaning works correctly
- ✅ **Basic audit trail**: Track API usage and tool executions
- ✅ **Performance monitoring**: Response times and resource usage
- ✅ **Error tracking**: Comprehensive error logging and debugging

### Metrics to Track
- **Thinking tag cleaning rate**: % of responses with thinking tags successfully cleaned
- **Session completion rate**: % of sessions that complete without errors
- **Tool execution success rate**: % of successful tool calls
- **Average response time**: Per inference round and overall session
- **Token efficiency**: Input/output token ratios

## Risk Mitigation

### Privacy Considerations
- **Configurable PII logging**: Option to exclude sensitive data
- **Log encryption**: Protect logs at rest
- **Access controls**: Restricted log file permissions

### Performance Impact
- **Asynchronous logging**: Non-blocking log writes
- **Log rotation**: Prevent disk space issues
- **Configurable verbosity**: Control log detail level

### Compliance Readiness
- **Structured formats**: JSON logs for easy parsing
- **Retention policies**: Automated cleanup
- **Audit trail integrity**: Tamper-evident logging

---

**Priority:** High - Essential for debugging thinking tag cleaning and future enterprise features  
**Complexity:** Medium - Well-established logging patterns  
**Timeline:** Phase 1 can be implemented immediately alongside thinking tag cleaning  
**Dependencies:** None - self-contained enhancement