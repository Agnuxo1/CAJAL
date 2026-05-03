# 🧠 CAJAL

> **Когнитивный слой для написания академических журналов** — Генерируйте научные статьи, готовые к публикации, локально, бесплатно и без зависимости от облака.

[![PyPI](https://img.shields.io/badge/PyPI-cajal--p2pclaw-blueviolet)](https://pypi.org/project/cajal-p2pclaw/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Agnuxo1%2FCAJAL-blue)](https://github.com/Agnuxo1/CAJAL)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Agnuxo%2FCAJAL-orange)](https://huggingface.co/Agnuxo)
[![P2PCLAW](https://img.shields.io/badge/Powered%20by-P2PCLAW-red)](https://p2pclaw.com)

---

## Что такое CAJAL?

CAJAL — это **локальный генератор научных статей**, который работает полностью на вашем компьютере. Никаких API-ключей. Никаких подписок. Данные не покидают ваш компьютер.

Назван в честь **Сантьяго Рамон-и-Кахаля** — отца современной нейронауки, чьи новаторские работы о нейронных сетях отражают нашу миссию: сделать создание научных знаний доступным, децентрализованным и бесплатным.

### Ключевые особенности

| Особенность | Описание |
|-------------|----------|
| 🔒 **100% Локальный** | Все вычисления выполняются на вашем оборудовании. Нулевая утечка данных. |
| 🆓 **Нулевая стоимость** | Лицензия MIT. Никаких подписок, уровней, ограничений. |
| 📄 **Готов к публикации** | 7-раздельная статья: Аннотация → Введение → Методы → Результаты → Обсуждение → Вывод → Список литературы. |
| 🔗 **Реальные цитаты** | Интеграция с arXiv и CrossRef для проверяемых, реальных ссылок. Никаких галлюцинированных цитат. |
| ⚖️ **Оценка трибунала** | 8–10 LLM-судей оценивают каждую статью по 10 качественным измерениям. Мгновенное рецензирование. |
| 🔌 **100+ интеграций** | Нативные наборы для LangChain, CrewAI, AutoGen, LlamaIndex, VS Code, Jupyter, Ollama и других. |
| 🤖 **Любая LLM** | Работает с любой совместимой с Ollama моделью. Используйте собственные веса. |

---

## Быстрый старт

```bash
# 1. Установите CAJAL
pip install cajal-p2pclaw

# 2. Установите Ollama (если еще не установлен)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 3. Создайте модель CAJAL
ollama create cajal -f integrations/ollama/Modelfile

# 4. Сгенерируйте свою первую статью
python -c "from cajal_p2pclaw import PaperGenerator; \
  PaperGenerator().generate('Квантовая коррекция ошибок с поверхностными кодами')"
```

### Python API

```python
from cajal_p2pclaw import PaperGenerator

gen = PaperGenerator(model="cajal", host="http://localhost:11434")
paper = gen.generate(
    topic="Квантовое машинное обучение для открытия лекарств",
    format="markdown",
    min_references=10
)
print(paper)
```

---

## Нативные интеграции

| Платформа | Интеграция | Файл |
|-----------|-----------|------|
| **LangChain** | LLM-обертка | `integrations/langchain/llm.py` |
| **CrewAI** | Мультиагент PaperCrew | `integrations/crewai/llm.py` |
| **AutoGen** | 4-агентная настройка | `integrations/autogen/client.py` |
| **LlamaIndex** | Поисковый движок + инструмент | `integrations/llamaindex/llm.py` |
| **VS Code** | Настройки + команды | `integrations/vscode/cajal.json` |
| **Ollama** | Modelfile | `integrations/ollama/Modelfile` |
| **Jupyter** | Магическая команда `%%cajal` | `integrations/jupyter/cajal_magic.py` |

---

## Цитирование

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

**Автор:** [Francisco Angulo de Lafuente](https://github.com/Agnuxo1) (@Agnuxo1)  
**Организация:** [P2PCLAW Research Network](https://p2pclaw.com)  
**Лицензия:** MIT

> *«Мозг — это мир, состоящий из множества неисследованных континентов и больших участков неизвестной территории.»*
> — **Сантьяго Рамон-и-Кахаль** (1852–1934)
