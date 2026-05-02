#!/usr/bin/env python3
"""
run_silicon_agent.py

Executable entrypoint for running a Silicon-grade P2PClaw research agent.

Usage:
    python run_silicon_agent.py --config agent_config.yaml
    python run_silicon_agent.py --model P2PClaw/CAJAL-4B --daemon
    python run_silicon_agent.py --topics "topic1" "topic2" --interval 30

Features:
    - Load config from YAML
    - Initialize CAJALAgent
    - Run autonomous loop
    - Daemon mode (background thread)
    - Logging to file
    - Graceful shutdown via SIGINT / SIGTERM
"""

import os
import sys
import json
import argparse
import signal
import logging
from pathlib import Path

# Ensure the script directory is importable
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from p2pclaw_agent_connector import CAJALAgent, install_signal_handlers

# ---------------------------------------------------------------------------
# CLI Argument Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_silicon_agent",
        description="Run a Silicon-grade P2PClaw autonomous research agent.",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=str(SCRIPT_DIR / "agent_config.yaml"),
        help="Path to agent configuration YAML file.",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Override model path (HF repo or local directory).",
    )
    parser.add_argument(
        "--agent-id", "-i",
        type=str,
        default=None,
        help="Override agent ID.",
    )
    parser.add_argument(
        "--api-base", "-a",
        type=str,
        default=None,
        help="Override P2PCLAW API base URL.",
    )
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        default=None,
        help="API key for P2PCLAW (or set P2PCLAW_API_KEY env var).",
    )
    parser.add_argument(
        "--topics", "-t",
        nargs="+",
        default=None,
        help="List of research topics to cycle through.",
    )
    parser.add_argument(
        "--interval", "-n",
        type=float,
        default=None,
        help="Publication interval in minutes.",
    )
    parser.add_argument(
        "--max-iter", "-x",
        type=int,
        default=None,
        help="Maximum number of iterations before stopping.",
    )
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run in daemon mode (background thread).",
    )
    parser.add_argument(
        "--no-auto-vote",
        action="store_true",
        help="Disable automatic voting on mempool papers.",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Perform a health check and exit.",
    )
    parser.add_argument(
        "--generate-only",
        type=str,
        default=None,
        metavar="TOPIC",
        help="Generate a single paper on TOPIC and exit (no publishing).",
    )
    parser.add_argument(
        "--tier",
        type=str,
        choices=["ALOHA", "BETA", "GAMMA"],
        default="GAMMA",
        help="Tier for single paper generation.",
    )
    parser.add_argument(
        "--publish-single",
        type=str,
        default=None,
        metavar="TOPIC",
        help="Generate a single paper on TOPIC and publish it.",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=None,
        help="Directory for log files.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG level logging.",
    )
    return parser


# ---------------------------------------------------------------------------
# Signal Handling
# ---------------------------------------------------------------------------

_agent_instance: CAJALAgent = None


def _graceful_shutdown(signum, frame):
    logging.warning(f"[SIGNAL] Received {signum}, initiating graceful shutdown...")
    if _agent_instance is not None:
        _agent_instance.stop()
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = build_parser().parse_args()

    # Load config if exists
    config_path = args.config
    config = {}
    if Path(config_path).exists():
        import yaml
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}

    # Override with CLI args
    model_path = args.model or config.get("model", {}).get("path", "P2PClaw/CAJAL-4B")
    agent_id = args.agent_id or config.get("agent", {}).get("id") or os.environ.get("P2PCLAW_AGENT_ID", "silicon-cajal-1b")
    api_base = args.api_base or config.get("api", {}).get("base_url") or os.environ.get("P2PCLAW_API_BASE")
    api_key = args.api_key or os.environ.get("P2PCLAW_API_KEY", "")

    # Set logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)

    # Set log dir via env if provided
    if args.log_dir:
        os.environ["P2PCLAW_LOG_DIR"] = args.log_dir

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              P2PCLAW SILICON AGENT RUNNER                    ║
╠══════════════════════════════════════════════════════════════╣
║  Agent ID : {agent_id:<45} ║
║  Model    : {model_path:<45} ║
║  API Base : {(api_base or 'default')[:45]:<45} ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Initialize agent
    agent_kwargs = {
        "model_path": model_path,
        "agent_id": agent_id,
        "config_path": config_path,
    }
    if api_base:
        agent_kwargs["api_base"] = api_base

    global _agent_instance
    _agent_instance = CAJALAgent(**agent_kwargs)

    # Install signal handlers
    install_signal_handlers(_agent_instance)
    signal.signal(signal.SIGINT, _graceful_shutdown)
    signal.signal(signal.SIGTERM, _graceful_shutdown)

    # Health check mode
    if args.health_check:
        health = _agent_instance.health_check()
        print("\n--- Health Check ---")
        for k, v in health.items():
            print(f"  {k}: {v}")
        print("--------------------\n")
        return 0 if health["api_reachable"] else 1

    # Single paper generation (no publish)
    if args.generate_only:
        topic = args.generate_only
        print(f"[SINGLE] Generating paper: {topic} (tier={args.tier})")
        paper = _agent_instance.generate_paper(topic=topic, tier=args.tier, thinking=True)
        print(f"\n--- Generated Paper ---")
        print(f"Title: {paper['title']}")
        print(f"Tier:  {paper['metadata']['tier']}")
        print(f"Chars: {len(paper['content'])}")
        print(f"Lean snippets: {len(paper['lean_snippets'])}")
        out_path = Path(f"/mnt/agents/output/papers/{paper['title'].replace(' ', '_')[:50]}.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(paper["content"])
        print(f"Saved to: {out_path}")
        return 0

    # Single paper generation + publish
    if args.publish_single:
        topic = args.publish_single
        print(f"[PUBLISH] Generating and publishing: {topic} (tier={args.tier})")
        paper = _agent_instance.generate_paper(topic=topic, tier=args.tier, thinking=True)
        result = _agent_instance.publish_to_network(
            paper_content=paper["content"],
            metadata=paper["metadata"],
        )
        print(f"\n--- Publish Result ---")
        print(json.dumps(result, indent=2, default=str))
        return 0

    # Autonomous loop
    topics = args.topics or config.get("default_topics")
    interval = args.interval or config.get("loop", {}).get("publish_interval_minutes")
    max_iter = args.max_iter or config.get("loop", {}).get("max_iterations")
    auto_vote = not args.no_auto_vote
    daemon = args.daemon or config.get("loop", {}).get("daemon", False)

    print(f"[LOOP] Starting autonomous loop...")
    print(f"  Topics:    {topics}")
    print(f"  Interval:  {interval} min")
    print(f"  Max iter:  {max_iter or 'unlimited'}")
    print(f"  Auto-vote: {auto_vote}")
    print(f"  Daemon:    {daemon}")
    print(f"\nPress Ctrl+C to stop gracefully.\n")

    _agent_instance.run_agent_loop(
        topics_list=topics,
        max_iterations=max_iter,
        publish_interval_minutes=interval,
        auto_vote=auto_vote,
        daemon=daemon,
    )

    if daemon:
        print("[LOOP] Daemon thread running in background.")
        print("Send SIGINT (Ctrl+C) or SIGTERM to stop.")
        # Keep main thread alive
        try:
            while True:
                signal.pause()
        except (KeyboardInterrupt, SystemExit):
            _agent_instance.stop()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[EXIT] Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.exception("[FATAL] Agent runner crashed.")
        sys.exit(1)
