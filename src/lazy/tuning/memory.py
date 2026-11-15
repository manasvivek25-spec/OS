"""Memory locking (mlock/mlockall) and page pre-faulting for Lazy OS."""
from __future__ import annotations

import ctypes
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("lazy.tuning.memory")

# mlockall flags (sys/mman.h)
MCL_CURRENT = 1
MCL_FUTURE = 2
MCL_ONFAULT = 4


def _get_libc():
    try:
        return ctypes.CDLL(None, use_errno=True)
    except Exception:
        try:
            return ctypes.CDLL("libc.so.6", use_errno=True)
        except Exception:
            return None


def lock_memory(current: bool = True, future: bool = True) -> bool:
    """Lock caller's virtual address space into RAM using mlockall.
    
    Prevents swapping out memory pages under memory pressure,
    eliminating major page fault latency on interactive LLM and audio inference.
    """
    libc = _get_libc()
    if not libc or not hasattr(libc, "mlockall"):
        logger.warning("libc mlockall not available on this platform")
        return False

    flags = 0
    if current:
        flags |= MCL_CURRENT
    if future:
        flags |= MCL_FUTURE

    try:
        res = libc.mlockall(ctypes.c_int(flags))
        if res == 0:
            logger.debug("Successfully locked process memory with mlockall(0x%x)", flags)
            return True
        else:
            errno = ctypes.get_errno()
            # If ENOMEM (errno 12) due to ulimit -l on unprivileged shell, try MCL_CURRENT alone
            if errno == 12 and (flags & MCL_FUTURE):
                res2 = libc.mlockall(ctypes.c_int(MCL_CURRENT))
                if res2 == 0:
                    logger.debug("Locked current process pages with MCL_CURRENT (MCL_FUTURE omitted due to ulimit)")
                    return True
            logger.debug("mlockall failed with code %d, errno %d", res, errno)
            return False
    except Exception as e:
        logger.debug("Exception during mlockall: %s", e)
        return False


def lock_range(buf: bytes | bytearray | memoryview) -> bool:
    """Lock a specific buffer in physical RAM using mlock()."""
    libc = _get_libc()
    if not libc or not hasattr(libc, "mlock"):
        return False
    try:
        length = len(buf)
        if length == 0:
            return True
        char_arr = (ctypes.c_char * length).from_buffer(buf)
        addr = ctypes.addressof(char_arr)
        res = libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(length))
        return res == 0
    except Exception as e:
        logger.debug("Exception during mlock: %s", e)
        return False


def unlock_range(buf: bytes | bytearray | memoryview) -> bool:
    """Unlock a specific buffer in physical RAM using munlock()."""
    libc = _get_libc()
    if not libc or not hasattr(libc, "munlock"):
        return False
    try:
        length = len(buf)
        if length == 0:
            return True
        char_arr = (ctypes.c_char * length).from_buffer(buf)
        addr = ctypes.addressof(char_arr)
        res = libc.munlock(ctypes.c_void_p(addr), ctypes.c_size_t(length))
        return res == 0
    except Exception as e:
        logger.debug("Exception during munlock: %s", e)
        return False


def unlock_memory() -> bool:
    """Unlock caller's memory using munlockall."""
    libc = _get_libc()
    if not libc or not hasattr(libc, "munlockall"):
        return False
    try:
        res = libc.munlockall()
        return res == 0
    except Exception as e:
        logger.debug("Exception during munlockall: %s", e)
        return False


def preload_and_fault(buf: bytes | bytearray | memoryview, page_size: int = 4096) -> int:
    """Touch every virtual memory page in buffer to pre-fault pages into physical RAM.
    
    Returns total number of pages touched.
    """
    if not buf:
        return 0
    total_len = len(buf)
    pages = 0
    # Read one byte from each page to trigger minor fault
    for offset in range(0, total_len, page_size):
        _ = buf[offset]
        pages += 1
    # Touch last byte
    if total_len > 0:
        _ = buf[total_len - 1]
    return pages


def get_locked_memory_kb() -> int:
    """Read VmLck (locked memory size in kB) from /proc/self/status."""
    status_path = Path("/proc/self/status")
    if not status_path.is_file():
        return 0
    try:
        with open(status_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmLck:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return int(parts[1])
    except Exception:
        pass
    return 0


def is_memory_locked() -> bool:
    """Return True if at least one page is currently locked in RAM."""
    return get_locked_memory_kb() > 0
