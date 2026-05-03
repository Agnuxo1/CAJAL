# 🧠 CAJAL

> **认知学术期刊撰写层** — 在本地生成可发表的科研论文，完全免费，零云依赖。

[![PyPI](https://img.shields.io/badge/PyPI-cajal--p2pclaw-blueviolet)](https://pypi.org/project/cajal-p2pclaw/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Agnuxo1%2FCAJAL-blue)](https://github.com/Agnuxo1/CAJAL)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Agnuxo%2FCAJAL-orange)](https://huggingface.co/Agnuxo)
[![P2PCLAW](https://img.shields.io/badge/Powered%20by-P2PCLAW-red)](https://p2pclaw.com)

---

## CAJAL 是什么？

CAJAL 是一个**本地科研论文生成器**，完全在您的机器上运行。无需 API 密钥。无需订阅。数据不会离开您的电脑。

以**圣地亚哥·拉蒙-卡哈尔**命名——现代神经科学之父，他对神经网络的开创性研究映射了我们的使命：让科学知识的生成变得可及、去中心化且免费。

### 核心特性

| 特性 | 描述 |
|------|------|
| 🔒 **100% 本地** | 所有计算在您的硬件上运行。零数据外泄。 |
| 🆓 **零成本** | MIT 许可证。无订阅、无层级、无限制。 |
| 📄 **可发表格式** | 7 部分论文：摘要 → 引言 → 方法 → 结果 → 讨论 → 结论 → 参考文献。 |
| 🔗 **真实引用** | 集成 arXiv 和 CrossRef，提供可验证的真实引用。无幻觉引用。 |
| ⚖️ **评审团评分** | 8-10 个 LLM 评委在 10 个质量维度上评估每篇论文。即时同行评审。 |
| 🔌 **100+ 集成** | 原生支持 LangChain、CrewAI、AutoGen、LlamaIndex、VS Code、Jupyter、Ollama 等。 |
| 🤖 **任意 LLM** | 兼容任何 Ollama 模型。使用您自己的权重。 |

---

## 快速开始

```bash
# 1. 安装 CAJAL
pip install cajal-p2pclaw

# 2. 安装 Ollama（如未安装）
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 3. 创建 CAJAL 模型
ollama create cajal -f integrations/ollama/Modelfile

# 4. 生成您的第一篇论文
python -c "from cajal_p2pclaw import PaperGenerator; \
  PaperGenerator().generate('量子纠错与表面码')"
```

### Python API

```python
from cajal_p2pclaw import PaperGenerator

gen = PaperGenerator(model="cajal", host="http://localhost:11434")
paper = gen.generate(
    topic="量子机器学习用于药物发现",
    format="markdown",
    min_references=10
)
print(paper)
```

---

## 原生集成

| 平台 | 集成类型 | 文件 |
|------|---------|------|
| **LangChain** | LLM 包装器 | `integrations/langchain/llm.py` |
| **CrewAI** | 多智能体 PaperCrew | `integrations/crewai/llm.py` |
| **AutoGen** | 4 智能体设置 | `integrations/autogen/client.py` |
| **LlamaIndex** | 查询引擎 + 工具 | `integrations/llamaindex/llm.py` |
| **VS Code** | 设置 + 命令 | `integrations/vscode/cajal.json` |
| **Ollama** | Modelfile | `integrations/ollama/Modelfile` |
| **Jupyter** | `%%cajal` 魔法命令 | `integrations/jupyter/cajal_magic.py` |

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
**组织：** [P2PCLAW Research Network](https://p2pclaw.com)  
**许可证：** MIT

> *"大脑是一个由许多未探索的大陆和广阔未知领域组成的世界。"*
> — **圣地亚哥·拉蒙-卡哈尔** (1852–1934)
