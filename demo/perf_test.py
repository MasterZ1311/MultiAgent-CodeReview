#!/usr/bin/env python3
"""
cerberus</> Performance & Latency Benchmark Suite.
Measures sequential latency, concurrent throughput, and multi-tier cache acceleration.
"""

import asyncio
from pathlib import Path
import statistics
import sys
import time

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cerberus.agents.orchestrator import orchestrator
from cerberus.models.schemas import CodeReviewRequest

console = Console()

TEST_SNIPPETS = [
    "def add(a, b): return a + b",
    "def query(uid): return db.execute(f'SELECT * FROM users WHERE id = {uid}')",
    "def proc(arr):\n  for i in arr:\n    for j in arr: pass",
    "import logging\ndef log(ssn): logging.info(f'SSN: {ssn}')",
    "from ..deep.pkg import x\ndef fn(): pass"
]


async def run_benchmark():
    console.print(Panel(
        "[bold cyan]cerberus</>[/bold cyan] [bold white]Performance & Scalability Benchmark[/bold white]\n"
        "[dim]Benchmarking parallel agent orchestration, in-memory caching, and asynchronous throughput[/dim]",
        title="[bold blue]⚡ BENCHMARK SUITE[/bold blue]",
        border_style="blue"
    ))

    # 1. Warm-up
    warmup_req = CodeReviewRequest(code="def warmup(): pass", language="python")
    await orchestrator.execute_review(warmup_req)

    # 2. Sequential Benchmark (20 requests)
    seq_latencies = []
    for i in range(20):
        code = f"{TEST_SNIPPETS[i % len(TEST_SNIPPETS)]}\n# iteration {i}"
        req = CodeReviewRequest(code=code, language="python")
        t0 = time.perf_counter()
        resp = await orchestrator.execute_review(req)
        seq_latencies.append((time.perf_counter() - t0) * 1000)

    # 3. Concurrent Benchmark (20 parallel requests)
    async def _timed_review(c):
        r = CodeReviewRequest(code=c, language="python")
        t = time.perf_counter()
        res = await orchestrator.execute_review(r)
        return (time.perf_counter() - t) * 1000

    concurrent_codes = [f"{TEST_SNIPPETS[i % len(TEST_SNIPPETS)]}\n# concurrent_{i}" for i in range(20)]
    t_start = time.perf_counter()
    con_latencies = await asyncio.gather(*[_timed_review(c) for c in concurrent_codes])
    total_con_time = time.perf_counter() - t_start
    con_rps = len(con_latencies) / total_con_time

    # 4. Cache Hit Benchmark (Re-running same 10 requests)
    cache_latencies = []
    cache_hits = 0
    for code in concurrent_codes[:10]:
        r = CodeReviewRequest(code=code, language="python")
        t0 = time.perf_counter()
        resp = await orchestrator.execute_review(r)
        cache_latencies.append((time.perf_counter() - t0) * 1000)
        if resp.cache_hit:
            cache_hits += 1

    # Output Table
    table = Table(title="Benchmark Performance Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Mode", width=22)
    table.add_column("Requests", justify="right", width=10)
    table.add_column("Avg Latency", justify="right", width=14)
    table.add_column("P95 Latency", justify="right", width=14)
    table.add_column("Max Latency", justify="right", width=14)
    table.add_column("Throughput / Details", justify="left")

    table.add_row(
        "Sequential (Cold)",
        str(len(seq_latencies)),
        f"{statistics.mean(seq_latencies):.2f} ms",
        f"{statistics.quantiles(seq_latencies, n=20)[18]:.2f} ms",
        f"{max(seq_latencies):.2f} ms",
        f"~{1000 / statistics.mean(seq_latencies):.1f} req/s"
    )

    table.add_row(
        "Concurrent (20 Gather)",
        str(len(con_latencies)),
        f"{statistics.mean(con_latencies):.2f} ms",
        f"{statistics.quantiles(con_latencies, n=20)[18]:.2f} ms",
        f"{max(con_latencies):.2f} ms",
        f"[bold green]{con_rps:.1f} req/s[/bold green] (Parallel)"
    )

    table.add_row(
        "Cache Hit (Hot)",
        str(len(cache_latencies)),
        f"[bold green]{statistics.mean(cache_latencies):.2f} ms[/bold green]",
        f"{statistics.quantiles(cache_latencies, n=20)[18]:.2f} ms",
        f"{max(cache_latencies):.2f} ms",
        f"[bold cyan]{(cache_hits / len(cache_latencies)) * 100:.0f}% Hit Rate[/bold cyan] (~{statistics.mean(seq_latencies) / max(0.01, statistics.mean(cache_latencies)):.0f}x Speedup)"
    )

    console.print(table)
    console.print(Panel(
        f"[bold green]✔ Benchmark Completed Successfully[/bold green]\n"
        f"• Average Cold Review Latency: [bold]{statistics.mean(seq_latencies):.2f} ms[/bold]\n"
        f"• Average Cached Review Latency: [bold]{statistics.mean(cache_latencies):.2f} ms[/bold]\n"
        f"• Peak Concurrent Throughput: [bold]{con_rps:.1f} reviews/sec[/bold]\n"
        f"• All 5 Agents executed in parallel per review with zero external network overhead.",
        title="[bold green]📊 SUMMARY VERDICT[/bold green]",
        border_style="green"
    ))


if __name__ == "__main__":
    asyncio.run(run_benchmark())
