# Guía Legal Completa para Publicar Modelos Derivados (Apache 2.0)
## Modelo: CAJAL | Bases: Qwen3 / Gemma 4

---

## 📋 Resumen Ejecutivo: Qué Permite Apache 2.0

La **Licencia Apache 2.0** es una de las licencias open source más permisivas y amigables para el mundo de la IA. En lenguaje simple:

| Permiso | ¿Lo permite Apache 2.0? |
|---------|------------------------|
| Usar el modelo para cualquier propósito (incluido comercial) | ✅ SÍ |
| Modificar el modelo (fine-tuning, merge, quantization) | ✅ SÍ |
| Redistribuir el modelo (con o sin los pesos) | ✅ SÍ |
| Ponerle tu propio nombre al modelo derivado | ✅ SÍ |
| NO liberar los pesos finales (mantenerlos privados) | ✅ SÍ |
| Sublicenciar el modelo derivado | ✅ SÍ |
| Integrarlo en productos propietarios o SaaS | ✅ SÍ |
| Vender acceso al modelo como API o servicio | ✅ SÍ |
| "Atacar" al licenciante original (patent retaliation clause) | ❌ NO (la licencia se rescinde) |

> **La única obligación real**: **Incluir atribución al modelo base** y una **copia de la licencia Apache 2.0**.

---

## ✅ Checklist de Cumplimiento Obligatorio

Antes de publicar o comercializar tu modelo derivado, verifica que has cumplido con TODOS estos puntos:

- [ ] **Incluir NOTICE de atribución**: Archivo `NOTICE` o sección en README que mencione el modelo base y sus autores.
- [ ] **Incluir copia de licencia Apache 2.0**: Archivo `LICENSE` con el texto completo de Apache 2.0 en tu repositorio.
- [ ] **Declarar modelo derivado en model card**: Especificar claramente que es un modelo derivado (fine-tuned, merged, etc.) del modelo base.
- [ ] **No usar trademarks del creador original**: No usar los nombres "Qwen", "Gemma", "Alibaba Cloud" o "Google" como si fueran tuyos, ni en la marca de tu producto.
- [ ] **Incluir copyright notices originales**: Si el modelo base incluye archivos con copyright, mantenerlos.
- [ ] **Documentar cambios realizados**: Indicar qué modificaciones hiciste (dataset, fine-tuning, merge, etc.).
- [ ] **Verificar compatibilidad de datasets de entrenamiento**: Asegurar que los datos usados para fine-tuning no introduzcan restricciones incompatibles.
- [ ] **Incluir disclaimer de garantía**: Apache 2.0 requiere que el software se distribuye "AS IS" (sin garantía).

---

## ✅ Qué SÍ Puedes Hacer (Con total libertad legal)

### 1. Llamarlo CAJAL (tu nombre propio)
Apache 2.0 te permite ponerle el nombre que quieras a tu modelo derivado. No estás obligado a mantener "Qwen" o "Gemma" en el nombre. Puedes crear tu propia marca.

**Ejemplo de nomenclatura válida**:
- `CAJAL` ✅
- `CAJAL-v1-Qwen3-Base` ✅ (opcional, menciona la base pero como información)

### 2. Vender acceso al modelo
Puedes monetizar el modelo:
- API paga con acceso al modelo
- Suscripción SaaS que use el modelo
- Licencias empresariales
- Servicios de consultoría basados en el modelo

### 3. NO liberar los pesos (mantenerlos privados)
Apache 2.0 **NO obliga** a liberar los pesos del modelo derivado. Puedes:
- Mantener los LoRA adapters privados
- No publicar el modelo completo fine-tuned
- Usarlo solo en tu infraestructura interna

> Nota: Esto es diferente de licencias copyleft (como GPL) o licencias de IA específicas que pueden exigir publicación.

### 4. Usar en producto comercial propietario
Puedes integrar el modelo en:
- Aplicaciones de código cerrado
- Servicios en la nube (AWS, GCP, Azure)
- Software empresarial
- Juegos, apps móviles, etc.

### 5. Publicar en Hugging Face con tu nombre
Puedes crear un repositorio en Hugging Face llamado:
- `tu-organizacion/CAJAL`
- `tu-usuario/CAJAL-v1`

Sin necesidad de incluir "Qwen" o "Gemma" en el nombre del repo.

### 6. Cambiar la licencia de tu modelo derivado
Puedes sublicenciar tu trabajo derivado bajo otra licencia permisiva:
- MIT
- BSD-3-Clause
- Otra Apache 2.0
- Incluso licencias propietarias (para tu parte adicional)

> Importante: La parte del modelo base sigue bajo Apache 2.0, pero tus modificaciones/adiciones pueden tener otra licencia.

---

## ❌ Qué NO Debes Hacer (Para Evitar Problemas Legales)

### 1. No reclamar que creaste el modelo base desde cero
**Prohibido**:
- "CAJAL es un modelo completamente original creado por nosotros"
- "Desarrollamos esta arquitectura de transformer desde cero"

**Obligatorio**:
- "CAJAL es un modelo fine-tuned derivado de Qwen3 (Alibaba Cloud)"
- "Basado en la arquitectura Gemma 4 de Google"

### 2. No eliminar la atribución original
Aunque no publiques los pesos, si publicas UN archivo de configuración, tokenizer, o documentación relacionada con el modelo, DEBES incluir la atribución.

### 3. No usar logos/nombres trademarked como si fueran tuyos
**Prohibido**:
- Usar el logo de Alibaba Cloud, Qwen, Google o Gemma en tu branding
- Llamar a tu producto "Qwen P2PClaw" o "Gemma Research Edition"
- Registrar "Qwen" o "Gemma" como marca de tu producto

**Permitido**:
- "Compatible con modelos Qwen3" (descripción factual)
- "Basado en Gemma 4" (atribución correcta)

### 4. No ofrecer garantías en nombre del autor original
No puedes decir: "Alibaba Cloud garantiza que este modelo funciona para X". Tú puedes ofrecer tus propias garantías, pero no en nombre del autor original.

### 5. No eliminar la cláusula de patentes
Si sublicencias, debes mantener la protección de patentes de Apache 2.0 (la "patent grant").

---

## 📄 Plantillas de Texto Legales (Listas para Copiar y Pegar)

### A. Texto de Atribución Corto (para README.md)

```markdown
## Attribution

This model, **CAJAL**, is a derivative work based on:

- **Qwen3** by Alibaba Cloud, licensed under [Apache 2.0](LICENSE)

The base model weights and architecture are used under the terms of the Apache 2.0 license.
Additional training, fine-tuning, and modifications were performed by [Your Name/Organization].

CAJAL is not affiliated with, endorsed by, or sponsored by Alibaba Cloud.
```

### B. Texto de Atribución Largo (para Model Card / Documentación)

```markdown
## Attribution & License

**CAJAL** is a derivative model created by [Your Name/Organization].

### Base Model
This model is derived from:
- **Model**: Qwen3-235B-A22B (or Qwen3-30B-A3B, etc.)
- **Author**: Alibaba Cloud (Qwen series)
- **License**: Apache License 2.0
- **Source**: https://huggingface.co/Qwen/Qwen3-235B-A22B

### What Was Modified
- Fine-tuned on [dataset name] for scientific research tasks
- Applied LoRA adapters with rank [X] and alpha [Y]
- Modified system prompt and chat template for research assistance
- [Any other modifications]

### License of This Derivative Work
The original base model weights remain under Apache 2.0.
The modifications (LoRA adapters, training code, documentation) are released under [Apache 2.0 / MIT / Your choice].

### Third-Party Components
- Training framework: Unsloth (Apache 2.0)
- Dataset: [Dataset name] ([Dataset license])
- Evaluation framework: [If applicable]

### Disclaimer
THIS MODEL IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. See the Apache 2.0 license for full terms.
```

### C. Aviso Legal para Producto Comercial

```markdown
## Legal Notice

**CAJAL** incorporates artificial intelligence models that are derivative
works of third-party open source software.

### Open Source Attributions

This product includes software developed by:

1. **Alibaba Cloud** - Qwen3 model (Apache License 2.0)
   Copyright © Alibaba Cloud. All rights reserved.
   https://huggingface.co/Qwen

2. **[Training Framework]** - [Name] ([License])
   [Copyright notice]

### Your Rights
As a user of this product, you have the right to request the source code and
license text of any open source components incorporated herein, in accordance
with their respective licenses. Please contact [your contact] for such requests.

### No Endorsement
The use of third-party open source models does not imply endorsement by the
original authors of this product or its outputs.

### Warranty Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### D. Texto para Hugging Face README (sección de licencia)

```markdown
## License

The base model weights are licensed under the **Apache License 2.0** by Alibaba Cloud.
This derivative model (CAJAL) is released under **Apache License 2.0**.

- Base model: [Qwen3-235B-A22B](https://huggingface.co/Qwen/Qwen3-235B-A22B) (Apache 2.0)
- This model: CAJAL (Apache 2.0)

You may use, modify, and distribute this model for commercial and non-commercial
purposes, subject to the terms of the Apache 2.0 license. A copy of the license
is included in this repository (`LICENSE`).
```

---

## 📜 Licencia Recomendada para Tu Modelo Derivado

### Recomendación Principal: Apache 2.0

Si tu modelo derivado es principalmente pesos de fine-tuning o LoRA adapters sobre Qwen3/Gemma 4, **recomendamos mantener Apache 2.0**.

**Ventajas**:
- ✅ Mantiene la cadena de permisividad
- ✅ Compatible con productos comerciales
- ✅ Reconocida legalmente en todo el mundo
- ✅ Fácil de cumplir (solo atribución + copia de licencia)
- ✅ Protección de patentes incluida

### Alternativa: MIT License

Si deseas una licencia aún más simple:

```
MIT License

Copyright (c) 2026 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

**Nota**: MIT no tiene cláusula de patentes como Apache 2.0. Para modelos de IA donde las patentes pueden ser relevantes, Apache 2.0 es más segura.

### No recomendado

- **GPL/ AGPL**: Incompatibles con uso en productos propietarios
- **Licencias con restricciones éticas**: Pueden generar incertidumbre legal
- **CC BY-NC** (non-commercial): Impide el uso comercial que buscas

### Licencia Dual (Opción Avanzada)

Puedes ofrecer:
- **Apache 2.0** para uso estándar
- **Licencia comercial** para empresas que desean soporte/garantías adicionales

Esto es 100% compatible con Apache 2.0.

---

## 📚 Referencias Legales

- [Apache License 2.0 - Texto Completo](https://www.apache.org/licenses/LICENSE-2.0)
- [Apache 2.0 FAQ](https://www.apache.org/foundation/license-faq.html)
- [Qwen3 Model Card - Hugging Face](https://huggingface.co/Qwen)
- [Gemma Terms of Use - Google](https://ai.google.dev/gemma/terms)
- [OSI - Open Source Initiative](https://opensource.org/licenses/Apache-2.0)

---

## ⚠️ Disclaimer Final

> Esta guía es proporcionada con fines informativos y educativos. No constituye asesoramiento legal profesional. Para decisiones críticas sobre licenciamiento comercial, consulta con un abogado especializado en propiedad intelectual y software open source.

---

*Guía generada para CAJAL | Compatible con Qwen3 & Gemma 4 | 2026*
