#!/usr/bin/env python3
"""
Local Python/Shell Executor Skill for OpenClaw
Provides secure local code execution capabilities for autonomous problem-solving and data processing
"""

import subprocess
import sys
import os
import tempfile
import json
import signal
from pathlib import Path

class LocalExecutor:
    def __init__(self, timeout=30, max_output_size=10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.working_dir = Path(tempfile.mkdtemp(prefix="openclaw_exec_"))
        
    def execute_shell(self, command, cwd=None, env=None):
        """
        Execute a shell command securely
        
        Args:
            command: Shell command to execute
            cwd: Working directory (defaults to temp dir)
            env: Environment variables (defaults to current env with PATH)
            
        Returns:
            dict with stdout, stderr, returncode, and success status
        """
        if cwd is None:
            cwd = str(self.working_dir)
            
        if env is None:
            env = os.environ.copy()
            # Ensure basic PATH is set
            if 'PATH' not in env:
                env['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin'
                
        try:
            # Use timeout and limit output
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Create new process group for proper cleanup
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                
                # Truncate output if too large
                if len(stdout) > self.max_output_size:
                    stdout = stdout[:self.max_output_size] + f"\n... (output truncated, {len(stdout)} chars total)"
                if len(stderr) > self.max_output_size:
                    stderr = stderr[:self.max_output_size] + f"\n... (output truncated, {len(stderr)} chars total)"
                    
                return {
                    'success': process.returncode == 0,
                    'stdout': stdout,
                    'stderr': stderr,
                    'returncode': process.returncode,
                    'command': command
                }
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': f'Command timed out after {self.timeout} seconds',
                    'returncode': -1,
                    'command': command
                }
                
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'returncode': -1,
                'command': command
            }
    
    def execute_python(self, code, args=None, cwd=None, env=None):
        """
        Execute Python code securely
        
        Args:
            code: Python code string or path to .py file
            args: Command line arguments for the script
            cwd: Working directory
            env: Environment variables
            
        Returns:
            dict with execution results
        """
        if cwd is None:
            cwd = str(self.working_dir)
            
        # Create temporary Python file if code is a string
        if code.endswith('.py') and os.path.exists(code):
            script_path = code
        else:
            script_path = self.working_dir / "temp_script.py"
            with open(script_path, 'w') as f:
                f.write(code)
                
        # Build command
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
            
        return self.execute_shell(' '.join(cmd), cwd=cwd, env=env)
    
    def execute_with_input(self, command, input_data, cwd=None, env=None):
        """
        Execute command with stdin input
        """
        if cwd is None:
            cwd = str(self.working_dir)
            
        if env is None:
            env = os.environ.copy()
            if 'PATH' not in env:
                env['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin'
                
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            
            try:
                stdout, stderr = process.communicate(input=input_data, timeout=self.timeout)
                
                if len(stdout) > self.max_output_size:
                    stdout = stdout[:self.max_output_size] + f"\n... (output truncated, {len(stdout)} chars total)"
                if len(stderr) > self.max_output_size:
                    stderr = stderr[:self.max_output_size] + f"\n... (output truncated, {len(stderr)} chars total)"
                    
                return {
                    'success': process.returncode == 0,
                    'stdout': stdout,
                    'stderr': stderr,
                    'returncode': process.returncode,
                    'command': command
                }
                
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': f'Command timed out after {self.timeout} seconds',
                    'returncode': -1,
                    'command': command
                }
                
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'returncode': -1,
                'command': command
            }
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.working_dir)
        except Exception:
            pass

# CLI interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description='Local Code Executor')
    parser.add_argument('--shell', help='Shell command to execute')
    parser.add_argument('--python', help='Python code or file to execute')
    parser.add_argument('--args', nargs='*', help='Arguments for Python script')
    parser.add_argument('--input', help='Input data for stdin')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    parser.add_argument('--max-output', type=int, default=10000, help='Max output size')
    
    args = parser.parse_args()
    
    executor = LocalExecutor(timeout=args.timeout, max_output_size=args.max_output)
    
    try:
        if args.shell:
            if args.input:
                result = executor.execute_with_input(args.shell, args.input)
            else:
                result = executor.execute_shell(args.shell)
        elif args.python:
            result = executor.execute_python(args.python, args.args)
        else:
            print("Error: Please specify --shell or --python")
            return 1
            
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result['success'] else 1
        
    finally:
        executor.cleanup()

if __name__ == "__main__":
    sys.exit(main())