# 🚢 Proyecto Titanic ML - Predicción de Supervivencia

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC.svg)](https://www.terraform.io/)
[![AWS ECR](https://img.shields.io/badge/Registry-ECR-FF9900.svg)](https://aws.amazon.com/ecr/)
[![SageMaker](https://img.shields.io/badge/ML-SageMaker-FF9900.svg)](https://aws.amazon.com/sagemaker/)

Proyecto completo de Machine Learning para predecir la supervivencia de pasajeros del Titanic, con un pipeline de MLOps que integra **Docker**, **AWS ECR**, **SageMaker Processing** e **infraestructura como código con Terraform**, todo orquestado por **GitHub Actions**.

> [!NOTE]
> **🎯 Proyecto académico de práctica**: Este repositorio fue creado como ejercicio práctico para aprender CI/CD, testing y mejores prácticas en proyectos de Machine Learning.

## 📑 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura del Pipeline](#-arquitectura-del-pipeline)
- [Infraestructura con Terraform](#-infraestructura-con-terraform)
- [Inicio Rápido](#-inicio-rápido)
- [Documentación](#-documentación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Workflows de CI/CD](#-workflows-de-cicd)
- [Testing](#-testing)
- [Modelos Soportados](#-modelos-soportados)
- [Resultados](#-resultados)
- [🎓 Ejercicio para Alumnos](#-ejercicio-para-alumnos)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

### Pipeline de ML Completo

- ✅ **Descarga automática de datos** desde fuentes confiables
- ✅ **Preprocesamiento robusto** con feature engineering
- ✅ **Múltiples modelos** ML (Random Forest, Logistic Regression, Gradient Boosting)
- ✅ **Validación cruzada** para estimación robusta del rendimiento
- ✅ **Evaluación completa** con métricas y visualizaciones

### Ingeniería de Software

- ✅ **Código modular** y reutilizable
- ✅ **Tests unitarios** con pytest (cobertura > 80%)
- ✅ **Linting** con flake8
- ✅ **Type hints** y documentación
- ✅ **Git-friendly** con .gitignore configurado

### CI/CD y MLOps Automatizado

- ✅ **Testing automático** en cada push/PR (flake8 + pytest)
- ✅ **Docker multi-stage** con imágenes separadas para processing y training
- ✅ **Publicación automática** de imágenes a **AWS ECR**
- ✅ **SageMaker Processing Job** lanzado automáticamente en cada push
- ✅ **Infraestructura como código** con Terraform (ECR, IAM roles, políticas)
- ✅ **Artifacts** versionados (modelos, métricas, reportes)

## 🏗️ Arquitectura del Pipeline

```mermaid
graph TD
    subgraph "GitHub Platform"
        Repo["GitHub Repository (Code & Workflows)"]
        Secrets["GitHub Secrets (AWS Credentials)"]
    end

    subgraph "GitHub Actions CI/CD"
        Action1["Docker Build & Publish"]
        Action2["SageMaker Pipeline Runner"]
        Downloader["Python Script: download_data.py"]
    end

    subgraph "AWS Cloud (Infrastructure)"
        ECR["Amazon ECR (Docker Images)"]
        S3["Amazon S3 (Data Bucket)"]
        
        subgraph "Amazon SageMaker"
            ProcJob["Processing Job (Python src/process.py)"]
            TrainJob["Training Job (Python src/train.py)"]
        end
    end

    %% Flow connections
    Repo -->|Trigger| Action1
    Repo -->|Trigger| Action2
    Secrets -.->|Auth| Action1
    Secrets -.->|Auth| Action2

    %% Docker Stage
    Action1 -->|Push Image| ECR

    %% Data Staging
    Action2 --> Downloader
    Downloader -->|CSV files local| Action2
    Action2 -->|Upload raw/| S3

    %% SageMaker Stages
    ECR -->|Pull Image| ProcJob
    ECR -->|Pull Image| TrainJob
    
    S3 <==>|Read Raw / Write Processed| ProcJob
    S3 <==>|Read Processed / Write Models| TrainJob
    
    %% Execution Context
    ProcJob -.->|Failure Report| S3
    TrainJob -.->|Failure Report/Metrics| S3
```

## ☁️ Infraestructura con Terraform

Toda la infraestructura AWS se gestiona con Terraform en el directorio `terraform/`.

### Recursos creados

| Recurso | Nombre | Para qué sirve |
|---|---|---|
| `aws_ecr_repository` | `practica-ci-cd` | Almacena las imágenes Docker |
| `aws_ecr_lifecycle_policy` | — | Mantiene solo las últimas 10 imágenes |
| `aws_iam_user` | `github-actions-ecr-practica-ci-cd` | Usuario que usa GitHub Actions para autenticarse |
| `aws_iam_access_key` | — | Credenciales → secretos de GitHub |
| `aws_iam_role` | `sagemaker-execution-practica-ci-cd` | Rol que SageMaker asume al correr jobs |
| `aws_iam_role_policy` | `sagemaker-s3-policy` | Acceso lectura/escritura al bucket S3 |
| `aws_iam_role_policy` | `sagemaker-ecr-policy` | Pull de imágenes desde ECR |

### Cómo se conecta Terraform con el pipeline

```
Terraform                     GitHub Actions
──────────────────────────    ──────────────────────────────────────
Crea aws_iam_user         →   usa AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
Crea aws_ecr_repository   →   docker-publish.yml sube imágenes aquí
Crea aws_iam_role         →   sagemaker-pipeline.yml pasa el ARN al job
```

### Aplicar la infraestructura

```bash
cd terraform/
terraform init
terraform apply        # Crea todos los recursos en AWS
terraform output       # Muestra URLs, ARNs y credenciales
```

> [!IMPORTANT]
> Después del primer `terraform apply`, copia los outputs `aws_access_key_id` y `aws_secret_access_key` y agrégalos como **Secrets** en GitHub → Settings → Secrets and variables → Actions.

## 🚀 Inicio Rápido

### Opción 1: Usando Docker 🐳 (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/ivhuco/practica_ci_cd.git
cd practica_ci_cd

# Construir y ejecutar con Docker Compose
docker-compose up train evaluate

# O usar Docker directamente
docker build -t titanic-ml:dev .
docker run -it --rm titanic-ml:dev
```

Ver [docs/DOCKER.md](docs/DOCKER.md) para documentación completa de Docker.

### Opción 2: Instalación Local

#### Prerequisitos

- Python 3.9 o superior
- pip
- Git

#### Instalación en 3 Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/ivhuco/practica_ci_cd.git
cd practica_ci_cd

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Ejecutar pipeline completo
python scripts/download_data.py  # Descargar datos
python scripts/run_pipeline.py   # Entrenar y evaluar
```

### Verificación

Si todo funcionó correctamente, deberías ver:

```
✓ Trained model saved in 'models/' directory
✓ Evaluation metrics in 'reports/evaluation_results.json'
✓ Visualizations in 'reports/*.png'
```

## 📚 Documentación

Este proyecto cuenta con documentación completa en español:

### Documentación Principal

| Documento | Descripción |
|-----------|-------------|
| **[📖 README.md](README.md)** | Este archivo - Visión general del proyecto |
| **[🏗️ ARQUITECTURA.md](ARQUITECTURA.md)** | Arquitectura técnica detallada con diagramas |
| **[📚 GUIA_USO.md](GUIA_USO.md)** | Guía paso a paso de instalación y uso |

### Documentación de Módulos

Documentación detallada de cada componente:

- [📦 Data Loader](docs/modulos/DATA_LOADER.md) - Carga y gestión de datos
- [🔧 Preprocessing](docs/modulos/PREPROCESSING.md) - Pipeline de preprocesamiento
- [🤖 Model](docs/modulos/MODEL.md) - Definición y gestión de modelos
- [🎓 Train](docs/modulos/TRAIN.md) - Proceso de entrenamiento
- [📊 Evaluate](docs/modulos/EVALUATE.md) - Evaluación y métricas

### Documentación de Scripts

- [📜 Download Data](docs/scripts/DOWNLOAD_DATA.md) - Descarga del dataset
- [📜 Run Pipeline](docs/scripts/RUN_PIPELINE.md) - Pipeline end-to-end

### Documentación de CI/CD

- [🔄 CI Workflow](docs/ci-cd/WORKFLOW_CI.md) - Testing y linting automático
- [🚂 Train Workflow](docs/ci-cd/WORKFLOW_TRAIN.md) - Entrenamiento automático
- [📈 Evaluate Workflow](docs/ci-cd/WORKFLOW_EVALUATE.md) - Evaluación automática
- [🐳 Docker Workflow](docs/ci-cd/WORKFLOW_DOCKER.md) - Build y publicación de imágenes a ECR
- [🔬 SageMaker Pipeline](docs/ci-cd/WORKFLOW_SAGEMAKER.md) - Processing Job en AWS SageMaker

### Documentación de Docker

- [🐳 Docker Guide](docs/DOCKER.md) - Guía completa de Docker (instalación, uso, troubleshooting)

### Otros

- [🧪 Testing](docs/tests/TESTING.md) - Guía de testing

## 📂 Estructura del Proyecto

```
practica_ci_cd/
├── 📄 README.md                 # Este archivo
├── 📄 ARQUITECTURA.md           # Documentación de arquitectura
├── 📄 GUIA_USO.md              # Guía de uso detallada
├── 📄 requirements.txt          # Dependencias Python
├── 📄 .gitignore               # Archivos ignorados por Git
│
├── 📁 .github/workflows/        # GitHub Actions
│   ├── ci.yml                  # Testing y linting automático
│   ├── docker-publish.yml      # Build y push de imágenes a ECR
│   ├── sagemaker-pipeline.yml  # Lanza SageMaker Processing Job
│   ├── train-model.yml         # Entrenamiento automático (local)
│   └── evaluate-model.yml      # Evaluación automática
│
├── 📁 terraform/                # Infraestructura como código (IaC)
│   ├── main.tf                 # ECR repo + IAM user para GitHub Actions
│   ├── sagemaker_role.tf       # IAM Role para SageMaker + permisos
│   ├── variables.tf            # Variables (región, nombre del repo)
│   └── outputs.tf              # URLs, ARNs y credenciales
│
├── 📁 src/                      # Código fuente principal
│   ├── data_loader.py          # Carga de datos
│   ├── preprocessing.py        # Preprocesamiento y feature engineering
│   ├── process.py              # Entrypoint SageMaker Processing Job
│   ├── model.py                # Definición de modelos
│   ├── train.py                # Entrypoint SageMaker Training Job (🚧)
│   └── evaluate.py             # Script de evaluación
│
├── 📁 scripts/                  # Scripts de utilidad
│   ├── download_data.py        # Descarga del dataset
│   ├── launch_processing_job.py # Lanza job via boto3
│   └── run_pipeline.py         # Pipeline end-to-end (local)
│
├── 📁 tests/                    # Tests unitarios
│   ├── test_preprocessing.py   # Tests del preprocessor
│   └── test_model.py           # Tests del modelo
│
├── 📁 data/                     # Datos (git-ignored)
│   ├── raw/                    # Datos originales
│   └── processed/              # Datos procesados
│
├── 📁 models/                   # Modelos entrenados (git-ignored)
├── 📁 reports/                  # Reportes y métricas
└── 📁 docs/                     # Documentación detallada
    ├── modulos/                # Docs de módulos Python
    ├── scripts/                # Docs de scripts
    ├── ci-cd/                  # Docs de workflows
    └── tests/                  # Docs de testing
```

## 💻 Uso Detallado

### Opción 1: Pipeline Completo (Recomendado)

```bash
# Descargar datos y ejecutar todo el pipeline
python scripts/download_data.py
python scripts/run_pipeline.py
```

### Opción 2: Ejecución Paso a Paso

```bash
# 1. Descargar datos
python scripts/download_data.py

# 2. Entrenar modelo (Random Forest por defecto)
python src/train.py

# 3. Evaluar modelo
python src/evaluate.py --use-test

# 4. Ver resultados
cat reports/evaluation_results.json
open reports/confusion_matrix.png  # macOS
```

### Entrenar Diferentes Modelos

```bash
# Random Forest (por defecto)
python src/train.py --model random_forest --cv-folds 5

# Logistic Regression
python src/train.py --model logistic_regression --cv-folds 5

# Gradient Boosting
python src/train.py --model gradient_boosting --cv-folds 5
```

> [!TIP]
> Para uso avanzado y personalización, consulta [GUIA_USO.md](GUIA_USO.md)

## 🔄 Workflows de CI/CD

### 1. CI - Testing y Linting (`ci.yml`)

**Trigger**: Push o Pull Request a `main` o `develop`

```
Matriz de Python: 3.9, 3.10, 3.11
├── Linting con flake8
├── Tests con pytest + cobertura
└── Upload a Codecov
```

[📖 Documentación detallada](docs/ci-cd/WORKFLOW_CI.md)

---

### 2. Docker Build and Publish (`docker-publish.yml`)

**Trigger**: Push a `main` o tag `v*`

```
├── Construye imagen processing  → ECR :processing-latest, :processing-<sha>
├── Construye imagen train       → ECR :train-latest, :train-<sha>
└── (en tags v*) imagen prod     → ECR :prod-latest
```

Las imágenes se publican en: `421041021233.dkr.ecr.us-east-1.amazonaws.com/practica-ci-cd`

[📖 Documentación detallada](docs/ci-cd/WORKFLOW_DOCKER.md)

---

### 3. SageMaker Processing Pipeline (`sagemaker-pipeline.yml`)

**Trigger**: Automático cuando `docker-publish.yml` termina exitosamente en `main`

```
├── Login a ECR
├── Lanza SageMaker Processing Job
│     ├── Imagen: ECR :processing-latest
│     ├── Input:  s3://practica.mlops.2026/ejemplo.studio/
│     └── Output: s3://practica.mlops.2026/ejemplo.studio/processed/
└── Espera que el job complete (~5-10 min)
```

[📖 Documentación detallada](docs/ci-cd/WORKFLOW_SAGEMAKER.md)

---

### 4. Train Model / Evaluate Model

**Trigger**: Manual o programado

Workflows de CI/CD locales (sin SageMaker) para pruebas rápidas.

[📖 Train](docs/ci-cd/WORKFLOW_TRAIN.md) | [📖 Evaluate](docs/ci-cd/WORKFLOW_EVALUATE.md)

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Con reporte de cobertura
pytest tests/ -v --cov=src --cov-report=html

# Ver reporte HTML
open htmlcov/index.html
```

### Linting

```bash
# Verificar estilo de código
flake8 src/ tests/ --max-line-length=100

# Solo errores críticos
flake8 src/ tests/ --select=E9,F63,F7,F82 --show-source
```

[📖 Guía completa de testing](docs/tests/TESTING.md)

## 🤖 Modelos Soportados

| Modelo | Ventajas | Accuracy típica | Tiempo de entrenamiento |
|--------|----------|-----------------|------------------------|
| **Random Forest** | Alta precisión, interpretable | ~82-84% | Medio (~10s) |
| **Logistic Regression** | Rápido, baseline sólido | ~78-80% | Rápido (~1s) |
| **Gradient Boosting** | Máxima precisión | ~83-85% | Lento (~30s) |

### Features Utilizados

El modelo utiliza las siguientes características:

**Features originales:**

- `Pclass` - Clase del pasajero
- `Sex` - Género
- `Age` - Edad
- `SibSp` - Número de hermanos/cónyuge a bordo
- `Parch` - Número de padres/hijos a bordo
- `Fare` - Tarifa pagada
- `Embarked` - Puerto de embarque

**Features engineered:**

- `FamilySize` - Tamaño total de la familia
- `IsAlone` - Indicador de viaje solo
- `Title` - Título extraído del nombre (Mr, Mrs, Miss, Master, etc.)

[📖 Detalles del preprocesamiento](docs/modulos/PREPROCESSING.md)

## 📊 Resultados

### Métricas de Rendimiento

Resultados típicos del modelo Random Forest:

| Métrica | Valor |
|---------|-------|
| **Accuracy** | 82.68% |
| **Precision** | 80.23% |
| **Recall** | 76.92% |
| **F1-Score** | 78.54% |
| **ROC-AUC** | 87.45% |

### Importancia de Features

Top 5 features más importantes:

1. `Sex` (género) - 25.4%
2. `Title` (título) - 18.7%
3. `Fare` (tarifa) - 15.3%
4. `Age` (edad) - 12.8%
5. `Pclass` (clase) - 11.2%

### Visualizaciones

El proyecto genera automáticamente:

- 📊 **Matriz de Confusión** - Clasificación detallada
- 📈 **Curva ROC** - Rendimiento del clasificador
- 📉 **Importancia de Features** - Peso de cada característica

## 🛠️ Tecnologías Utilizadas

### Core

- **Python 3.9+** - Lenguaje de programación
- **scikit-learn** - Algoritmos de ML
- **pandas** - Manipulación de datos
- **numpy** - Operaciones numéricas

### Visualización

- **matplotlib** - Gráficas
- **seaborn** - Visualizaciones estadísticas

### Testing & Quality

- **pytest** - Framework de testing
- **pytest-cov** - Cobertura de código
- **flake8** - Linting

### CI/CD e Infraestructura

- **GitHub Actions** - Orquestación de workflows
- **Docker** - Contenerización multi-stage
- **Terraform** - Infraestructura como código (IaC)
- **AWS ECR** - Registro de imágenes Docker
- **AWS SageMaker** - Processing Jobs en la nube
- **AWS IAM** - Gestión de permisos
- **boto3** - SDK de AWS para Python

### Otros

- **joblib** - Serialización de modelos

## ✅ Pipeline de Entrenamiento Finalizado

El ejercicio de entrenamiento en SageMaker ha sido completado e integrado en el pipeline automáticamente.

- ✅ **Creación de `scripts/launch_training_job.py`** — Usa `boto3` para disparar el entrenamiento.
- ✅ **Encadenamiento en `sagemaker-pipeline.yml`** — El entrenamiento corre automáticamente tras el procesamiento.
- ✅ **Adaptación de Scripts** — `src/train.py` y `src/model.py` ahora leen y guardan datos en las rutas de SageMaker.
- ✅ **S3 Data Bucket** — Se migró a un bucket propio para evitar problemas de permisos.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Antes de contribuir

- Ejecuta los tests: `pytest tests/ -v`
- Verifica el linting: `flake8 src/ tests/ --max-line-length=100`
- Actualiza la documentación si es necesario

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Ivan Hurtado**

- GitHub: [@ivhuco](https://github.com/ivhuco)
- Repositorio: [practica_ci_cd](https://github.com/ivhuco/practica_ci_cd)

## 🙏 Agradecimientos

- Dataset del Titanic de [Kaggle](https://www.kaggle.com/c/titanic)
- Comunidad de scikit-learn
- GitHub Actions por la infraestructura de CI/CD

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!

**[📖 Ver documentación completa](ARQUITECTURA.md)** | **[🚀 Guía de uso](GUIA_USO.md)** | **[🐛 Reportar un bug](https://github.com/ivhuco/practica_ci_cd/issues)**
