"""
resource_guard.py - Container Memory and Timeout Watchdogs for Stage 2

Stage 2 container constraints:
- 2 CPUs
- 4 GB RAM total (soft limit 3.2 GB)
- 6-hour task timeout (agent_timeout_sec)
- 1 GB /tmp scratch space
"""
from __future__ import annotations

import asyncio
import gc
import logging
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("ple-resource-guard")

SOFT_MEMORY_LIMIT_BYTES = int(3.2 * 1024 * 1024 * 1024)  # 3.2 GiB
WRAP_UP_SEC = 240  # 4 minutes before task deadline

class MemoryLimitExceeded(Exception):
    """Raised when memory watchdog exceeds soft threshold (3.2 GiB)."""
    pass

class TaskTimeoutApproaching(Exception):
    """Raised when deadline is near and task must wrap up."""
    pass

class ResourceGuard:
    """Monitors memory usage and wall-clock deadline."""

    def __init__(self, time_limit_sec: Optional[float] = 21600.0, soft_mem_limit: int = SOFT_MEMORY_LIMIT_BYTES):
        self.start_time = time.monotonic()
        self.time_limit_sec = time_limit_sec
        self.soft_mem_limit = soft_mem_limit
        self.scratch_dir = Path(tempfile.mkdtemp(prefix="ple_scratch_"))

    def get_memory_usage_bytes(self) -> int:
        """Returns current process RSS memory in bytes."""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except Exception:
            # Fallback for Linux /proc/self/statm or mock
            try:
                with open("/proc/self/statm") as f:
                    pages = int(f.read().split()[1])
                    return pages * os.sysconf("SC_PAGE_SIZE")
            except Exception:
                return 0

    def check_memory(self, requested_bytes: int = 0) -> bool:
        """Soft-check memory threshold."""
        current = self.get_memory_usage_bytes()
        if (current + requested_bytes) > self.soft_mem_limit:
            gc.collect()
            current = self.get_memory_usage_bytes()
            if (current + requested_bytes) > self.soft_mem_limit:
                logger.warning(f"Memory threshold breached: {current / (1024*1024):.1f} MiB used")
                raise MemoryLimitExceeded(f"Memory threshold 3.2 GB exceeded: {current} bytes")
        return True

    def time_left_sec(self) -> float:
        if self.time_limit_sec is None:
            return 999999.0
        elapsed = time.monotonic() - self.start_time
        return max(0.0, self.time_limit_sec - elapsed)

    def check_time(self) -> bool:
        """Throws if time left is below wrap-up margin."""
        remaining = self.time_left_sec()
        if remaining <= WRAP_UP_SEC:
            logger.warning(f"Task deadline approaching: only {remaining:.1f}s left (wrap-up margin={WRAP_UP_SEC}s)")
            raise TaskTimeoutApproaching(f"Task deadline approaching: {remaining:.1f}s remaining")
        return True

    def cleanup_scratch(self):
        """Clean up scratch files."""
        if self.scratch_dir.exists():
            shutil.rmtree(self.scratch_dir, ignore_errors=True)
            logger.info("Scratch directory cleaned up")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_scratch()
