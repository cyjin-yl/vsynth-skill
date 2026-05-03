"""
Abstract base class for all vocal synthesis file format parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseParser(ABC):
    """Abstract base class for all format parsers."""

    SUPPORTED_EXTENSIONS: List[str] = []
    FORMAT_NAME: str = "Unknown"
    FORMAT_VERSION: str = ""

    @abstractmethod
    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """
        Validate a file's format.

        Args:
            file_path: Path to the file to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
            If is_valid is True, error_messages should be empty.
        """
        pass

    @abstractmethod
    def info(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract information from a file.

        Args:
            file_path: Path to the file to parse.

        Returns:
            Dictionary containing extracted file information.
        """
        pass

    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file extension matches supported extensions.
        """
        if not file_path.is_file():
            return False
        return file_path.suffix.lower() in [ext.lower() for ext in self.SUPPORTED_EXTENSIONS]

    def validate_or_raise(self, file_path: Path) -> None:
        """
        Validate a file and raise an exception if invalid.

        Args:
            file_path: Path to the file to validate.

        Raises:
            ValueError: If the file is invalid.
        """
        is_valid, errors = self.validate(file_path)
        if not is_valid:
            raise ValueError(f"File validation failed: {'; '.join(errors)}")

    def _read_file(self, file_path: Path, encoding: Optional[str] = None) -> str:
        """
        Read file content as text.

        Args:
            file_path: Path to the file.
            encoding: Optional encoding to use. If None, auto-detect.

        Returns:
            File content as string.

        Raises:
            ValueError: If file cannot be read.
        """
        try:
            if encoding:
                return file_path.read_text(encoding=encoding)
            # Try UTF-8 first, then fallback
            try:
                return file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return file_path.read_text(encoding="shift_jis")
        except Exception as e:
            raise ValueError(f"Cannot read file {file_path}: {e}")

    def _read_bytes(self, file_path: Path) -> bytes:
        """
        Read file content as bytes.

        Args:
            file_path: Path to the file.

        Returns:
            File content as bytes.

        Raises:
            ValueError: If file cannot be read.
        """
        try:
            return file_path.read_bytes()
        except Exception as e:
            raise ValueError(f"Cannot read file {file_path}: {e}")
