# Local Python/Shell Executor Skill

## Description
Provides local code sandbox execution capabilities for autonomous problem-solving and data processing. Allows the agent to write and execute Python or Shell scripts directly, with full terminal output capture and error handling.

## Location
- **Skill Directory**: `/Users/kirin/.openclaw/workspace/skills/local-executor`
- **Main Module**: `local_executor.py`

## Capabilities
- Execute Python scripts with full output capture
- Execute Shell commands with environment control
- Capture stdout, stderr, and exit codes
- Handle timeouts and resource limits
- Provide detailed error logs for debugging
- Support interactive script development

## Usage Examples
- Data processing and analysis
- File system operations
- System diagnostics
- Custom tool creation
- Error debugging and log analysis

## Safety Features
- Timeout protection (default 30 seconds)
- Output size limits
- Error handling with detailed traceback
- Resource monitoring

## Dependencies
- Python 3.11+
- subprocess module (built-in)
- tempfile module (built-in)
- json module (built-in)