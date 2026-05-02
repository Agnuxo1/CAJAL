# CAJAL + Manubot Integration

## Setup

```bash
pip install cajal-p2pclaw manubot
```

## Generate Paper

```python
from cajal_p2pclaw import CAJALChat
import manubot

chat = CAJALChat()

# Generate sections
abstract = chat.send("Write an abstract on P2P consensus mechanisms")
introduction = chat.send("Write introduction with citations")
methods = chat.send("Describe methodology")
results = chat.send("Present results")
discussion = chat.send("Discuss implications")

# Assemble manuscript
manuscript = f"""
---
title: "{chat.send('Generate paper title')}"
author:
  - Francisco Angulo de Lafuente
---

## Abstract

{abstract}

## Introduction

{introduction}

## Methods

{methods}

## Results

{results}

## Discussion

{discussion}
"""

with open('content/01.main-text.md', 'w') as f:
    f.write(manuscript)
```

## Build

```bash
manubot build
```
