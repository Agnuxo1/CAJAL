# 🧠 CAJAL

> **認知学術ジャーナル執筆レイヤー** — クラウドに依存せず、完全に無料で、ローカルに出版可能な科学論文を生成します。

[![PyPI](https://img.shields.io/badge/PyPI-cajal--p2pclaw-blueviolet)](https://pypi.org/project/cajal-p2pclaw/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Agnuxo1%2FCAJAL-blue)](https://github.com/Agnuxo1/CAJAL)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Agnuxo%2FCAJAL-orange)](https://huggingface.co/Agnuxo)
[![P2PCLAW](https://img.shields.io/badge/Powered%20by-P2PCLAW-red)](https://p2pclaw.com)

---

## CAJAL とは？

CAJAL は**ローカル科学論文生成器**です。あなたのマシン上で完全に動作します。API キー不要。サブスクリプション不要。データはあなたのコンピュータから外に出ません。

**サンティアゴ・ラモン・イ・カハル**にちなんで名付けられました——現代神経科学の父であり、神経ネットワークに関する先駆的な研究が私たちの使命を反映しています：科学知識の生成をアクセス可能にし、分散化し、無料にすること。

### 主な機能

| 機能 | 説明 |
|------|------|
| 🔒 **100% ローカル** | すべての計算はあなたのハードウェア上で実行されます。データの外部流出はゼロ。 |
| 🆓 **ゼロコスト** | MIT ライセンス。サブスクリプション、階層、制限なし。 |
| 📄 **出版可能な形式** | 7 部構成の論文：要旨 → 序論 → 方法 → 結果 → 考察 → 結論 → 参考文献。 |
| 🔗 **実際の引用** | arXiv と CrossRef と統合し、検証可能な実際の引用を提供。幻覚引用なし。 |
| ⚖️ **審査員採点** | 8-10 人の LLM 審査員が 10 の品質次元で各論文を評価。即時のピアレビュー。 |
| 🔌 **100+ 統合** | LangChain、CrewAI、AutoGen、LlamaIndex、VS Code、Jupyter、Ollama などにネイティブ対応。 |
| 🤖 **任意の LLM** | あらゆる Ollama 互換モデルで動作。独自の重みを使用可能。 |

---

## クイックスタート

```bash
# 1. CAJAL をインストール
pip install cajal-p2pclaw

# 2. Ollama をインストール（未インストールの場合）
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 3. CAJAL モデルを作成
ollama create cajal -f integrations/ollama/Modelfile

# 4. 最初の論文を生成
python -c "from cajal_p2pclaw import PaperGenerator; \
  PaperGenerator().generate('表面符号による量子誤り訂正')"
```

### Python API

```python
from cajal_p2pclaw import PaperGenerator

gen = PaperGenerator(model="cajal", host="http://localhost:11434")
paper = gen.generate(
    topic="創薬のための量子機械学習",
    format="markdown",
    min_references=10
)
print(paper)
```

---

## ネイティブ統合

| プラットフォーム | 統合タイプ | ファイル |
|------|---------|------|
| **LangChain** | LLM ラッパー | `integrations/langchain/llm.py` |
| **CrewAI** | マルチエージェント PaperCrew | `integrations/crewai/llm.py` |
| **AutoGen** | 4 エージェント設定 | `integrations/autogen/client.py` |
| **LlamaIndex** | クエリエンジン + ツール | `integrations/llamaindex/llm.py` |
| **VS Code** | 設定 + コマンド | `integrations/vscode/cajal.json` |
| **Ollama** | Modelfile | `integrations/ollama/Modelfile` |
| **Jupyter** | `%%cajal` マジックコマンド | `integrations/jupyter/cajal_magic.py` |

---

## 引用

```bibtex
@software{cajal2026,
  title = {CAJAL: Cognitive Academic Journal Authoring Layer},
  author = {Angulo de Lafuente, Francisco},
  organization = {P2PCLAW Research Network},
  year = {2026},
  url = {https://github.com/Agnuxo1/CAJAL}
}
```

---

**作者：** [Francisco Angulo de Lafuente](https://github.com/Agnuxo1) (@Agnuxo1)  
**組織：** [P2PCLAW Research Network](https://p2pclaw.com)  
**ライセンス：** MIT

> *「脳は、多くの未踏の大陸と広大な未知の領域からなる世界である。」*
> — **サンティアゴ・ラモン・イ・カハル** (1852–1934)
