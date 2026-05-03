# CAJAL-4B-P2PCLAW — ローカル科学論文生成モデル

[English](README.md) | [Español](README_ES.md) | [简体中文](README_ZH.md) | **日本語** | [Русский](README_RU.md)

## 🧠 概要

CAJAL は、実際の arXiv 引用を持つ出版品質の科学論文を生成するために微調整された 40 億パラメータモデルです —— 完全にローカルで実行されます。

**主な機能：**
- 7セクション論文構造を生成（要旨 → 序論 → 方法 → 結果 → 考察 → 結論 → 参考文献）
- すべての引用は arXiv API で検証済み（実在の論文、著者、DOI）
- トリビュナル採点システム：3人の模擬審査員が各セクションを採点（0-10）
- 100% ローカル推論（Ollama、vLLM、llama.cpp）
- BibTeX エクスポート対応

## 🚀 クイックスタート

### Ollama 経由
```bash
ollama run cajal-p2pclaw
```

### PyPI 経由
```bash
pip install cajal-p2pclaw
cajal-generate --topic "量子機械学習" --output paper.md
```

## 📊 技術仕様

| パラメータ | 値 |
|----------|-----|
| ベースモデル | Qwen3.5-4B |
| パラメータ数 | 42億 |
| コンテキストウィンドウ | 32Kトークン |
| VRAM要件 | 8GB |
| ライセンス | MIT |

## 🔗 リンク

- **GitHub:** https://github.com/Agnuxo1/CAJAL
- **HuggingFace:** https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- **論文:** https://arxiv.org/pdf/2604.19792
- **デモ:** https://www.p2pclaw.com/silicon

## 🤝 統合エコシステム

CAJAL は 30以上のオープンソースプロジェクトと統合されています：Ollama、Open WebUI、Chainlit、Gradio、Dify、n8n、Flowise、LibreChat など。

---
*CAJAL — 現代神経科学の父、サンティアゴ・ラモン・イ・カハルにちなんで命名。*
