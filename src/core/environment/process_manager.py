"""
Process Manager for HyperSync
Enables agents to execute real programs with resource and policy oversight.
"""

import os
import sys
import subprocess
import threading
import logging
import signal
import time
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """Process execution states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"


@dataclass
class ProcessResult:
    """Result of process execution"""
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str
    state: ProcessState
    duration_seconds: float
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "state": self.state.value,
            "duration_seconds": self.duration_seconds,
            "pid": self.pid,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }

    @property
    def success(self) -> bool:
        """Check if process completed successfully"""
        return self.state == ProcessState.COMPLETED and self.exit_code == 0


@dataclass
class ProcessConfig:
    """Configuration for process execution"""
    command: List[str]
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: Optional[float] = None
    capture_output: bool = True
    shell: bool = False
    stdin_data: Optional[str] = None
    max_output_size: int = 10 * 1024 * 1024  # 10MB default

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "cwd": self.cwd,
            "env": self.env,
            "timeout": self.timeout,
            "capture_output": self.capture_output,
            "shell": self.shell,
            "max_output_size": self.max_output_size
        }


class ProcessMonitor:
    """Monitors running process"""

    def __init__(self, process: subprocess.Popen, config: ProcessConfig):
        self.process = process
        self.config = config
        self.started_at = datetime.utcnow()
        self.stdout_data = []
        self.stderr_data = []
        self.total_output_size = 0
        self._lock = threading.Lock()

    def read_output(self) -> Tuple[str, str]:
        """Read stdout and stderr"""
        try:
            stdout, stderr = self.process.communicate(
                input=self.config.stdin_data.encode() if self.config.stdin_data else None,
                timeout=self.config.timeout
            )

            stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""

            # Truncate if too large
            if len(stdout_str) > self.config.max_output_size:
                stdout_str = stdout_str[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED]"
            if len(stderr_str) > self.config.max_output_size:
                stderr_str = stderr_str[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED]"

            return stdout_str, stderr_str

        except subprocess.TimeoutExpired:
            # Kill process on timeout
            self.process.kill()
            stdout, stderr = self.process.communicate()

            stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""

            raise

    def get_duration(self) -> float:
        """Get process duration in seconds"""
        return (datetime.utcnow() - self.started_at).total_seconds()


class ProcessManager:
    """Manages process execution with resource and policy controls"""

    def __init__(self, sandbox=None):
        """
        Initialize process manager.

        Args:
            sandbox: Optional sandbox for policy enforcement
        """
        self.sandbox = sandbox
        self.active_processes: Dict[int, ProcessMonitor] = {}
        self.process_history: List[ProcessResult] = []
        self._lock = threading.Lock()

        logger.info("ProcessManager initialized")

    def run(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        capture_output: bool = True,
        shell: bool = False,
        stdin_data: Optional[str] = None
    ) -> ProcessResult:
        """
        Execute a command and wait for completion.

        Args:
            command: Command and arguments to execute
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds
            capture_output: Capture stdout/stderr
            shell: Execute through shell
            stdin_data: Data to send to stdin

        Returns:
            ProcessResult with execution details
        """
        config = ProcessConfig(
            command=command,
            cwd=cwd,
            env=env,
            timeout=timeout,
            capture_output=capture_output,
            shell=shell,
            stdin_data=stdin_data
        )

        # Check policy if sandbox is configured
        if self.sandbox:
            if not self._check_execution_policy(config):
                return ProcessResult(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    state=ProcessState.FAILED,
                    duration_seconds=0.0,
                    error="Execution denied by policy"
                )

        logger.info(f"Executing command: {' '.join(command)}")

        started_at = datetime.utcnow()
        state = ProcessState.PENDING

        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            # Resolve working directory
            if cwd:
                cwd = str(Path(cwd).resolve())
                if not os.path.exists(cwd):
                    raise FileNotFoundError(f"Working directory not found: {cwd}")

            # Start process
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=process_env,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                stdin=subprocess.PIPE if stdin_data else None,
                shell=shell
            )

            state = ProcessState.RUNNING
            monitor = ProcessMonitor(process, config)

            with self._lock:
                self.active_processes[process.pid] = monitor

            logger.info(f"Process started: PID={process.pid}")

            # Read output and wait for completion
            try:
                stdout, stderr = monitor.read_output()
                exit_code = process.returncode
                state = ProcessState.COMPLETED

            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
                exit_code = -1
                state = ProcessState.TIMEOUT
                logger.warning(f"Process timeout: PID={process.pid}")

            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()

            result = ProcessResult(
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                state=state,
                duration_seconds=duration,
                pid=process.pid,
                started_at=started_at,
                completed_at=completed_at
            )

            logger.info(f"Process completed: PID={process.pid}, exit_code={exit_code}, duration={duration:.2f}s")

        except FileNotFoundError as e:
            result = ProcessResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                state=ProcessState.FAILED,
                duration_seconds=0.0,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                error=f"Command not found: {command[0]}"
            )
            logger.error(f"Command not found: {command[0]}")

        except Exception as e:
            result = ProcessResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                state=ProcessState.FAILED,
                duration_seconds=0.0,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                error=str(e)
            )
            logger.error(f"Process execution failed: {e}")

        finally:
            # Remove from active processes
            if 'process' in locals() and process.pid in self.active_processes:
                with self._lock:
                    del self.active_processes[process.pid]

        # Store in history
        with self._lock:
            self.process_history.append(result)

        return result

    def run_async(
        self,
        command: List[str],
        callback: Optional[Callable[[ProcessResult], None]] = None,
        **kwargs
    ) -> threading.Thread:
        """
        Execute command asynchronously.

        Args:
            command: Command to execute
            callback: Optional callback when process completes
            **kwargs: Additional arguments for run()

        Returns:
            Thread object
        """
        def _run_thread():
            result = self.run(command, **kwargs)
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Callback failed: {e}")

        thread = threading.Thread(target=_run_thread, daemon=True)
        thread.start()
        return thread

    def kill_process(self, pid: int) -> bool:
        """
        Kill a running process.

        Args:
            pid: Process ID to kill

        Returns:
            True if killed, False if not found
        """
        with self._lock:
            monitor = self.active_processes.get(pid)

        if not monitor:
            logger.warning(f"Process not found: PID={pid}")
            return False

        try:
            if sys.platform == "win32":
                monitor.process.terminate()
            else:
                os.kill(pid, signal.SIGTERM)

            logger.info(f"Killed process: PID={pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False

    def list_active_processes(self) -> List[Dict]:
        """List all active processes"""
        with self._lock:
            return [
                {
                    "pid": pid,
                    "command": monitor.config.command,
                    "cwd": monitor.config.cwd,
                    "duration": monitor.get_duration()
                }
                for pid, monitor in self.active_processes.items()
            ]

    def get_history(self, limit: Optional[int] = None) -> List[ProcessResult]:
        """Get process execution history"""
        with self._lock:
            if limit:
                return self.process_history[-limit:]
            return self.process_history.copy()

    def _check_execution_policy(self, config: ProcessConfig) -> bool:
        """Check if execution is allowed by policy"""
        if not self.sandbox:
            return True

        # Check if working directory is accessible
        if config.cwd:
            if not self.sandbox.check_access(config.cwd, "execute"):
                logger.warning(f"Execution denied: cwd not accessible: {config.cwd}")
                return False

        # Additional policy checks could be added here
        # - Check if command is in allowed list
        # - Check resource limits
        # - Check clearance requirements

        return True

    def get_stats(self) -> Dict:
        """Get process manager statistics"""
        with self._lock:
            total_processes = len(self.process_history)
            successful = sum(1 for r in self.process_history if r.success)
            failed = sum(1 for r in self.process_history if not r.success)
            active = len(self.active_processes)

            total_duration = sum(r.duration_seconds for r in self.process_history)
            avg_duration = total_duration / total_processes if total_processes > 0 else 0

        return {
            "total_processes": total_processes,
            "successful": successful,
            "failed": failed,
            "active_processes": active,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": avg_duration
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    manager = ProcessManager()

    # Run simple command
    result = manager.run(["echo", "Hello, HyperSync!"])
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.stdout}")

    # Run with timeout
    result = manager.run(["sleep", "2"], timeout=1.0)
    print(f"State: {result.state}")

    # Run with working directory
    result = manager.run(["ls", "-la"], cwd="/tmp")
    print(f"Files in /tmp:\n{result.stdout}")

    # Get statistics
    stats = manager.get_stats()
    print(f"Stats: {stats}")
