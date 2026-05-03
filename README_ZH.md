# CAJAL-4B-P2PCLAW — 本地科学论文生成器

[English](README.md) | [Español](README_ES.md) | **简体中文** | [日本語](README_JA.md) | [Русский](README_RU.md)

## 🧠 概述

CAJAL 是一个经过微调的 40 亿参数模型，专门用于生成具有真实 arXiv 引用的出版级科学论文 —— 完全在本地运行。

**核心功能：**
- 生成 7 部分论文结构（摘要 → 引言 → 方法 → 结果 → 讨论 → 结论 → 参考文献）
- 所有引用均通过 arXiv API 验证（真实论文、真实作者、真实 DOI）
- 法庭评分系统：3 名模拟评审员对每部分打分（0-10）
- 100% 本地推理（Ollama、vLLM、llama.cpp）
- 支持 BibTeX 导出

## 🚀 快速开始

### 通过 Ollama
```bash
ollama run cajal-p2pclaw
```

### 通过 PyPI
```bash
pip install cajal-p2pclaw
cajal-generate --topic "量子机器学习" --output paper.md
```

## 📊 技术规格

| 参数 | 值 |
|------|-----|
| 基础模型 | Qwen3.5-4B |
| 参数量 | 42 亿 |
| 上下文窗口 | 32K tokens |
| 显存需求 | 8GB VRAM |
| 许可证 | MIT |

## 🔗 链接

- **GitHub:** https://github.com/Agnuxo1/CAJAL
- **HuggingFace:** https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
- **论文:** https://arxiv.org/pdf/2604.19792
- **在线演示:** https://www.p2pclaw.com/silicon

## 🤝 集成生态

CAJAL 已与 30+ 开源项目集成：Ollama、Open WebUI、Chainlit、Gradio、Dify、n8n、Flowise、LibreChat 等。

---
*CAJAL — 以圣地亚哥·拉蒙·卡哈尔（Santiago Ramón y Cajal）命名，现代神经科学之父。*
