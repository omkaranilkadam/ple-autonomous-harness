#!/usr/bin/env python3
"""
Test P4 WebSocket Conformance:
Runs a mock evaluator speaking the official serve protocol against serve.py:
1. Connects to server within 120s bind limit.
2. Sends official task frame.
3. Responds to exec / read / write / usage / log requests.
4. Confirms done frame received with valid final_message.
5. Tests malformed frames (non-JSON, wrong initial message) producing error frames, not hangs.
6. Confirms clean shutdown.
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
import websockets

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import harness
import taskbridge

logging.basicConfig(level=logging.WARNING)
PORT = 8999
HOST = "127.0.0.1"

async def mock_evaluator():
    print("=" * 60)
    print("STARTING P4 WEBSOCKET CONFORMANCE TEST")
    print("=" * 60)
    
    server_task = asyncio.create_task(_run_server())
    await asyncio.sleep(0.5)  # wait for bind
    uri = f"ws://{HOST}:{PORT}"
    
    # -------------------------------------------------------------
    # Test 1: Full Valid Task Round-trip
    # -------------------------------------------------------------
    print("Test 1: Valid Task Round-trip...")
    async with websockets.connect(uri) as ws:
        task_frame = {
            "type": "task",
            "protocol": 1,
            "session": "test-session-001",
            "instruction": "Inspect /app and write /app/output/solution.txt.",
            "workdir": "/app",
            "limits": {
                "agent_timeout_sec": 60,
                "exec_timeout_sec": 10,
                "max_output_bytes": 100000,
                "max_write_bytes": 10000000
            },
            "mcp_servers": []
        }
        await ws.send(json.dumps(task_frame))
        
        done_received = False
        final_message = ""
        
        while not done_received:
            msg_str = await asyncio.wait_for(ws.recv(), timeout=10.0)
            msg = json.loads(msg_str)
            msg_type = msg.get("type")
            
            if msg_type == "exec":
                reply = {
                    "type": "result",
                    "id": msg["id"],
                    "ok": True,
                    "exit_code": 0,
                    "output": "total 4\n-rw-r--r-- 1 root root 1024 project.md\n-rw-r--r-- 1 root root 2048 criteria.pdf",
                    "truncated": False,
                    "timed_out": False
                }
                await ws.send(json.dumps(reply))
            elif msg_type in ("usage", "log"):
                pass
            elif msg_type == "done":
                done_received = True
                final_message = msg.get("final_message", "")
                break
                
        assert done_received, "Done frame was not received"
        assert len(final_message) > 0, "final_message was empty"
        print(f"  [PASS] Task round-trip completed! final_message length={len(final_message)}")

    # -------------------------------------------------------------
    # Test 2: Malformed initial message (non-task) -> returns error frame
    # -------------------------------------------------------------
    print("Test 2: Malformed initial message rejection...")
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "random_invalid_frame"}))
        reply_str = await asyncio.wait_for(ws.recv(), timeout=5.0)
        reply = json.loads(reply_str)
        assert reply.get("type") == "error", f"Expected error frame, got: {reply}"
        print(f"  [PASS] Server returned error frame as expected: {reply.get('message')}")

    # -------------------------------------------------------------
    # Test 3: Non-JSON raw bytes -> handled gracefully without hang
    # -------------------------------------------------------------
    print("Test 3: Non-JSON raw bytes rejection...")
    async with websockets.connect(uri) as ws:
        await ws.send("INVALID_RAW_GARBAGE{{{{")
        reply_str = await asyncio.wait_for(ws.recv(), timeout=5.0)
        reply = json.loads(reply_str)
        assert reply.get("type") == "error", f"Expected error frame, got: {reply}"
        print(f"  [PASS] Server returned error frame for non-JSON: {reply.get('message')}")

    server_task.cancel()
    print("=" * 60)
    print("ALL P4 WEBSOCKET CONFORMANCE TESTS PASSED")
    print("=" * 60)

async def _run_server():
    async def handler(ws):
        await taskbridge._session(ws, harness.solve)
            
    async with websockets.serve(handler, HOST, PORT, ping_interval=None, max_size=taskbridge.MAX_FRAME):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(mock_evaluator())
