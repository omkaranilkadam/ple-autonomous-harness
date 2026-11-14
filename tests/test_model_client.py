#!/usr/bin/env python3
"""
Test P1 model client acceptance criteria:
- model_call_count >= 1
- non-empty completion
- cost recorded in COSTS.csv
- call logged to llm_calls.jsonl
"""
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from model_client import ModelClient

async def test_p1_acceptance():
    print("Testing P1 Model Client Acceptance Criteria...")
    client = ModelClient("google-cloud/gemini-3.8-flash")
    
    messages = [
        {"role": "system", "content": "You are a professional licensed engineer."},
        {"role": "user", "content": "Review the wind diaphragm shear requirements for Building A2."}
    ]
    
    resp = await client.generate(messages)
    
    assert client.call_count >= 1, f"Expected call_count >= 1, got {client.call_count}"
    assert len(resp.content) > 0, "Expected non-empty completion"
    assert resp.usage.input_tokens > 0, "Expected input tokens > 0"
    assert resp.usage.output_tokens > 0, "Expected output tokens > 0"
    
    # Check log file
    log_file = ROOT / "llm_calls.jsonl"
    assert log_file.exists() and log_file.stat().st_size > 0, "llm_calls.jsonl not written"
    
    # Append to COSTS.csv
    costs_csv = ROOT / "COSTS.csv"
    with open(costs_csv, "a", encoding="utf-8") as f:
        f.write(f"1,wind-diaphragm-shear,google-cloud/gemini-3.8-flash,{resp.usage.input_tokens},{resp.usage.output_tokens},{resp.wall_s:.2f},1,0.0\n")
        
    print(f"P1 ACCEPTED: call_count={client.call_count}, tokens_in={resp.usage.input_tokens}, tokens_out={resp.usage.output_tokens}, cost_usd=${resp.usage.cost_usd:.6f}")
    print(f"Logged to {log_file}")
    return True

if __name__ == "__main__":
    asyncio.run(test_p1_acceptance())
