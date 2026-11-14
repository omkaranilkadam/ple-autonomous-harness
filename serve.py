#!/usr/bin/env python3
"""
serve.py - PLE-2026 Agent Server
Serves `harness.solve` over the official WebSocket serve protocol on $PORT.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness
import taskbridge

if __name__ == "__main__":
    taskbridge.run(harness.solve)
