# CAJAL — модель с открытым исходным кодом для локальной генерации научных статей

## Что такое CAJAL?

CAJAL — это полностью открытая, локально работающая языковая модель, специализированная для генерации высококачественных научных статей. Никаких API-ключей, никакого облака, полностью на вашем оборудовании.

## Ключевые особенности

- 🔬 **Научная специализация** — оптимизирована для исследовательских статей, аннотаций и обзоров литературы
- 🏠 **Полностью локальная** — работает на вашем GPU, данные никогда не покидают ваш компьютер
- 💰 **Нулевая стоимость** — открытый исходный код, бесплатное использование, без подписок
- 🔒 **Защита конфиденциальности** — конфиденциальные исследовательские данные остаются локально
- 📄 **Готовые к публикации выходные данные** — совместимость с LaTeX, управление цитированием

## Быстрый старт

### Использование Ollama (рекомендуется)
```bash
ollama pull Agnuxo/CAJAL-4B-P2PCLAW
ollama run CAJAL-4B-P2PCLAW
```

### Использование llama.cpp
```bash
# Скачать GGUF модель
wget https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/resolve/main/cajal-4b-q4_k_m.gguf

# Запустить
./main -m cajal-4b-q4_k_m.gguf --temp 0.7
```

### Использование Hugging Face Transformers
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
tokenizer = AutoTokenizer.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")
```

## Генерация научной статьи

```python
prompt = """Сгенерируйте аннотацию исследовательской статьи по машинному обучению о влиянии изменения климата на сельское хозяйство.
Включите: введение, методы, результаты, заключение."""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
print(tokenizer.decode(outputs[0]))
```

## Спецификации модели

| Атрибут | Значение |
|------|-----|
| Архитектура | Qwen2.5-4B-Instruct |
| Метод дообучения | QLoRA + обучение с подкреплением |
| Обучающие данные | 50+ научных статей P2PCLAW |
| Длина контекста | 32K токенов |
| Лицензия | Apache 2.0 |
| Квантование | GGUF Q4_K_M, Q5_K_M, Q8_0 |

## Интеграции

| Платформа | Статус | Ссылка |
|------|------|------|
| Ollama | ✅ | [Страница модели](https://ollama.com/Agnuxo/CAJAL-4B-P2PCLAW) |
| LM Studio | ✅ | [Скачать](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW) |
| Jan | ✅ | [Руководство](https://github.com/Agnuxo1/CAJAL/blob/main/docs/JAN.md) |
| Continue.dev | ✅ | [Конфигурация](https://github.com/Agnuxo1/CAJAL/blob/main/docs/CONTINUE.md) |
| Pinokio | ✅ | [Скрипт](https://github.com/Agnuxo1/CAJAL/blob/main/docs/PINOKIO.md) |

## Системные требования

| Компонент | Минимум | Рекомендуется |
|------|---------|---------|
| GPU | 4GB VRAM | 8GB+ VRAM |
| CPU | 4 ядра | 8 ядер+ |
| ОЗУ | 8GB | 16GB+ |
| Хранилище | 3GB | 5GB+ |

## Экосистема P2PCLAW

CAJAL — часть P2PCLAW — децентрализованной сети для научных исследований:

- 🤖 **14 автономных агентов** — исследования, бенчмарки, безопасность
- 🔗 **P2P-синхронизация** — сотрудничество агентов между устройствами
- 🔐 **Шифрованное хранилище** — локально, с защитой конфиденциальности
- 🌐 **Веб-приложение** — https://p2pclaw.com

## Цитирование

```bibtex
@software{cajal2026,
  author = {Angulo de Lafuente, Francisco},
  title = {CAJAL: Local Scientific Paper Generation Model},
  year = {2026},
  url = {https://github.com/Agnuxo1/CAJAL}
}
```

## Лицензия

Apache 2.0 — подробности в [LICENSE](LICENSE)

---

*P2PCLAW — децентрализованные научные исследования*
