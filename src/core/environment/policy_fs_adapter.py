"""
Policy-Enforced Filesystem Adapter
Wraps filesystem operations with policy checks and telemetry.
"""

import logging
from typing import Optional, List
from datetime import datetime
from .fs_adapters import FileSystemAdapter, FileInfo

logger = logging.getLogger(__name__)


class FilesystemOperation:
    """Represents a filesystem operation for telemetry"""

    def __init__(
        self,
        operation: str,
        path: str,
        agent_id: str,
        sandbox_id: str,
        success: bool,
        error: Optional[str] = None,
        bytes_transferred: int = 0,
        duration_ms: float = 0.0
    ):
        self.operation = operation
        self.path = path
        self.agent_id = agent_id
        self.sandbox_id = sandbox_id
        self.success = success
        self.error = error
        self.bytes_transferred = bytes_transferred
        self.duration_ms = duration_ms
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "path": self.path,
            "agent_id": self.agent_id,
            "sandbox_id": self.sandbox_id,
            "success": self.success,
            "error": self.error,
            "bytes_transferred": self.bytes_transferred,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat()
        }


class PolicyEnforcedFileSystemAdapter:
    """Filesystem adapter with policy enforcement and telemetry"""

    def __init__(
        self,
        adapter: FileSystemAdapter,
        sandbox,
        telemetry_callback=None
    ):
        """
        Initialize policy-enforced adapter.

        Args:
            adapter: Underlying filesystem adapter
            sandbox: Sandbox instance for policy checks
            telemetry_callback: Optional callback for telemetry events
        """
        self.adapter = adapter
        self.sandbox = sandbox
        self.telemetry_callback = telemetry_callback
        self.operation_count = 0
        self.bytes_read = 0
        self.bytes_written = 0

    def _check_access(self, path: str, operation: str) -> bool:
        """Check if operation is allowed by policy"""
        if not self.sandbox:
            logger.warning("No sandbox configured, allowing operation")
            return True

        return self.sandbox.check_access(path, operation)

    def _record_operation(self, op: FilesystemOperation):
        """Record operation for telemetry"""
        self.operation_count += 1

        if op.operation in ["read", "read_text", "read_bytes"]:
            self.bytes_read += op.bytes_transferred
        elif op.operation in ["write", "write_text", "write_bytes"]:
            self.bytes_written += op.bytes_transferred

        if self.telemetry_callback:
            try:
                self.telemetry_callback(op)
            except Exception as e:
                logger.error(f"Telemetry callback failed: {e}")

        # Log operation
        if op.success:
            logger.info(f"FS operation: {op.operation} on {op.path} - SUCCESS")
        else:
            logger.warning(f"FS operation: {op.operation} on {op.path} - FAILED: {op.error}")

    def read_text(self, path: str, encoding: Optional[str] = None) -> str:
        """Read text file with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "read"):
            op = FilesystemOperation(
                operation="read_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            content = self.adapter.read_text(path, encoding)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="read_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                bytes_transferred=len(content.encode('utf-8')),
                duration_ms=duration
            )
            self._record_operation(op)
            return content

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="read_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def read_bytes(self, path: str) -> bytes:
        """Read binary file with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "read"):
            op = FilesystemOperation(
                operation="read_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            content = self.adapter.read_bytes(path)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="read_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                bytes_transferred=len(content),
                duration_ms=duration
            )
            self._record_operation(op)
            return content

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="read_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def write_text(self, path: str, content: str, append: bool = False, encoding: Optional[str] = None):
        """Write text file with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "write"):
            op = FilesystemOperation(
                operation="write_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            self.adapter.write_text(path, content, append, encoding)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="write_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                bytes_transferred=len(content.encode('utf-8')),
                duration_ms=duration
            )
            self._record_operation(op)

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="write_text",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def write_bytes(self, path: str, content: bytes, append: bool = False):
        """Write binary file with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "write"):
            op = FilesystemOperation(
                operation="write_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            self.adapter.write_bytes(path, content, append)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="write_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                bytes_transferred=len(content),
                duration_ms=duration
            )
            self._record_operation(op)

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="write_bytes",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def list_dir(self, path: str) -> List[str]:
        """List directory with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "list"):
            op = FilesystemOperation(
                operation="list_dir",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            entries = self.adapter.list_dir(path)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="list_dir",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                duration_ms=duration
            )
            self._record_operation(op)
            return entries

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="list_dir",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def delete(self, path: str, recursive: bool = False):
        """Delete file/directory with policy check"""
        import time
        start = time.time()

        # Check policy
        if not self._check_access(path, "delete"):
            op = FilesystemOperation(
                operation="delete",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error="Access denied by policy"
            )
            self._record_operation(op)
            raise PermissionError(f"Access denied: {path}")

        # Perform operation
        try:
            self.adapter.delete(path, recursive)
            duration = (time.time() - start) * 1000

            op = FilesystemOperation(
                operation="delete",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=True,
                duration_ms=duration
            )
            self._record_operation(op)

        except Exception as e:
            duration = (time.time() - start) * 1000
            op = FilesystemOperation(
                operation="delete",
                path=path,
                agent_id=self.sandbox.agent_id if self.sandbox else "unknown",
                sandbox_id=self.sandbox.sandbox_id if self.sandbox else "unknown",
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self._record_operation(op)
            raise

    def get_stats(self) -> dict:
        """Get adapter statistics"""
        return {
            "operation_count": self.operation_count,
            "bytes_read": self.bytes_read,
            "bytes_written": self.bytes_written,
            "agent_id": self.sandbox.agent_id if self.sandbox else "unknown",
            "sandbox_id": self.sandbox.sandbox_id if self.sandbox else "unknown"
        }

    # Delegate other methods to underlying adapter
    def __getattr__(self, name):
        """Delegate unknown methods to underlying adapter"""
        return getattr(self.adapter, name)


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    from .fs_adapters import FileSystemAdapter

    # Create base adapter
    base_adapter = FileSystemAdapter.for_host()

    # Mock sandbox for testing
    class MockSandbox:
        agent_id = "test-agent"
        sandbox_id = "test-sandbox"

        def check_access(self, path, operation):
            # Allow /tmp, deny /etc
            return path.startswith("/tmp")

    # Create policy-enforced adapter
    sandbox = MockSandbox()
    enforced_adapter = PolicyEnforcedFileSystemAdapter(
        base_adapter,
        sandbox,
        telemetry_callback=lambda op: print(f"Telemetry: {op.to_dict()}")
    )

    # Test operations
    try:
        enforced_adapter.write_text("/tmp/test.txt", "Hello!")
        content = enforced_adapter.read_text("/tmp/test.txt")
        print(f"Content: {content}")

        # This should fail
        enforced_adapter.write_text("/etc/test.txt", "Denied!")
    except PermissionError as e:
        print(f"Expected error: {e}")

    # Print stats
    print(f"Stats: {enforced_adapter.get_stats()}")
