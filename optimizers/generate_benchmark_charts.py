import matplotlib.pyplot as plt
import numpy as np

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('CAJAL-9B v2 — P2PCLAW Benchmark Results', fontsize=18, fontweight='bold', y=0.98)

# Data
configs = ['Q8_0 v3-13\n(Auto)', 'Q8_0 v7-4\n(Manual)', 'Q8_0 v8b-2\n(Auto)']
overall = [7.5, 8.2, 6.3]
reproducibility = [6.0, 9.9, 9.6]
citations = [8.6, 8.3, 6.3]
references = [8.8, 7.9, 6.1]
novelty = [7.2, 7.2, 6.5]

# Color palette
colors = ['#2E86AB', '#A23B72', '#F18F01']

# 1. Overall Score Comparison
ax = axes[0, 0]
bars = ax.bar(configs, overall, color=colors, edgecolor='black', linewidth=1.2, alpha=0.85)
ax.set_ylabel('Overall Score (/10)')
ax.set_title('Overall Score by Configuration', fontweight='bold')
ax.set_ylim(0, 10)
for bar, val in zip(bars, overall):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15, f'{val}', 
            ha='center', va='bottom', fontsize=13, fontweight='bold')
ax.axhline(y=7.0, color='gray', linestyle='--', alpha=0.5, label='SOTA Threshold (~7.0)')
ax.legend(loc='upper left')

# 2. Key Metrics Radar-style bar
ax = axes[0, 1]
x = np.arange(len(configs))
width = 0.2
ax.bar(x - width, reproducibility, width, label='Reproducibility', color='#06A77D', edgecolor='black')
ax.bar(x, citations, width, label='Citation Quality', color='#F4A261', edgecolor='black')
ax.bar(x + width, novelty, width, label='Novelty', color='#E76F51', edgecolor='black')
ax.set_ylabel('Score (/10)')
ax.set_title('Key Quality Metrics', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(configs)
ax.set_ylim(0, 10.5)
ax.legend(loc='upper left')

# 3. Section-wise breakdown for best run (v7-4)
ax = axes[1, 0]
sections = ['Abstract', 'Intro', 'Method', 'Results', 'Discussion', 'Conclusion', 'Refs']
scores_best = [7.3, 7.7, 7.7, 7.3, 6.9, 7.1, 7.9]
scores_auto = [6.9, 6.8, 6.8, 5.7, 6.6, 4.9, 6.1]

x = np.arange(len(sections))
width = 0.35
ax.bar(x - width/2, scores_best, width, label='Best (8.2) — Manual cleanup', color='#2E86AB', edgecolor='black')
ax.bar(x + width/2, scores_auto, width, label='Auto (7.1) — No cleanup', color='#F18F01', edgecolor='black')
ax.set_ylabel('Score (/10)')
ax.set_title('Section Scores: Best vs Fully Automated', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(sections, rotation=15, ha='right')
ax.set_ylim(0, 10)
ax.legend(loc='upper left')

# 4. Score distribution / consensus
ax = axes[1, 1]
configs_judges = ['v3-13\n(8 judges)', 'v7-4\n(4 judges)', 'v8b-2\n(9 judges)']
consensus = [79, 90, 63]
judges = [8, 4, 9]

ax2 = ax.twinx()
bars = ax.bar(configs_judges, consensus, color=['#A23B72', '#2E86AB', '#F18F01'], 
              edgecolor='black', alpha=0.85, label='Consensus %')
ax.set_ylabel('Consensus (%)', color='black')
ax.set_title('Judge Panel Consensus', fontweight='bold')
ax.set_ylim(0, 100)

# Add judge count as text
for bar, j in zip(bars, judges):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
            f'{bar.get_height():.0f}%\n({j} judges)', 
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('E:/CAJAL-9B/benchmark_results.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("[OK] Saved benchmark_results.png")

# Create a second figure: Score progression over iterations
fig2, ax = plt.subplots(figsize=(12, 6))
iterations = list(range(1, 32))
scores_v3 = [0,0,0,0,0,6.5,0,0,0,0,0,0,7.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # simplified
ax.plot([6, 13], [6.5, 7.5], 'o-', color='#2E86AB', linewidth=2, markersize=8, label='Q8_0 v3 (Auto)')
ax.axhline(y=7.5, color='#2E86AB', linestyle='--', alpha=0.3)

# v7 manual iterations
ax.plot([4], [8.2], 's', color='#06A77D', markersize=12, markeredgecolor='black', 
        markeredgewidth=1.5, label='Q8_0 v7 (Manual cleanup) — 8.2')

# v8b auto
ax.plot([2], [6.3], 'D', color='#F18F01', markersize=10, markeredgecolor='black',
        markeredgewidth=1.5, label='Q8_0 v8b (Fully Auto) — 6.3')

ax.set_xlabel('Iteration Number')
ax.set_ylabel('P2PCLAW Overall Score (/10)')
ax.set_title('CAJAL-9B Score Progression Over Development', fontsize=14, fontweight='bold')
ax.set_ylim(4, 9)
ax.legend(loc='lower right', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('E:/CAJAL-9B/benchmark_progression.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("[OK] Saved benchmark_progression.png")
