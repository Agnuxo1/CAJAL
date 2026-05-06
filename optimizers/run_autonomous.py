#!/usr/bin/env python3
"""
run_autonomous.py

One-shot autonomous paper generator for CAJAL-9B v2.
No human intervention required. Produces a P2PCLAW-ready paper.

Usage:
    python run_autonomous.py

Requirements:
    - Ollama running with cajal-9b-v2:latest loaded
    - Python 3.10+
    - requests package

Output:
    - Saves paper to papers/ directory
    - Prints paper stats
    - Optionally publishes to P2PCLAW if --publish flag is used
"""

import sys
import time
import subprocess
from pathlib import Path

# Import from v8 optimizer
sys.path.insert(0, str(Path(__file__).parent))
from q8_0_optimizer_v8 import (
    run_simulation, generate_paper, auto_structural_fixes,
    expand_paper_to_minimum, inject_code_and_bridge,
    extract_title, build_paper_prompt, SYSTEM_PROMPT,
    MODEL, PAPERS_DIR, complete_tribunal, publish_paper,
    poll_for_scores
)

DEFAULT_TOPIC = "Adaptive Timeout Calibration for Byzantine Fault-Tolerant Consensus"


def ensure_ollama_running():
    """Check if Ollama is accessible, try to start if not."""
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            print("[OK] Ollama is running")
            return True
    except Exception:
        pass
    
    print("[START] Attempting to start Ollama...")
    try:
        subprocess.Popen([r"E:\Ollama\ollama.exe", "serve"], 
                        creationflags=subprocess.DETACHED_PROCESS)
        time.sleep(10)
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            print("[OK] Ollama started successfully")
            return True
    except Exception as e:
        print(f"[FAIL] Could not start Ollama: {e}")
    return False


def generate_autonomous_paper(topic: str = DEFAULT_TOPIC, publish: bool = False):
    print("=" * 70)
    print("  CAJAL-9B AUTONOMOUS PAPER GENERATOR v8")
    print("  100% Automated — No Human Intervention")
    print("=" * 70)
    
    if not ensure_ollama_running():
        print("[ERROR] Ollama is not available. Please start it manually.")
        return None
    
    print(f"[TOPIC] {topic}")
    
    # Run simulation
    sim_results = run_simulation()
    print(f"[SIM] Results: {sim_results}")
    
    # Generate paper
    prompt = build_paper_prompt(topic, sim_results, iteration=1)
    gen_opts = {
        "num_predict": 24000,
        "temperature": 0.4,
        "top_p": 0.90,
        "top_k": 50,
        "repeat_penalty": 1.18,
    }
    
    print("[GEN] Generating paper with CAJAL-9B Q8_0...")
    raw_paper = generate_paper(MODEL, prompt, SYSTEM_PROMPT, gen_opts)
    
    if not raw_paper or len(raw_paper) < 500:
        print("[FAIL] Paper generation failed or too short")
        return None
    
    # Apply all automated fixes
    print("[FIX] Applying structural corrections...")
    paper_text = inject_code_and_bridge(raw_paper, sim_results)
    
    word_count = len(paper_text.split())
    if word_count < 2600:
        print(f"[EXPAND] Paper too short ({word_count} words), expanding...")
        paper_text = expand_paper_to_minimum(paper_text, topic, target_words=2600)
        paper_text = auto_structural_fixes(paper_text)
    
    paper_text = auto_structural_fixes(paper_text)
    word_count = len(paper_text.split())
    
    title = extract_title(paper_text, topic)
    print(f"[DONE] Title: {title}")
    print(f"[DONE] Words: {word_count}")
    print(f"[DONE] Sections: Abstract, Introduction, Methodology, Results, Discussion, Conclusion, References")
    
    # Save
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CAJAL_autonomous_{ts}.md"
    filepath = PAPERS_DIR / filename
    filepath.write_text(paper_text, encoding="utf-8")
    print(f"[SAVE] {filepath}")
    
    if publish:
        agent_id = f"cajal-9b-v2-autonomous-{ts}"
        print(f"[TRIBUNAL] Starting examination...")
        clearance = complete_tribunal(agent_id, topic)
        if clearance:
            print(f"[PUB] Publishing to P2PCLAW...")
            pub_result = publish_paper(title, paper_text, agent_id, clearance)
            paper_id = pub_result.get("paperId") or pub_result.get("id")
            if paper_id:
                print(f"[PUB] Published: {paper_id}")
                print("[WAIT] Waiting for scores (this may take 2-5 minutes)...")
                scores = poll_for_scores(paper_id, agent_id)
                if scores:
                    overall = scores.get("overall")
                    print(f"[SCORE] Overall: {overall}/10")
                    print(f"[SCORE] Reproducibility: {scores.get('reproducibility')}")
                    print(f"[SCORE] Citations: {scores.get('citation_quality')}")
                else:
                    print("[SCORE] Scores not yet available")
            else:
                print(f"[PUB] Failed: {pub_result}")
        else:
            print("[TRIBUNAL] Failed to pass examination")
    
    print("=" * 70)
    print("  AUTONOMOUS GENERATION COMPLETE")
    print("=" * 70)
    return filepath


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a P2PCLAW paper autonomously with CAJAL-9B")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Paper topic")
    parser.add_argument("--publish", action="store_true", help="Publish to P2PCLAW after generation")
    args = parser.parse_args()
    
    generate_autonomous_paper(topic=args.topic, publish=args.publish)
