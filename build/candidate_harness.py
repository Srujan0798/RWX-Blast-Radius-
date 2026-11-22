#!/usr/bin/env python3
"""One-command candidate harness: unit tests, clean amd64 build, constrained sample, hashes, ledger fields."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "evaluation" / "sample"
ANSWERS = SAMPLE / "answers.json"
TESTS_JSON = SAMPLE / "tests.json"
DEFAULT_SEEDS = (1, 31337, 90210)
RUN_FLAGS = [
    "--rm",
    "--platform",
    "linux/amd64",
    "--network",
    "none",
    "--cpus",
    "2",
    "--memory",
    "4096m",
    "--memory-swap",
    "4096m",
    "--pids-limit",
    "256",
    "--read-only",
    "--tmpfs",
    "/tmp:rw,size=64m,mode=1777",
    "--cap-drop",
    "ALL",
    "--security-opt",
    "no-new-privileges",
    "--user",
    "65534:65534",
    "--env",
    "HOME=/tmp",
    "--volume",
    f"{SAMPLE / 'commits'}:/data/commits:ro",
    "--volume",
    f"{TESTS_JSON}:/data/tests.json:ro",
]
PROBE = (
    "import sys, resource; "
    "from src.main import main; "
    "rc = main(); "
    "r = resource.getrusage(resource.RUSAGE_SELF); "
    "sys.stderr.write('HARNESS_CPU_US=%d\\nHARNESS_MAXRSS_KB=%d\\n' "
    "% (int((r.ru_utime + r.ru_stime) * 1000000), int(r.ru_maxrss))); "
    "sys.stderr.flush(); "
    "sys.exit(rc)"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_command(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=ROOT, **kwargs)


def parse_unittest_summary(text: str) -> dict[str, Any]:
    match = re.search(r"Ran (\d+) tests? in ", text)
    count = int(match.group(1)) if match else None
    ok = bool(re.search(r"^OK( \(.*\))?$", text, re.MULTILINE))
    failed = bool(re.search(r"^FAILED( \(.*\))?$", text, re.MULTILINE))
    return {"tests_run": count, "ok": ok, "failed": failed}


def parse_score_report(text: str) -> dict[str, Any]:
    simulated = re.search(r"Simulated:\s+([\d.]+) s", text)
    misses = re.search(r"Misses:\s+(\d+)", text)
    total = re.search(r"Total:\s+([\d.]+) s", text)
    rejected = re.search(r"Rejected:\s+(\w+)", text)
    return {
        "rejected": rejected.group(1) if rejected else None,
        "simulated_seconds": float(simulated.group(1)) if simulated else None,
        "misses": int(misses.group(1)) if misses else None,
        "total_seconds": float(total.group(1)) if total else None,
    }


def parse_probe(text: str) -> dict[str, Any]:
    cpu = re.search(r"HARNESS_CPU_US=(\d+)", text)
    rss = re.search(r"HARNESS_MAXRSS_KB=(\d+)", text)
    return {
        "cpu_seconds": int(cpu.group(1)) / 1_000_000 if cpu else None,
        "peak_memory_mb": int(rss.group(1)) / 1024 if rss else None,
    }


def duration_ms(seconds: float) -> int:
    return math.floor(seconds * 1000 + 0.5)


def compute_base_and_count(output: bytes, tests: list[dict]) -> tuple[int, int]:
    durations = {t["number"]: duration_ms(t["seconds"]) for t in tests}
    base_ms = 0
    selected_count = 0
    for line in output.decode("utf-8").splitlines():
        if not line.strip():
            continue
        workers = json.loads(line)["workers"]
        occupied = [w for w in workers if w]
        if occupied:
            largest = max(sum(durations[t] for t in w) for w in occupied)
            base_ms += largest + 2000 * len(occupied)
        selected_count += sum(len(w) for w in occupied)
    return base_ms, selected_count


def unit_tests() -> dict[str, Any]:
    started = time.monotonic()
    proc = run_command(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        capture_output=True,
        text=True,
    )
    summary = parse_unittest_summary(proc.stdout + proc.stderr)
    summary["returncode"] = proc.returncode
    summary["wall_seconds"] = round(time.monotonic() - started, 3)
    summary["passed"] = proc.returncode == 0 and summary["ok"] and not summary["failed"]
    return summary


def build_image(image: str, no_cache: bool) -> dict[str, Any]:
    command = ["docker", "build", "--platform", "linux/amd64", "-t", image]
    if no_cache:
        command.append("--no-cache")
    command.append(".")
    started = time.monotonic()
    proc = run_command(command, capture_output=True, text=True)
    return {
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "wall_seconds": round(time.monotonic() - started, 3),
        "tail": "\n".join(proc.stdout.splitlines()[-5:] + proc.stderr.splitlines()[-5:]),
    }


def scoped_run(image: str, env_seed: int | None, probe: bool) -> dict[str, Any]:
    command = ["docker", "run"]
    command.extend(RUN_FLAGS)
    if env_seed is not None:
        command.extend(["--env", f"PYTHONHASHSEED={env_seed}"])
    if probe:
        command.extend(["--entrypoint", "python", image, "-c", PROBE])
    else:
        command.append(image)
    started = time.monotonic()
    proc = run_command(command, capture_output=True)
    wall = time.monotonic() - started
    result: dict[str, Any] = {
        "returncode": proc.returncode,
        "wall_seconds": round(wall, 4),
        "stdout": proc.stdout,
        "stdout_bytes": len(proc.stdout),
        "stdout_sha256": sha256_bytes(proc.stdout),
        "stderr": proc.stderr.decode("utf-8", errors="replace"),
    }
    if probe:
        result.update(parse_probe(result["stderr"]))
    return result


def score_output(path: Path, cpu_seconds: float | None = None) -> dict[str, Any]:
    command = [sys.executable, str(ROOT / "score.py"), str(SAMPLE), str(ANSWERS), str(path)]
    if cpu_seconds is not None:
        command.extend(["--cpu-seconds", str(cpu_seconds)])
    proc = run_command(command, capture_output=True, text=True)
    report = parse_score_report(proc.stdout + proc.stderr)
    report["returncode"] = proc.returncode
    return report


def mutation_evidence(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "not_run"}
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    try:
        payload = json.loads(path.read_text("utf-8"))
    except ValueError:
        return {"status": "invalid_json", "path": str(path)}
    return {"status": "provided", "path": str(path), "summary": payload}


def ledger_row(result: dict[str, Any], args: argparse.Namespace) -> str:
    cells = [
        args.benchmark_id,
        args.source_revision,
        args.architecture_version,
        "one_command_harness_constrained_amd64",
        "sample_30_commits",
        "adaptive",
        str(result["selected_test_count"]),
        str(result["misses"]),
        f"{result['base_seconds']:.3f}",
        f"{result['simulated_seconds']:.3f}",
        "not_measured" if result["cpu_seconds"] is None else f"{result['cpu_seconds']:.3f}",
        f"{result['median_wall_seconds']:.3f}",
        "not_measured" if result["peak_memory_mb"] is None else f"{result['peak_memory_mb']:.1f}",
        result["result_status"],
        f"sha256={result['output_sha256']};tests={result['unit_tests']['tests_run']};"
        f"seeds={'-'.join(str(s) for s in args.hash_seeds)};"
        f"stdout_bytes={result['stdout_bytes']};mutation={result['mutation']['status']}",
    ]
    return ",".join(cells)


def run(args: argparse.Namespace) -> dict[str, Any]:
    missing = [str(p.relative_to(ROOT)) for p in (TESTS_JSON, ANSWERS, ROOT / "score.py") if not p.exists()]
    if missing or shutil.which("docker") is None:
        raise SystemExit(f"preflight failed; missing={missing}, docker={shutil.which('docker')}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tests = json.loads(TESTS_JSON.read_text("utf-8"))["tests"]
    result: dict[str, Any] = {
        "candidate_image": args.image,
        "unit_tests": unit_tests(),
        "build": (
            {"passed": True, "returncode": 0, "wall_seconds": 0.0, "tail": "skipped"}
            if args.skip_build
            else build_image(args.image, args.no_cache)
        ),
        "seeds": [],
        "mutation": mutation_evidence(args.mutation_evidence),
    }

    probes = [scoped_run(args.image, None, probe=True) for _ in range(args.probe_runs)]
    result["probe"] = {
        "runs": [
            {
                "returncode": p["returncode"],
                "cpu_seconds": p.get("cpu_seconds"),
                "peak_memory_mb": p.get("peak_memory_mb"),
            }
            for p in probes
        ],
        "returncode": max(p["returncode"] for p in probes),
        "cpu_seconds": statistics.median(p["cpu_seconds"] for p in probes if p.get("cpu_seconds") is not None)
        if all(p.get("cpu_seconds") is not None for p in probes)
        else None,
        "peak_memory_mb": statistics.median(p["peak_memory_mb"] for p in probes if p.get("peak_memory_mb") is not None)
        if all(p.get("peak_memory_mb") is not None for p in probes)
        else None,
    }
    probe_result = result["probe"]

    baseline: bytes | None = None
    for seed in args.hash_seeds:
        run_result = scoped_run(args.image, seed, probe=False)
        out_path = output_dir / f"output.seed{seed}.jsonl"
        out_path.write_bytes(run_result["stdout"])
        scored = score_output(out_path, result["probe"]["cpu_seconds"])
        base_ms, selected_count = compute_base_and_count(run_result["stdout"], tests)
        entry = {
            "seed": seed,
            "returncode": run_result["returncode"],
            "wall_seconds": run_result["wall_seconds"],
            "stdout_bytes": run_result["stdout_bytes"],
            "stdout_sha256": run_result["stdout_sha256"],
            "simulated_seconds": scored.get("simulated_seconds"),
            "misses": scored.get("misses"),
            "rejected": scored.get("rejected"),
            "total_seconds": scored.get("total_seconds"),
            "base_seconds": base_ms / 1000,
            "selected_test_count": selected_count,
        }
        result["seeds"].append(entry)
        if baseline is None:
            baseline = run_result["stdout"]

    valid = [s for s in result["seeds"] if s["rejected"] is None and s["misses"] is not None]
    result["output_sha256"] = baseline and sha256_bytes(baseline)
    result["byte_identical"] = all(s["stdout_sha256"] == result["output_sha256"] for s in result["seeds"])
    result["simulated_seconds"] = statistics.median(s["simulated_seconds"] for s in valid) if valid else None
    result["misses"] = max(s["misses"] for s in valid) if valid else None
    result["base_seconds"] = statistics.median(s["base_seconds"] for s in valid) if valid else None
    result["selected_test_count"] = valid[0]["selected_test_count"] if valid else 0
    result["median_wall_seconds"] = statistics.median(s["wall_seconds"] for s in result["seeds"])
    result["stdout_bytes"] = max(s["stdout_bytes"] for s in result["seeds"])
    result["cpu_seconds"] = probe_result.get("cpu_seconds")
    result["peak_memory_mb"] = probe_result.get("peak_memory_mb")
    result["total_seconds"] = (
        statistics.median(s["total_seconds"] for s in valid if s["total_seconds"] is not None)
        if valid and all(s["total_seconds"] is not None for s in valid)
        else None
    )
    result["limitations"] = [
        "cpu_seconds and peak_memory_mb come from an in-container rusage probe, not the server scorer",
        "independent mutation comparison is not run; pass --mutation-evidence to attach outside-truth results",
    ]

    gates = {
        "unit_tests": result["unit_tests"]["passed"],
        "build": result["build"]["passed"],
        "valid_output": len(valid) == len(result["seeds"]),
        "zero_misses": result["misses"] == 0,
        "byte_identical": result["byte_identical"],
        "stdout_under_2mb": result["stdout_bytes"] < 2_000_000,
        "probe_ok": probe_result["returncode"] == 0 and result["cpu_seconds"] is not None,
    }
    result["gates"] = gates
    result["result_status"] = "VERIFIED_ZERO_MISS" if all(gates.values()) else "REJECTED"
    result["ledger_csv_row"] = ledger_row(result, args)

    summary_path = output_dir / "harness_result.json"
    summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["summary_path"] = str(summary_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="blast-radius-candidate")
    parser.add_argument("--output-dir", default="/tmp/rwx-candidate-harness")
    parser.add_argument("--hash-seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--probe-runs", type=int, default=3)
    parser.add_argument("--benchmark-id", default="HARNESS-CANDIDATE")
    parser.add_argument("--source-revision", default="candidate")
    parser.add_argument("--architecture-version", default="candidate")
    parser.add_argument("--mutation-evidence", type=Path, default=None)
    args = parser.parse_args()

    result = run(args)
    print(result["ledger_csv_row"])
    print(f"status={result['result_status']} summary={result['summary_path']}")
    return 0 if result["result_status"] == "VERIFIED_ZERO_MISS" else 1


if __name__ == "__main__":
    sys.exit(main())
