#!/usr/bin/env python3
"""End-to-End Live Verification Script for Background Agent Dispatcher.

Verifies:
1. Live dispatch via `python -m engine.cli --skill prd-generator --input ... --background`
2. Parsing Task ID and PID
3. Polling `python -m engine.cli --status <task_id>` until completed
4. Checking output artifact in `output/` and log file in `data/logs/`
5. Live dispatch via `python scripts/run.py --skill backend-schema ... --provider ollama --background`
6. Polling status and checking output for ollama runner
"""

import json
from pathlib import Path
import re
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)

def main():
    print("=" * 70)
    print("LIVE BACKGROUND AGENT DISPATCHER END-TO-END VERIFICATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Test 1: engine.cli --background
    # ---------------------------------------------------------
    print("\n[*] Step 1: Dispatching task via `engine.cli`...")
    dispatch_cmd = [
        sys.executable,
        "-m",
        "engine.cli",
        "--skill",
        "prd-generator",
        "--input",
        "Decentralized video platform",
        "--background",
    ]
    t0 = time.perf_counter()
    res = run_cmd(dispatch_cmd)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"Dispatch returncode: {res.returncode} (took {elapsed_ms:.1f}ms)")
    print(res.stdout)
    if res.returncode != 0:
        print("Dispatch stderr:", res.stderr)
        sys.exit(1)

    # Strip ANSI escape codes
    clean_stdout = re.sub(r"\x1b\[[0-9;]*m", "", res.stdout)
    task_id_match = re.search(r"Task ID:\s+(task_\S+)", clean_stdout)
    pid_match = re.search(r"Worker PID:\s+(\d+)", clean_stdout)
    assert task_id_match, f"Could not parse Task ID from dispatch output: {res.stdout}"
    task_id = task_id_match.group(1).strip()
    pid = int(pid_match.group(1)) if pid_match else None
    print(f"[+] Successfully captured Task ID: {task_id}, Worker PID: {pid}")

    # Poll status
    print(f"\n[*] Step 2: Polling status for {task_id}...")
    deadline = time.time() + 15.0
    status_output = ""
    is_completed = False
    while time.time() < deadline:
        st_res = run_cmd([sys.executable, "-m", "engine.cli", "--status", task_id])
        status_output = st_res.stdout
        print(f"  [Poll] Status check output:\n{status_output.strip()}\n")
        if "COMPLETED" in status_output:
            is_completed = True
            break
        elif "FAILED" in status_output:
            break
        time.sleep(0.5)

    assert is_completed, f"Task {task_id} did not complete successfully!\n{status_output}"
    print(f"[+] Task {task_id} completed successfully!")

    # Verify log file
    print(f"\n[*] Step 3: Verifying logs for {task_id}...")
    log_file = REPO_ROOT / "data" / "logs" / f"{task_id}.log"
    assert log_file.is_file(), f"Expected log file {log_file} does not exist!"
    log_content = log_file.read_text(encoding="utf-8")
    assert len(log_content) > 0, "Log file is empty!"
    assert "Initializing worker for task" in log_content
    assert "marked COMPLETED" in log_content
    print(f"[+] Verified log file: {log_file} ({len(log_content)} bytes)")

    # Verify CLI logs command
    logs_res = run_cmd([sys.executable, "-m", "engine.cli", "--logs", task_id])
    assert "marked COMPLETED" in logs_res.stdout, "CLI --logs did not return expected logs"
    print("[+] Verified `engine.cli --logs` output.")

    # Verify output artifact
    print(f"\n[*] Step 4: Verifying output artifact...")
    output_files = list((REPO_ROOT / "output").glob(f"prd-generator_{task_id}*.md"))
    assert len(output_files) > 0, f"Expected output artifact for task {task_id} not found in output/"
    artifact = output_files[0]
    artifact_content = artifact.read_text(encoding="utf-8")
    assert len(artifact_content) > 100, "Artifact content is too short"
    print(f"[+] Verified artifact: {artifact} ({len(artifact_content)} bytes)")

    # ---------------------------------------------------------
    # Test 2: scripts/run.py --provider ollama --background
    # ---------------------------------------------------------
    print("\n[*] Step 5: Dispatching Ollama runner task via `scripts/run.py`...")
    ollama_cmd = [
        sys.executable,
        "scripts/run.py",
        "--skill",
        "backend-schema",
        "--input",
        "SaaS Auth Schema",
        "--provider",
        "ollama",
        "--background",
    ]
    t0 = time.perf_counter()
    res_ollama = run_cmd(ollama_cmd)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"Ollama dispatch returncode: {res_ollama.returncode} (took {elapsed_ms:.1f}ms)")
    print(res_ollama.stdout)
    if res_ollama.returncode != 0:
        print("Ollama dispatch stderr:", res_ollama.stderr)
        sys.exit(1)

    clean_stdout2 = re.sub(r"\x1b\[[0-9;]*m", "", res_ollama.stdout)
    task_id_match2 = re.search(r"Task ID:\s+(task_\S+)", clean_stdout2)
    assert task_id_match2, f"Could not parse Task ID from ollama dispatch output: {res_ollama.stdout}"
    task_id2 = task_id_match2.group(1).strip()
    print(f"[+] Successfully captured Ollama Task ID: {task_id2}")

    # Poll status via scripts/run.py --status
    print(f"\n[*] Step 6: Polling status for Ollama task {task_id2} via `scripts/run.py`...")
    deadline = time.time() + 15.0
    is_completed2 = False
    while time.time() < deadline:
        st_res = run_cmd([sys.executable, "scripts/run.py", "--status", task_id2])
        status_output2 = st_res.stdout
        print(f"  [Poll] Ollama status check:\n{status_output2.strip()}\n")
        if "COMPLETED" in status_output2:
            is_completed2 = True
            break
        elif "FAILED" in status_output2:
            break
        time.sleep(0.5)

    assert is_completed2, f"Ollama task {task_id2} did not complete successfully!\n{status_output2}"
    print(f"[+] Ollama task {task_id2} completed successfully!")

    # Verify Ollama log and artifact
    log_file2 = REPO_ROOT / "data" / "logs" / f"{task_id2}.log"
    assert log_file2.is_file(), f"Log file {log_file2} does not exist"
    print(f"[+] Verified Ollama log file: {log_file2} ({log_file2.stat().st_size} bytes)")

    output_files2 = list((REPO_ROOT / "output").glob(f"backend-schema_{task_id2}*.md"))
    assert len(output_files2) > 0, f"Expected output artifact for task {task_id2} not found"
    print(f"[+] Verified Ollama artifact: {output_files2[0]} ({output_files2[0].stat().st_size} bytes)")

    print("\n" + "=" * 70)
    print("🎉 ALL END-TO-END LIVE BACKGROUND DISPATCH VERIFICATIONS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
