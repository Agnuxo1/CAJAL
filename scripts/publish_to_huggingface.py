#!/usr/bin/env python3
"""
publish_to_huggingface.py

Script completo para publicar modelos derivados en Hugging Face
con cumplimiento legal total de Apache 2.0.

Uso:
    python publish_to_huggingface.py \
        --model_path ./output/CAJAL \
        --repo_name CAJAL \
        --org_name mi-organizacion \
        --base_model Qwen/Qwen3-30B-A3B \
        --base_model_author "Alibaba Cloud" \
        --model_description "Modelo de investigacion cientifica" \
        --hf_token $HF_TOKEN

Autor: CAJAL Team
Licencia: Apache 2.0
"""

import argparse
import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==============================================================================
# DEPENDENCIAS
# ==============================================================================

try:
    from huggingface_hub import (
        HfApi,
        HfFolder,
        create_repo,
        upload_folder,
        upload_file,
        hf_hub_download,
        whoami,
    )
    from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError
except ImportError:
    print("[ERROR] huggingface_hub no esta instalado. Instala con:")
    print("  pip install huggingface_hub")
    sys.exit(1)


# ==============================================================================
# PLANTILLA DE README.md (Model Card)
# ==============================================================================

README_TEMPLATE = r"""---
{card_data}
---

# {model_name}

## Descripcion

{model_description}

Este modelo es un trabajo derivado de **{base_model}** de {base_model_author}.
Ha sido entrenado y optimizado para {intended_use}.

## Atribucion

Este modelo es un trabajo derivado basado en:

- **Modelo base:** [{base_model}](https://huggingface.co/{base_model})
- **Autor del modelo base:** {base_model_author}
- **Licencia del modelo base:** Apache License 2.0

{model_name} **NO esta afiliado, respaldado ni patrocinado** por {base_model_author}.

## Licencia

Los pesos del modelo base estan licenciados bajo **Apache License 2.0** por {base_model_author}.
Este modelo derivado ({model_name}) se libera bajo **{derivative_license}**.

Puedes usar, modificar y distribuir este modelo para fines comerciales y no comerciales,
sujeto a los terminos de la licencia Apache 2.0. Una copia de la licencia se incluye
en este repositorio (`LICENSE`).

## Uso

### Instalacion

```bash
pip install transformers torch huggingface_hub
```

### Cargar el modelo

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "{repo_id}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
```

### Inferencia

```python
messages = [
    {{"role": "user", "content": "Explica el metodo cientifico en 3 pasos."}}
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
print(response)
```

## Detalles del Entrenamiento

| Hiperparametro | Valor |
|----------------|-------|
| Learning Rate | {learning_rate} |
| Batch Size | {batch_size} |
| Epochs | {num_epochs} |
| LoRA Rank | {lora_rank} |
| LoRA Alpha | {lora_alpha} |
| Framework | {training_framework} |
| Hardware | {training_hardware} |
| Tiempo de entrenamiento | {training_time} |

## Limitaciones

- Este modelo ha sido entrenado para {intended_use} y puede no funcionar bien para otros usos.
- Puede producir alucinaciones o informacion incorrecta. Verifica siempre las afirmaciones importantes.
- No utilizar para tomar decisiones medicas, legales o financieras criticas sin supervision humana.

## Aviso Legal

ESTE MODELO SE PROPORCIONA "TAL CUAL", SIN GARANTIA DE NINGUN TIPO, EXPRESA O IMPLICITA,
INCLUYENDO PERO NO LIMITADO A GARANTIAS DE COMERCIABILIDAD, IDONEIDAD PARA UN PROPOSITO
PARTICULAR Y NO INFRACCION.

## Citacion

Si utilizas este modelo en tu investigacion, por favor cita:

```bibtex
@software{{{model_name.lower().replace('-', '_')},
  author = {{{author_name}}},
  title = {{{model_name}}},
  year = {{{year}}},
  url = {{https://huggingface.co/{repo_id}}}
}}
```

Y cita tambien el modelo base:

```bibtex
{base_model_bibtex}
```

---

*Model card generado automaticamente el {date}*
"""


# ==============================================================================
# PLANTILLA DE LICENSE (Apache 2.0)
# ==============================================================================

APACHE_2_0_LICENSE = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Support. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {year} {author}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


# ==============================================================================
# PLANTILLA DE NOTICE
# ==============================================================================

NOTICE_TEMPLATE = """{model_name}
Copyright {year} {author}

This product includes software and/or model weights derived from the following
third-party works, used under the terms of their respective licenses:

================================================================================
Base Model
================================================================================

{base_model_name}
Copyright {base_model_year} {base_model_author}
Licensed under the Apache License, Version 2.0
Original repository: https://huggingface.co/{base_model}

================================================================================
Training Framework
================================================================================

{training_framework}
Licensed under the Apache License, Version 2.0

================================================================================
License Notice
================================================================================

This product, {model_name}, is a derivative work. The original base model
and its components remain under their original licenses. The modifications,
additional training, LoRA adapters, and documentation created by
{author} are provided under the {derivative_license}.

You may obtain a copy of the Apache License 2.0 at:

    https://www.apache.org/licenses/LICENSE-2.0

A copy of the Apache License 2.0 is also included in the LICENSE file in this
repository.

Unless required by applicable law or agreed to in writing, software distributed
under the Apache 2.0 license is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
license for the specific language governing permissions and limitations under
the license.

================================================================================
Trademark Notice
================================================================================

{base_model_name} and {base_model_author} are trademarks of their respective
owners. {model_name} is an independent derivative work and is not affiliated
with, endorsed by, or sponsored by {base_model_author}.
"""


# ==============================================================================
# CONFIGURACIONES DE MODELOS BASE
# ==============================================================================

BASE_MODEL_BIBTEX = {
    "Qwen/Qwen3-235B-A22B": """@article{qwen3,
  title={Qwen3 Technical Report},
  author={Qwen Team},
  journal={arXiv preprint arXiv:2505.XXXXX},
  year={2025}
}""",
    "Qwen/Qwen3-30B-A3B": """@article{qwen3,
  title={Qwen3 Technical Report},
  author={Qwen Team},
  journal={arXiv preprint arXiv:2505.XXXXX},
  year={2025}
}""",
    "google/gemma-4-27b-it": """@article{gemma4,
  title={Gemma 4 Technical Report},
  author={Gemma Team, Google},
  journal={arXiv preprint arXiv:2505.XXXXX},
  year={2025}
}""",
    "google/gemma-4-9b-it": """@article{gemma4,
  title={Gemma 4 Technical Report},
  author={Gemma Team, Google},
  journal={arXiv preprint arXiv:2505.XXXXX},
  year={2025}
}""",
}


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def print_step(step_num: int, message: str):
    """Imprime un paso del proceso."""
    print(f"\n{'='*60}")
    print(f"  PASO {step_num}: {message}")
    print(f"{'='*60}")


def print_success(message: str):
    """Imprime un mensaje de exito."""
    print(f"  [OK] {message}")


def print_error(message: str):
    """Imprime un mensaje de error."""
    print(f"  [ERROR] {message}", file=sys.stderr)


def print_warning(message: str):
    """Imprime un mensaje de advertencia."""
    print(f"  [WARN] {message}")


def generate_card_data(
    model_name: str,
    base_model: str,
    tags: List[str],
    license_type: str = "apache-2.0",
) -> str:
    """Genera los metadados YAML para el model card."""
    card = {
        "license": license_type,
        "tags": tags + ["transformers", "pytorch", "llama", "fine-tuned"],
        "base_model": base_model,
        "model-index": [
            {
                "name": model_name,
                "results": [],
            }
        ],
        "language": ["es", "en"],
        "datasets": ["custom"],
    }
    return json.dumps(card, indent=2)


def detect_model_type(model_path: str) -> str:
    """Detecta si el modelo es LoRA, completo o quantized."""
    path = Path(model_path)
    
    if not path.exists():
        return "unknown"
    
    files = [f.name for f in path.iterdir() if f.is_file()]
    
    # Detectar LoRA
    lora_indicators = ["adapter_config.json", "adapter_model.safetensors", "lora"]
    if any(indicator in " ".join(files).lower() for indicator in lora_indicators):
        return "lora"
    
    # Detectar GGUF/quantized
    gguf_indicators = [".gguf", "quantized", "q4", "q8"]
    if any(indicator in " ".join(files).lower() for indicator in gguf_indicators):
        return "gguf"
    
    # Detectar modelo completo
    full_indicators = ["model.safetensors", "pytorch_model.bin", "config.json"]
    if any(indicator in files for indicator in full_indicators):
        return "full"
    
    return "unknown"


def get_model_files(model_path: str) -> List[Path]:
    """Obtiene la lista de archivos del modelo a subir."""
    path = Path(model_path)
    if not path.exists():
        print_error(f"La ruta del modelo no existe: {model_path}")
        sys.exit(1)
    
    files = []
    for f in path.rglob("*"):
        if f.is_file():
            # Excluir archivos temporales y de cache
            if not any(part.startswith(".") or part == "__pycache__" for part in f.parts):
                files.append(f)
    
    return files


# ==============================================================================
# FUNCIONES PRINCIPALES
# ==============================================================================

def verify_hf_token(token: str) -> Dict[str, Any]:
    """Verifica que el token de Hugging Face sea valido."""
    try:
        api = HfApi(token=token)
        user_info = whoami(token=token)
        print_success(f"Token valido. Usuario: {user_info.get('name', 'unknown')}")
        return user_info
    except Exception as e:
        print_error(f"Token de Hugging Face invalido: {e}")
        sys.exit(1)


def create_hf_repo(
    api: HfApi,
    repo_id: str,
    repo_type: str = "model",
    private: bool = False,
    exist_ok: bool = True,
) -> str:
    """Crea el repositorio en Hugging Face."""
    try:
        url = create_repo(
            repo_id=repo_id,
            repo_type=repo_type,
            private=private,
            token=api.token,
            exist_ok=exist_ok,
        )
        print_success(f"Repositorio creado/verificado: {url}")
        return url
    except HfHubHTTPError as e:
        if "already exists" in str(e).lower():
            print_warning(f"El repositorio ya existe: {repo_id}")
            return f"https://huggingface.co/{repo_id}"
        print_error(f"Error creando repositorio: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado creando repositorio: {e}")
        sys.exit(1)


def generate_readme(args) -> str:
    """Genera el README.md con atribucion legal correcta."""
    repo_id = f"{args.org_name}/{args.repo_name}" if args.org_name else args.repo_name
    
    card_data = generate_card_data(
        model_name=args.repo_name,
        base_model=args.base_model,
        tags=args.tags or [],
    )
    
    base_model_bibtex = BASE_MODEL_BIBTEX.get(
        args.base_model,
        f"@software{{{args.base_model.split('/')[-1].lower().replace('-', '_')},\n  author = {{{args.base_model_author}}},\n  title = {{{args.base_model}}},\n  year = {{2025}}\n}}"
    )
    
    readme = README_TEMPLATE.format(
        card_data=card_data,
        model_name=args.repo_name,
        model_description=args.model_description,
        base_model=args.base_model,
        base_model_author=args.base_model_author,
        base_model_bibtex=base_model_bibtex,
        derivative_license=args.derivative_license,
        intended_use=args.intended_use,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        num_epochs=args.num_epochs,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        training_framework=args.training_framework,
        training_hardware=args.training_hardware,
        training_time=args.training_time,
        author_name=args.author_name,
        year=datetime.now().year,
        repo_id=repo_id,
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    
    return readme


def generate_license(args) -> str:
    """Genera el archivo LICENSE con Apache 2.0."""
    return APACHE_2_0_LICENSE.format(
        year=datetime.now().year,
        author=args.author_name,
    )


def generate_notice(args) -> str:
    """Genera el archivo NOTICE con atribucion correcta."""
    base_model_name = args.base_model.split("/")[-1]
    
    return NOTICE_TEMPLATE.format(
        model_name=args.repo_name,
        year=datetime.now().year,
        author=args.author_name,
        base_model_name=base_model_name,
        base_model_year=datetime.now().year,
        base_model_author=args.base_model_author,
        base_model=args.base_model,
        training_framework=args.training_framework,
        derivative_license=args.derivative_license,
    )


def upload_model_files(
    api: HfApi,
    repo_id: str,
    model_path: str,
    readme_content: str,
    license_content: str,
    notice_content: str,
    repo_type: str = "model",
) -> bool:
    """Sube los archivos del modelo al repositorio de Hugging Face."""
    
    # Crear directorio temporal con todos los archivos
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Copiar archivos del modelo
        model_files = get_model_files(model_path)
        model_path_obj = Path(model_path)
        
        print(f"  Archivos del modelo a subir: {len(model_files)}")
        
        for file in model_files:
            rel_path = file.relative_to(model_path_obj)
            dest = tmpdir_path / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest)
        
        # Crear README.md
        readme_path = tmpdir_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        print_success("README.md generado con atribucion legal")
        
        # Crear LICENSE
        license_path = tmpdir_path / "LICENSE"
        license_path.write_text(license_content, encoding="utf-8")
        print_success("LICENSE (Apache 2.0) generado")
        
        # Crear NOTICE
        notice_path = tmpdir_path / "NOTICE"
        notice_path.write_text(notice_content, encoding="utf-8")
        print_success("NOTICE generado con atribucion al modelo base")
        
        # Subir todo al repositorio
        try:
            print(f"  Subiendo archivos a {repo_id}...")
            upload_folder(
                repo_id=repo_id,
                repo_type=repo_type,
                folder_path=str(tmpdir_path),
                token=api.token,
                commit_message=f"Upload {args.repo_name} model with legal attribution",
            )
            print_success(f"Archivos subidos exitosamente a {repo_id}")
            return True
        except Exception as e:
            print_error(f"Error subiendo archivos: {e}")
            return False


def verify_upload(api: HfApi, repo_id: str, repo_type: str = "model") -> bool:
    """Verifica que todos los archivos necesarios se subieron correctamente."""
    required_files = ["README.md", "LICENSE", "NOTICE"]
    
    try:
        repo_files = api.list_repo_files(repo_id, repo_type=repo_type, token=api.token)
        repo_filenames = [f for f in repo_files]
        
        print(f"\n  Verificando archivos en {repo_id}:")
        all_ok = True
        
        for required in required_files:
            if required in repo_filenames:
                print_success(f"{required} presente")
            else:
                print_error(f"{required} NO encontrado!")
                all_ok = False
        
        # Verificar que hay archivos del modelo
        model_files = [f for f in repo_filenames if f not in required_files + [".gitattributes"]]
        if model_files:
            print_success(f"Archivos del modelo presentes ({len(model_files)} archivos)")
        else:
            print_warning("No se detectaron archivos del modelo (posiblemente solo metadata)")
        
        return all_ok
    except Exception as e:
        print_error(f"Error verificando repositorio: {e}")
        return False


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Publicar modelo derivado en Hugging Face con cumplimiento legal Apache 2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Publicar LoRA adapters
  python publish_to_huggingface.py \\
      --model_path ./output/lora_adapters \\
      --repo_name CAJAL-v1 \\
      --org_name mi-lab \\
      --base_model Qwen/Qwen3-30B-A3B \\
      --base_model_author "Alibaba Cloud" \\
      --model_description "Modelo especializado en investigacion cientifica" \\
      --hf_token $HF_TOKEN

  # Publicar modelo completo fine-tuned
  python publish_to_huggingface.py \\
      --model_path ./output/finetuned_model \\
      --repo_name CAJAL-Full \\
      --base_model google/gemma-4-9b-it \\
      --base_model_author "Google" \\
      --model_description "Gemma 4 fine-tuned para investigacion" \\
      --private \\
      --hf_token $HF_TOKEN
        """
    )
    
    # Argumentos requeridos
    parser.add_argument("--model_path", required=True, help="Ruta al directorio del modelo a publicar")
    parser.add_argument("--repo_name", required=True, help="Nombre del repositorio en Hugging Face")
    parser.add_argument("--base_model", required=True, help="ID del modelo base en Hugging Face (ej: Qwen/Qwen3-30B-A3B)")
    parser.add_argument("--base_model_author", required=True, help="Autor del modelo base (ej: 'Alibaba Cloud', 'Google')")
    parser.add_argument("--model_description", required=True, help="Descripcion corta del modelo")
    parser.add_argument("--hf_token", required=True, help="Token de Hugging Face (o usa HF_TOKEN env var)")
    
    # Argumentos opcionales - Organizacion
    parser.add_argument("--org_name", default=None, help="Nombre de la organizacion en HF (opcional)")
    parser.add_argument("--private", action="store_true", help="Crear repositorio privado")
    
    # Argumentos opcionales - Detalles del modelo
    parser.add_argument("--intended_use", default="investigacion cientifica y asistencia en analisis de papers", help="Uso previsto del modelo")
    parser.add_argument("--tags", nargs="+", default=[], help="Tags adicionales para el model card")
    parser.add_argument("--author_name", default="CAJAL Team", help="Nombre del autor del modelo derivado")
    parser.add_argument("--derivative_license", default="Apache License 2.0", help="Licencia del modelo derivado")
    
    # Argumentos opcionales - Entrenamiento
    parser.add_argument("--learning_rate", default="2e-4", help="Learning rate usado")
    parser.add_argument("--batch_size", default="4", help="Batch size")
    parser.add_argument("--num_epochs", default="3", help="Numero de epochs")
    parser.add_argument("--lora_rank", default="64", help="LoRA rank")
    parser.add_argument("--lora_alpha", default="128", help="LoRA alpha")
    parser.add_argument("--training_framework", default="Unsloth", help="Framework de entrenamiento")
    parser.add_argument("--training_hardware", default="NVIDIA A100 80GB", help="Hardware de entrenamiento")
    parser.add_argument("--training_time", default="~8 horas", help="Tiempo total de entrenamiento")
    
    # Argumentos opcionales - Comportamiento
    parser.add_argument("--skip_upload", action="store_true", help="Solo generar archivos localmente sin subir")
    parser.add_argument("--output_dir", default=None, help="Directorio de salida para archivos generados (si --skip_upload)")
    
    global args
    args = parser.parse_args()
    
    # Determinar token
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    if not hf_token:
        print_error("Debes proporcionar --hf_token o definir la variable de entorno HF_TOKEN")
        sys.exit(1)
    
    # Construir repo_id
    repo_id = f"{args.org_name}/{args.repo_name}" if args.org_name else args.repo_name
    
    print(f"\n{'#'*60}")
    print(f"#  PUBLICACION DE MODELO DERIVADO - CAJAL")
    print(f"#  Modelo: {args.repo_name}")
    print(f"#  Base: {args.base_model}")
    print(f"#  Repo: https://huggingface.co/{repo_id}")
    print(f"{'#'*60}")
    
    # Paso 1: Verificar token
    print_step(1, "Verificando token de Hugging Face")
    user_info = verify_hf_token(hf_token)
    api = HfApi(token=hf_token)
    
    # Paso 2: Detectar tipo de modelo
    print_step(2, "Detectando tipo de modelo")
    model_type = detect_model_type(args.model_path)
    print_success(f"Tipo de modelo detectado: {model_type}")
    
    # Paso 3: Generar archivos legales
    print_step(3, "Generando archivos legales (README.md, LICENSE, NOTICE)")
    readme_content = generate_readme(args)
    license_content = generate_license(args)
    notice_content = generate_notice(args)
    print_success("Archivos legales generados con atribucion correcta")
    
    # Si solo queremos generar localmente
    if args.skip_upload:
        output_dir = Path(args.output_dir or f"./hf_upload_{args.repo_name}")
        output_dir.mkdir(exist_ok=True)
        
        (output_dir / "README.md").write_text(readme_content, encoding="utf-8")
        (output_dir / "LICENSE").write_text(license_content, encoding="utf-8")
        (output_dir / "NOTICE").write_text(notice_content, encoding="utf-8")
        
        print(f"\n{'='*60}")
        print(f"  ARCHIVOS GENERADOS LOCALMENTE EN: {output_dir}")
        print(f"{'='*60}")
        print(f"  - README.md (con atribucion legal)")
        print(f"  - LICENSE (Apache 2.0)")
        print(f"  - NOTICE (atribucion al modelo base)")
        print(f"\n  Copia estos archivos a tu directorio de modelo y sube manualmente.")
        return
    
    # Paso 4: Crear repositorio
    print_step(4, f"Creando repositorio en Hugging Face: {repo_id}")
    repo_url = create_hf_repo(api, repo_id, private=args.private)
    
    # Paso 5: Subir archivos
    print_step(5, "Subiendo archivos del modelo y documentacion legal")
    success = upload_model_files(
        api=api,
        repo_id=repo_id,
        model_path=args.model_path,
        readme_content=readme_content,
        license_content=license_content,
        notice_content=notice_content,
    )
    
    if not success:
        print_error("Fallo la subida de archivos. Abortando.")
        sys.exit(1)
    
    # Paso 6: Verificar subida
    print_step(6, "Verificando que todos los archivos se subieron correctamente")
    verified = verify_upload(api, repo_id)
    
    # Resumen final
    print(f"\n{'#'*60}")
    print(f"#  PUBLICACION COMPLETADA")
    print(f"{'#'*60}")
    print(f"  Repositorio: https://huggingface.co/{repo_id}")
    print(f"  Tipo: {'Privado' if args.private else 'Publico'}")
    print(f"  Modelo base: {args.base_model}")
    print(f"  Atribucion: Cumplimiento Apache 2.0 incluido")
    print(f"  Archivos legales: README.md, LICENSE, NOTICE")
    print(f"")
    print(f"  {'[OK] Verificacion completada' if verified else '[WARN] Verificacion con problemas'}")
    print(f"{'#'*60}\n")
    
    if not verified:
        sys.exit(1)


if __name__ == "__main__":
    main()
