import sys
sys.path.insert(0, 'E:/CAJAL-9B')
from q8_0_optimizer_v8 import *

# Quick test: generate one paper and check structure
topic = 'Adaptive Timeout Calibration for Byzantine Fault-Tolerant Consensus'
sim = run_simulation()
print(f'[SIM] {sim}')

prompt = build_paper_prompt(topic, sim, 1)
opts = {'num_predict': 24000, 'temperature': 0.4, 'top_p': 0.9, 'top_k': 50, 'repeat_penalty': 1.18}

print('[GEN] Generating...')
raw = generate_paper(MODEL, prompt, SYSTEM_PROMPT, opts)
print(f'[RAW] Length: {len(raw)} chars, {len(raw.split())} words')

print('[FIX] Injecting code and structural fixes...')
paper = inject_code_and_bridge(raw, sim)

w = len(paper.split())
print(f'[POST] Words after injection: {w}')

if w < 2600:
    print('[EXPAND] Expanding...')
    paper = expand_paper_to_minimum(paper, topic, 2600)
    paper = auto_structural_fixes(paper)
    w = len(paper.split())
    print(f'[POST] Words after expansion: {w}')

# Check sections
sections = ['Abstract', 'Introduction', 'Methodology', 'Results', 'Discussion', 'Conclusion', 'References']
present = [s for s in sections if re.search(rf'^##\s+{s}\b', paper, re.MULTILINE | re.IGNORECASE)]
print(f'[CHECK] Sections present: {present}')
print(f'[CHECK] Missing: {set(sections) - set(present)}')
print(f'[CHECK] Word count: {w}')
has_code = '```python' in paper
has_table = 'Table 1' in paper
has_refs = '[1] Lamport' in paper
print(f'[CHECK] Has code: {has_code}')
print(f'[CHECK] Has Table 1: {has_table}')
print(f'[CHECK] Has refs: {has_refs}')

# Save test
from pathlib import Path
Path('E:/CAJAL-9B/papers').mkdir(exist_ok=True)
Path('E:/CAJAL-9B/papers/test_v8_autonomous.md').write_text(paper, encoding='utf-8')
print('[SAVE] Saved to papers/test_v8_autonomous.md')
