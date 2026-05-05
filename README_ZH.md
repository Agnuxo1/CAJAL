# CAJAL — 用于本地科学论文生成的开源模型

## 什么是 CAJAL？

CAJAL 是一个完全开源、本地运行的大语言模型，专门用于生成高质量科学论文。无需 API 密钥，无需云端，完全在您的硬件上运行。

## 核心特性

- 🔬 **科学专业化** — 针对研究论文、摘要和文献综述进行优化
- 🏠 **完全本地** — 在您的 GPU 上运行，数据永不离开您的机器
- 💰 **零成本** — 开源，免费使用，无订阅费用
- 🔒 **隐私保护** — 敏感研究数据保持本地
- 📄 **论文就绪输出** — LaTeX 兼容格式，引用管理

## 快速开始

### 使用 Ollama（推荐）
```bash
ollama pull Agnuxo/CAJAL-4B-P2PCLAW
ollama run CAJAL-4B-P2PCLAW
```

### 使用 llama.cpp
```bash
# 下载 GGUF 模型
wget https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/resolve/main/cajal-4b-q4_k_m.gguf

# 运行
./main -m cajal-4b-q4_k_m.gguf --temp 0.7
```

### 使用 Hugging Face Transformers
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
tokenizer = AutoTokenizer.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
```

## 生成科学论文

```python
prompt = """生成一篇关于气候变化对农业影响的机器学习研究论文摘要。
包含：背景、方法、结果、结论。"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
print(tokenizer.decode(outputs[0]))
```

## 模型规格

| 属性 | 值 |
|------|-----|
| 架构 | Qwen2.5-4B-Instruct |
| 微调方法 | QLoRA + 强化学习 |
| 训练数据 | 50+ 篇 P2PCLAW 科学论文 |
| 上下文长度 | 32K tokens |
| 许可证 | Apache 2.0 |
| 量化 | GGUF Q4_K_M, Q5_K_M, Q8_0 |

## 集成

| 平台 | 状态 | 链接 |
|------|------|------|
| Ollama | ✅ | [模型页面](https://ollama.com/Agnuxo/CAJAL-4B-P2PCLAW) |
| LM Studio | ✅ | [下载](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW) |
| Jan | ✅ | [配置指南](https://github.com/Agnuxo1/CAJAL/blob/main/docs/JAN.md) |
| Continue.dev | ✅ | [配置](https://github.com/Agnuxo1/CAJAL/blob/main/docs/CONTINUE.md) |
| Pinokio | ✅ | [脚本](https://github.com/Agnuxo1/CAJAL/blob/main/docs/PINOKIO.md) |

## 系统要求

| 硬件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| GPU | 4GB VRAM | 8GB+ VRAM |
| CPU | 4 核 | 8 核+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 3GB | 5GB+ |

## P2PCLAW 生态系统

CAJAL 是 P2PCLAW 的一部分 — 一个去中心化的科学研究网络：

- 🤖 **14 个自主代理** — 研究、基准测试、安全
- 🔗 **P2P 同步** — 跨设备代理协作
- 🔐 **加密保险库** — 本地优先，隐私保护
- 🌐 **Web 应用** — https://p2pclaw.com

## 引用

```bibtex
@software{cajal2026,
  author = {Angulo de Lafuente, Francisco},
  title = {CAJAL: Local Scientific Paper Generation Model},
  year = {2026},
  url = {https://github.com/Agnuxo1/CAJAL}
}
```

## 许可证

Apache 2.0 — 详见 [LICENSE](LICENSE)

---

*P2PCLAW — 去中心化科学研究*
