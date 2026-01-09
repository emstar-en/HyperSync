"""
OS-Agnostic Filesystem Adapters
Provides direct read/write helpers with path normalization and encoding support.
"""

import os
import sys
import shutil
import logging
from typing import Optional, List, Dict, BinaryIO, Union
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FileSystemType(Enum):
    """Supported filesystem types"""
    POSIX = "posix"
    WINDOWS = "windows"
    CONTAINER = "container"
    NETWORK = "network"


@dataclass
class FileInfo:
    """File metadata information"""
    path: str
    name: str
    size: int
    is_dir: bool
    is_file: bool
    is_symlink: bool
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    accessed_at: Optional[datetime]
    permissions: Optional[str]
    owner: Optional[str]
    group: Optional[str]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "size": self.size,
            "is_dir": self.is_dir,
            "is_file": self.is_file,
            "is_symlink": self.is_symlink,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group
        }


class FileSystemAdapter(ABC):
    """Abstract base class for filesystem adapters"""

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding
        self.fs_type: FileSystemType = FileSystemType.POSIX

    @abstractmethod
    def normalize_path(self, path: str) -> str:
        """Normalize path for the target OS"""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        pass

    @abstractmethod
    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        pass

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        pass

    @abstractmethod
    def read_text(self, path: str, encoding: Optional[str] = None) -> str:
        """Read text file"""
        pass

    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        """Read binary file"""
        pass

    @abstractmethod
    def write_text(self, path: str, content: str, append: bool = False, encoding: Optional[str] = None):
        """Write text file"""
        pass

    @abstractmethod
    def write_bytes(self, path: str, content: bytes, append: bool = False):
        """Write binary file"""
        pass

    @abstractmethod
    def list_dir(self, path: str) -> List[str]:
        """List directory contents"""
        pass

    @abstractmethod
    def get_info(self, path: str) -> FileInfo:
        """Get file/directory information"""
        pass

    @abstractmethod
    def create_dir(self, path: str, parents: bool = True, exist_ok: bool = True):
        """Create directory"""
        pass

    @abstractmethod
    def delete(self, path: str, recursive: bool = False):
        """Delete file or directory"""
        pass

    @abstractmethod
    def copy(self, src: str, dst: str, overwrite: bool = False):
        """Copy file or directory"""
        pass

    @abstractmethod
    def move(self, src: str, dst: str):
        """Move file or directory"""
        pass

    @classmethod
    def for_host(cls, encoding: str = "utf-8") -> 'FileSystemAdapter':
        """Factory method to create adapter for host OS"""
        if sys.platform.startswith('win'):
            return WindowsFileSystemAdapter(encoding)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            return PosixFileSystemAdapter(encoding)
        else:
            logger.warning(f"Unknown platform {sys.platform}, using POSIX adapter")
            return PosixFileSystemAdapter(encoding)


class PosixFileSystemAdapter(FileSystemAdapter):
    """Filesystem adapter for POSIX systems (Linux, macOS, Unix)"""

    def __init__(self, encoding: str = "utf-8"):
        super().__init__(encoding)
        self.fs_type = FileSystemType.POSIX

    def normalize_path(self, path: str) -> str:
        """Normalize path for POSIX"""
        # Convert to Path object and resolve
        p = Path(path).expanduser()
        # Convert backslashes to forward slashes
        normalized = str(p).replace('\\', '/')
        return normalized

    def exists(self, path: str) -> bool:
        """Check if path exists"""
        normalized = self.normalize_path(path)
        return os.path.exists(normalized)

    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        normalized = self.normalize_path(path)
        return os.path.isfile(normalized)

    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        normalized = self.normalize_path(path)
        return os.path.isdir(normalized)

    def read_text(self, path: str, encoding: Optional[str] = None) -> str:
        """Read text file"""
        normalized = self.normalize_path(path)
        enc = encoding or self.encoding

        try:
            with open(normalized, 'r', encoding=enc) as f:
                content = f.read()
            logger.debug(f"Read {len(content)} chars from {normalized}")
            return content
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {normalized}: {e}")
            # Try with error handling
            with open(normalized, 'r', encoding=enc, errors='replace') as f:
                return f.read()

    def read_bytes(self, path: str) -> bytes:
        """Read binary file"""
        normalized = self.normalize_path(path)

        with open(normalized, 'rb') as f:
            content = f.read()
        logger.debug(f"Read {len(content)} bytes from {normalized}")
        return content

    def write_text(self, path: str, content: str, append: bool = False, encoding: Optional[str] = None):
        """Write text file"""
        normalized = self.normalize_path(path)
        enc = encoding or self.encoding
        mode = 'a' if append else 'w'

        # Ensure parent directory exists
        parent = os.path.dirname(normalized)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(normalized, mode, encoding=enc) as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} chars to {normalized} (append={append})")

    def write_bytes(self, path: str, content: bytes, append: bool = False):
        """Write binary file"""
        normalized = self.normalize_path(path)
        mode = 'ab' if append else 'wb'

        # Ensure parent directory exists
        parent = os.path.dirname(normalized)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(normalized, mode) as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} bytes to {normalized} (append={append})")

    def list_dir(self, path: str) -> List[str]:
        """List directory contents"""
        normalized = self.normalize_path(path)

        if not self.is_dir(normalized):
            raise NotADirectoryError(f"{normalized} is not a directory")

        entries = os.listdir(normalized)
        logger.debug(f"Listed {len(entries)} entries in {normalized}")
        return sorted(entries)

    def get_info(self, path: str) -> FileInfo:
        """Get file/directory information"""
        normalized = self.normalize_path(path)

        if not self.exists(normalized):
            raise FileNotFoundError(f"{normalized} does not exist")

        stat = os.stat(normalized)
        p = Path(normalized)

        # Get timestamps
        created_at = datetime.fromtimestamp(stat.st_ctime)
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        accessed_at = datetime.fromtimestamp(stat.st_atime)

        # Get permissions (POSIX format)
        import stat as stat_module
        perms = stat_module.filemode(stat.st_mode)

        # Get owner/group (POSIX only)
        try:
            import pwd
            import grp
            owner = pwd.getpwuid(stat.st_uid).pw_name
            group = grp.getgrgid(stat.st_gid).gr_name
        except (ImportError, KeyError):
            owner = str(stat.st_uid)
            group = str(stat.st_gid)

        return FileInfo(
            path=normalized,
            name=p.name,
            size=stat.st_size,
            is_dir=p.is_dir(),
            is_file=p.is_file(),
            is_symlink=p.is_symlink(),
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            permissions=perms,
            owner=owner,
            group=group
        )

    def create_dir(self, path: str, parents: bool = True, exist_ok: bool = True):
        """Create directory"""
        normalized = self.normalize_path(path)

        if parents:
            os.makedirs(normalized, exist_ok=exist_ok)
        else:
            os.mkdir(normalized)

        logger.info(f"Created directory {normalized}")

    def delete(self, path: str, recursive: bool = False):
        """Delete file or directory"""
        normalized = self.normalize_path(path)

        if not self.exists(normalized):
            raise FileNotFoundError(f"{normalized} does not exist")

        if self.is_dir(normalized):
            if recursive:
                shutil.rmtree(normalized)
                logger.info(f"Recursively deleted directory {normalized}")
            else:
                os.rmdir(normalized)
                logger.info(f"Deleted empty directory {normalized}")
        else:
            os.remove(normalized)
            logger.info(f"Deleted file {normalized}")

    def copy(self, src: str, dst: str, overwrite: bool = False):
        """Copy file or directory"""
        src_norm = self.normalize_path(src)
        dst_norm = self.normalize_path(dst)

        if not self.exists(src_norm):
            raise FileNotFoundError(f"{src_norm} does not exist")

        if self.exists(dst_norm) and not overwrite:
            raise FileExistsError(f"{dst_norm} already exists")

        if self.is_dir(src_norm):
            if self.exists(dst_norm):
                shutil.rmtree(dst_norm)
            shutil.copytree(src_norm, dst_norm)
            logger.info(f"Copied directory {src_norm} to {dst_norm}")
        else:
            shutil.copy2(src_norm, dst_norm)
            logger.info(f"Copied file {src_norm} to {dst_norm}")

    def move(self, src: str, dst: str):
        """Move file or directory"""
        src_norm = self.normalize_path(src)
        dst_norm = self.normalize_path(dst)

        if not self.exists(src_norm):
            raise FileNotFoundError(f"{src_norm} does not exist")

        shutil.move(src_norm, dst_norm)
        logger.info(f"Moved {src_norm} to {dst_norm}")


class WindowsFileSystemAdapter(FileSystemAdapter):
    """Filesystem adapter for Windows"""

    def __init__(self, encoding: str = "utf-8"):
        super().__init__(encoding)
        self.fs_type = FileSystemType.WINDOWS

    def normalize_path(self, path: str) -> str:
        """Normalize path for Windows"""
        # Convert to Path object and resolve
        p = Path(path).expanduser()
        # Use Windows path separators
        normalized = str(p).replace('/', '\\')
        return normalized

    def exists(self, path: str) -> bool:
        """Check if path exists"""
        normalized = self.normalize_path(path)
        return os.path.exists(normalized)

    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        normalized = self.normalize_path(path)
        return os.path.isfile(normalized)

    def is_dir(self, path: str) -> bool:
        """Check if path is a directory"""
        normalized = self.normalize_path(path)
        return os.path.isdir(normalized)

    def read_text(self, path: str, encoding: Optional[str] = None) -> str:
        """Read text file"""
        normalized = self.normalize_path(path)
        enc = encoding or self.encoding

        try:
            with open(normalized, 'r', encoding=enc) as f:
                content = f.read()
            logger.debug(f"Read {len(content)} chars from {normalized}")
            return content
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {normalized}: {e}")
            # Try with error handling
            with open(normalized, 'r', encoding=enc, errors='replace') as f:
                return f.read()

    def read_bytes(self, path: str) -> bytes:
        """Read binary file"""
        normalized = self.normalize_path(path)

        with open(normalized, 'rb') as f:
            content = f.read()
        logger.debug(f"Read {len(content)} bytes from {normalized}")
        return content

    def write_text(self, path: str, content: str, append: bool = False, encoding: Optional[str] = None):
        """Write text file"""
        normalized = self.normalize_path(path)
        enc = encoding or self.encoding
        mode = 'a' if append else 'w'

        # Ensure parent directory exists
        parent = os.path.dirname(normalized)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(normalized, mode, encoding=enc) as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} chars to {normalized} (append={append})")

    def write_bytes(self, path: str, content: bytes, append: bool = False):
        """Write binary file"""
        normalized = self.normalize_path(path)
        mode = 'ab' if append else 'wb'

        # Ensure parent directory exists
        parent = os.path.dirname(normalized)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(normalized, mode) as f:
            f.write(content)

        logger.info(f"Wrote {len(content)} bytes to {normalized} (append={append})")

    def list_dir(self, path: str) -> List[str]:
        """List directory contents"""
        normalized = self.normalize_path(path)

        if not self.is_dir(normalized):
            raise NotADirectoryError(f"{normalized} is not a directory")

        entries = os.listdir(normalized)
        logger.debug(f"Listed {len(entries)} entries in {normalized}")
        return sorted(entries)

    def get_info(self, path: str) -> FileInfo:
        """Get file/directory information"""
        normalized = self.normalize_path(path)

        if not self.exists(normalized):
            raise FileNotFoundError(f"{normalized} does not exist")

        stat = os.stat(normalized)
        p = Path(normalized)

        # Get timestamps
        created_at = datetime.fromtimestamp(stat.st_ctime)
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        accessed_at = datetime.fromtimestamp(stat.st_atime)

        # Windows doesn't have POSIX permissions
        perms = "N/A (Windows)"
        owner = "N/A (Windows)"
        group = "N/A (Windows)"

        return FileInfo(
            path=normalized,
            name=p.name,
            size=stat.st_size,
            is_dir=p.is_dir(),
            is_file=p.is_file(),
            is_symlink=p.is_symlink(),
            created_at=created_at,
            modified_at=modified_at,
            accessed_at=accessed_at,
            permissions=perms,
            owner=owner,
            group=group
        )

    def create_dir(self, path: str, parents: bool = True, exist_ok: bool = True):
        """Create directory"""
        normalized = self.normalize_path(path)

        if parents:
            os.makedirs(normalized, exist_ok=exist_ok)
        else:
            os.mkdir(normalized)

        logger.info(f"Created directory {normalized}")

    def delete(self, path: str, recursive: bool = False):
        """Delete file or directory"""
        normalized = self.normalize_path(path)

        if not self.exists(normalized):
            raise FileNotFoundError(f"{normalized} does not exist")

        if self.is_dir(normalized):
            if recursive:
                shutil.rmtree(normalized)
                logger.info(f"Recursively deleted directory {normalized}")
            else:
                os.rmdir(normalized)
                logger.info(f"Deleted empty directory {normalized}")
        else:
            os.remove(normalized)
            logger.info(f"Deleted file {normalized}")

    def copy(self, src: str, dst: str, overwrite: bool = False):
        """Copy file or directory"""
        src_norm = self.normalize_path(src)
        dst_norm = self.normalize_path(dst)

        if not self.exists(src_norm):
            raise FileNotFoundError(f"{src_norm} does not exist")

        if self.exists(dst_norm) and not overwrite:
            raise FileExistsError(f"{dst_norm} already exists")

        if self.is_dir(src_norm):
            if self.exists(dst_norm):
                shutil.rmtree(dst_norm)
            shutil.copytree(src_norm, dst_norm)
            logger.info(f"Copied directory {src_norm} to {dst_norm}")
        else:
            shutil.copy2(src_norm, dst_norm)
            logger.info(f"Copied file {src_norm} to {dst_norm}")

    def move(self, src: str, dst: str):
        """Move file or directory"""
        src_norm = self.normalize_path(src)
        dst_norm = self.normalize_path(dst)

        if not self.exists(src_norm):
            raise FileNotFoundError(f"{src_norm} does not exist")

        shutil.move(src_norm, dst_norm)
        logger.info(f"Moved {src_norm} to {dst_norm}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create adapter for host OS
    fs = FileSystemAdapter.for_host()
    print(f"Using {fs.fs_type.value} adapter")

    # Example operations
    test_file = "/tmp/hypersync_test.txt"

    # Write text
    fs.write_text(test_file, "Hello from HyperSync!\n")

    # Append text
    fs.write_text(test_file, "This is appended.\n", append=True)

    # Read text
    content = fs.read_text(test_file)
    print(f"Content: {content}")

    # Get file info
    info = fs.get_info(test_file)
    print(f"File info: {info.to_dict()}")

    # Clean up
    fs.delete(test_file)
