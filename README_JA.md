# CAJAL — ローカル科学論文生成のためのオープンソースモデル

## CAJALとは？

CAJALは、高品質な科学論文を生成するために特化された、完全にオープンソースでローカル実行可能な大規模言語モデルです。APIキー不要、クラウド不要、あなたのハードウェア上で完全に動作します。

## 主な機能

- 🔬 **科学特化** — 研究論文、要約、文献レビューに最適化
- 🏠 **完全ローカル** — あなたのGPU上で実行、データが外部に流出しない
- 💰 **ゼロコスト** — オープンソース、無料使用、サブスクリプションなし
- 🔒 **プライバシー保護** — 機密性の高い研究データをローカルに保持
- 📄 **論文対応出力** — LaTeX互換フォーマット、引用管理

## クイックスタート

### Ollamaを使用（推奨）
```bash
ollama pull Agnuxo/CAJAL-4B-P2PCLAW
ollama run CAJAL-4B-P2PCLAW
```

### llama.cppを使用
```bash
# GGUFモデルをダウンロード
wget https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/resolve/main/cajal-4b-q4_k_m.gguf

# 実行
./main -m cajal-4b-q4_k_m.gguf --temp 0.7
```

### Hugging Face Transformersを使用
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
tokenizer = AutoTokenizer.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
```

## 科学論文の生成

```python
prompt = """気候変動が農業に与える影響に関する機械学習研究論文の要約を生成してください。
背景、方法、結果、結論を含めてください。"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
print(tokenizer.decode(outputs[0]))
```

## モデル仕様

| 属性 | 値 |
|------|-----|
| アーキテクチャ | Qwen2.5-4B-Instruct |
| ファインチューニング | QLoRA + 強化学習 |
| 学習データ | 50+ P2PCLAW科学論文 |
| コンテキスト長 | 32Kトークン |
| ライセンス | Apache 2.0 |
| 量子化 | GGUF Q4_K_M, Q5_K_M, Q8_0 |

## 統合

| プラットフォーム | 状態 | リンク |
|------|------|------|
| Ollama | ✅ | [モデルページ](https://ollama.com/Agnuxo/CAJAL-4B-P2PCLAW) |
| LM Studio | ✅ | [ダウンロード](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW) |
| Jan | ✅ | [設定ガイド](https://github.com/Agnuxo1/CAJAL/blob/main/docs/JAN.md) |
| Continue.dev | ✅ | [設定](https://github.com/Agnuxo1/CAJAL/blob/main/docs/CONTINUE.md) |
| Pinokio | ✅ | [スクリプト](https://github.com/Agnuxo1/CAJAL/blob/main/docs/PINOKIO.md) |

## システム要件

| ハードウェア | 最低構成 | 推奨構成 |
|------|---------|---------|
| GPU | 4GB VRAM | 8GB+ VRAM |
| CPU | 4コア | 8コア+ |
| メモリ | 8GB | 16GB+ |
| ストレージ | 3GB | 5GB+ |

## P2PCLAWエコシステム

CAJALはP2PCLAWの一部です — 分散型科学研究ネットワーク：

- 🤖 **14の自律エージェント** — 研究、ベンチマーク、セキュリティ
- 🔗 **P2P同期** — デバイス間エージェント連携
- 🔐 **暗号化ボールト** — ローカル優先、プライバシー保護
- 🌐 **Webアプリ** — https://p2pclaw.com

## 引用

```bibtex
@software{cajal2026,
  author = {Angulo de Lafuente, Francisco},
  title = {CAJAL: Local Scientific Paper Generation Model},
  year = {2026},
  url = {https://github.com/Agnuxo1/CAJAL}
}
```

## ライセンス

Apache 2.0 — 詳細は [LICENSE](LICENSE) を参照

---

*P2PCLAW — 分散型科学研究*
