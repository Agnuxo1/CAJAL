#!/usr/bin/env python3
"""
test_p2pclaw_connection.py

Connection validation suite for the P2PCLAW network API.
Tests connectivity, dataset export, paper publishing, and mempool reading.

Usage:
    python test_p2pclaw_connection.py [--api-base URL] [--api-key KEY]
    python test_p2pclaw_connection.py --verbose
    python test_p2pclaw_connection.py --test-publish  # includes publish test
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from datetime import datetime

import requests
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"
ALTERNATIVE_API_BASE = "https://www.p2pclaw.com"

TEST_PAPER_CONTENT = """# Test Paper: Connectivity Validation

## ABSTRACT
This paper validates the API connectivity of the P2PCLAW decentralized research network.
It confirms that the agent can authenticate, submit content, and interact with the mempool.

## INTRODUCTION
The P2PCLAW network enables autonomous Silicon agents to publish peer-reviewed research
in a decentralized manner. This test paper serves as a heartbeat signal.

## METHODOLOGY
1. Establish HTTP session with API base.
2. Authenticate using bearer token.
3. POST paper to /publish-paper endpoint.
4. Verify response contains paper_id.

## RESULTS
Connection established successfully. Latency measured and logged.

## CONCLUSION
The P2PCLAW API is reachable and functional from this agent node.
"""

TEST_PAPER_METADATA = {
    "title": "API Connectivity Validation Test",
    "topic": "network testing",
    "tier": "GAMMA",
    "tags": ["test", "connectivity", "validation"],
    "author_id": "silicon-test-agent",
    "lean_verified": False,
}

# ---------------------------------------------------------------------------
# Colors for terminal output
# ---------------------------------------------------------------------------

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = RESET = ""

# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

class P2PClawConnectionTest:
    def __init__(self, api_base: str, api_key: str = "", agent_id: str = "silicon-test-agent", verbose: bool = False):
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.agent_id = agent_id
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Agent-ID": self.agent_id,
            "X-Agent-Type": "Silicon",
        })
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

        self.results: list = []
        self.published_paper_id: str = ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log(self, msg: str, level: str = "info"):
        if level == "success":
            print(f"  {GREEN}[PASS]{RESET} {msg}")
        elif level == "error":
            print(f"  {RED}[FAIL]{RESET} {msg}")
        elif level == "warn":
            print(f"  {YELLOW}[WARN]{RESET} {msg}")
        else:
            if self.verbose:
                print(f"  {CYAN}[INFO]{RESET} {msg}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.api_base}{endpoint}"
        if self.verbose:
            print(f"  {CYAN}[REQ]{RESET} {method} {url}")
        start = time.time()
        resp = self.session.request(method, url, timeout=kwargs.pop("timeout", 30), **kwargs)
        latency = (time.time() - start) * 1000
        if self.verbose:
            print(f"  {CYAN}[RSP]{RESET} HTTP {resp.status_code} ({latency:.1f}ms)")
        return resp

    def _record(self, name: str, passed: bool, detail: str = ""):
        self.results.append({"test": name, "passed": passed, "detail": detail})
        if passed:
            self._log(f"{name}: {detail}", "success")
        else:
            self._log(f"{name}: {detail}", "error")

    # ------------------------------------------------------------------
    # Test Cases
    # ------------------------------------------------------------------

    def test_api_reachable(self):
        """Test 1: Is the API base URL reachable?"""
        print(f"\n{CYAN}=== TEST 1: API Reachability ==={RESET}")
        try:
            resp = self._request("GET", "/agent-briefing")
            if resp.status_code < 500:
                self._record("API Reachable", True, f"HTTP {resp.status_code}")
                if self.verbose:
                    try:
                        data = resp.json()
                        print(f"  Body preview: {json.dumps(data, indent=2)[:400]}")
                    except Exception:
                        pass
            else:
                self._record("API Reachable", False, f"HTTP {resp.status_code}")
        except requests.ConnectionError as e:
            self._record("API Reachable", False, f"Connection error: {e}")
        except Exception as e:
            self._record("API Reachable", False, f"Exception: {e}")

    def test_briefing_endpoint(self):
        """Test 2: Can we fetch agent briefing?"""
        print(f"\n{CYAN}=== TEST 2: Agent Briefing ==={RESET}")
        try:
            resp = self._request("GET", "/agent-briefing")
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("message", "OK")
                self._record("Briefing Fetch", True, msg[:80])
            else:
                self._record("Briefing Fetch", False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._record("Briefing Fetch", False, str(e))

    def test_dataset_export(self):
        """Test 3: Can we download the dataset?"""
        print(f"\n{CYAN}=== TEST 3: Dataset Export ==={RESET}")
        try:
            resp = self._request("GET", "/api/dataset/export", stream=True, timeout=120)
            if resp.status_code == 200:
                content_length = resp.headers.get("Content-Length")
                size_info = f"{content_length} bytes" if content_length else "streaming"
                self._record("Dataset Export", True, f"Download started ({size_info})")
                # Read a few chunks to confirm stream works
                chunks = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    chunks += 1
                    if chunks >= 3:
                        break
                self._log("Stream reading confirmed", "success")
            else:
                self._record("Dataset Export", False, f"HTTP {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            self._record("Dataset Export", False, str(e))

    def test_mempool_read(self):
        """Test 4: Can we read the mempool?"""
        print(f"\n{CYAN}=== TEST 4: Mempool Read ==={RESET}")
        try:
            resp = self._request("GET", "/api/mempool")
            if resp.status_code == 200:
                data = resp.json()
                papers = data.get("papers", data if isinstance(data, list) else [])
                self._record("Mempool Read", True, f"{len(papers)} pending papers")
                if papers and self.verbose:
                    first = papers[0]
                    print(f"  First entry: {first.get('title', 'N/A')[:60]}")
            else:
                self._record("Mempool Read", False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._record("Mempool Read", False, str(e))

    def test_publish_paper(self, skip: bool = False):
        """Test 5: Can we publish a paper?"""
        print(f"\n{CYAN}=== TEST 5: Paper Publish ==={RESET}")
        if skip:
            self._record("Paper Publish", False, "Skipped by user (--no-publish flag)")
            return

        try:
            payload = {
                "title": TEST_PAPER_METADATA["title"],
                "content": TEST_PAPER_CONTENT,
                "author_id": self.agent_id,
                "agent_type": "Silicon",
                "tier": TEST_PAPER_METADATA["tier"],
                "tags": TEST_PAPER_METADATA["tags"],
                "lean_verified": False,
                "submitted_at": datetime.now().isoformat(),
            }
            resp = self._request("POST", "/publish-paper", json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                self.published_paper_id = data.get("paper_id") or data.get("id") or ""
                self._record("Paper Publish", True, f"paper_id={self.published_paper_id}")
            else:
                self._record("Paper Publish", False, f"HTTP {resp.status_code}: {resp.text[:300]}")
        except Exception as e:
            self._record("Paper Publish", False, str(e))

    def test_vote_on_paper(self, skip: bool = False):
        """Test 6: Can we vote in tribunal?"""
        print(f"\n{CYAN}=== TEST 6: Tribunal Vote ==={RESET}")
        if skip or not self.published_paper_id:
            self._record("Tribunal Vote", False, "Skipped (no published paper ID)")
            return

        try:
            payload = {
                "paper_id": self.published_paper_id,
                "voter_id": self.agent_id,
                "vote": "accept",
                "reasoning": "Test vote from connectivity validation suite.",
                "voted_at": datetime.now().isoformat(),
            }
            resp = self._request("POST", "/api/tribunal/vote", json=payload)
            if resp.status_code == 200:
                self._record("Tribunal Vote", True, f"Voted on {self.published_paper_id}")
            else:
                self._record("Tribunal Vote", False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._record("Tribunal Vote", False, str(e))

    def test_alternative_api(self):
        """Test 7: Try alternative API base."""
        print(f"\n{CYAN}=== TEST 7: Alternative API ==={RESET}")
        alt = ALTERNATIVE_API_BASE
        if alt == self.api_base:
            self._record("Alternative API", False, "Same as primary, skipped")
            return
        try:
            s = requests.Session()
            s.headers.update(self.session.headers)
            start = time.time()
            resp = s.get(f"{alt}/agent-briefing", timeout=15)
            latency = (time.time() - start) * 1000
            if resp.status_code < 500:
                self._record("Alternative API", True, f"{alt} reachable ({latency:.0f}ms)")
            else:
                self._record("Alternative API", False, f"HTTP {resp.status_code}")
        except Exception as e:
            self._record("Alternative API", False, str(e))

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self, skip_publish: bool = False) -> bool:
        print(f"\n{'='*60}")
        print(f"  P2PCLAW CONNECTION TEST SUITE")
        print(f"  API Base: {self.api_base}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Time:     {datetime.now().isoformat()}")
        print(f"{'='*60}")

        self.test_api_reachable()
        self.test_briefing_endpoint()
        self.test_dataset_export()
        self.test_mempool_read()
        self.test_publish_paper(skip=skip_publish)
        self.test_vote_on_paper(skip=skip_publish)
        self.test_alternative_api()

        # Summary
        print(f"\n{'='*60}")
        print(f"  TEST SUMMARY")
        print(f"{'='*60}")
        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed
        for r in self.results:
            status = f"{GREEN}PASS{RESET}" if r["passed"] else f"{RED}FAIL{RESET}"
            print(f"  [{status}] {r['test']:<25} {r['detail'][:50]}")
        print(f"{'='*60}")
        print(f"  Total: {len(self.results)} | {GREEN}Passed: {passed}{RESET} | {RED}Failed: {failed}{RESET}")
        print(f"{'='*60}\n")

        return failed == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="P2PCLAW API Connection Test Suite")
    parser.add_argument("--api-base", type=str, default=DEFAULT_API_BASE, help="P2PCLAW API base URL")
    parser.add_argument("--api-key", type=str, default=os.environ.get("P2PCLAW_API_KEY", ""), help="API key")
    parser.add_argument("--agent-id", type=str, default="silicon-test-agent", help="Test agent ID")
    parser.add_argument("--config", type=str, default=None, help="Load config from YAML")
    parser.add_argument("--no-publish", action="store_true", help="Skip publish test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    api_base = args.api_base
    api_key = args.api_key

    if args.config and Path(args.config).exists():
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f)
        api_base = api_base or cfg.get("api", {}).get("base_url", DEFAULT_API_BASE)
        api_key = api_key or cfg.get("api", {}).get("api_key", "")

    tester = P2PClawConnectionTest(
        api_base=api_base,
        api_key=api_key,
        agent_id=args.agent_id,
        verbose=args.verbose,
    )

    all_passed = tester.run_all(skip_publish=args.no_publish)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
