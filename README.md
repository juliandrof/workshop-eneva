<img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/header_workshop_eneva.png">

# Workshop Hands-On Databricks | Eneva

Workshop prático de Databricks personalizado para o time da **Eneva**, com foco em **low-code**: Ingestão, Transformação de Dados, consumo em Linguagem Natural e Visualização — a **Data + AI Platform** de ponta a ponta.

</br>

## Apresentadores

<table>
  <tr>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/juliandro_circle.png" width="150"/><br>
      <strong>Juliandro Figueiró</strong><br>
      <em>Solutions Architect</em><br>
      <em>Databricks</em>
    </td>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/jean_circle.png" width="150"/><br>
      <strong>Jean Ertzogue</strong><br>
      <em>Account Executive</em><br>
      <em>Databricks</em>
    </td>
  </tr>
</table>

</br>

## Ementa do Workshop

| # | Lab | Tópicos | Duração |
| -- | -- | -- | -- |
| 00 | **Setup** | Catálogo compartilhado `workshop_eneva` + schema pessoal (seu nome) | 15 min |
| 01 | **Ingestão de Dados** | Upload manual de CSV/XLSX via Catalog (Create table), camada Bronze | 30 min |
| 02 | **Transformação — LakeFlow Designer** | Silver/Gold, 4 transformações low-code, Data Quality | 40 min |
| 03 | **Genie Space** | Consumo de dados em linguagem natural, instruções customizadas | 30 min |
| 04 | **AI/BI Dashboards** | Visualizações interativas, KPIs, gráficos | 30 min |
|    | **Encerramento** | Considerações finais e perguntas | 15 min |

</br>

## Arquitetura

<p align="center">
  <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/arquitetura.png" alt="Arquitetura — Workshop Eneva" width="100%">
</p>

</br>

## Modelo de Dados

O workshop usa um modelo estrela do **parque gerador da Eneva**: **1 tabela fato**
(`fato_geracao`, com as leituras horárias de geração), **2 dimensões** (`dim_usinas` e
`dim_unidades_geradoras`) e **2 tabelas de enriquecimento** (`enriquecimento_municipios` e
`enriquecimento_fabricantes`), usadas para enriquecer as dimensões durante as transformações
do Lab 2. Todas as tabelas são ingeridas na camada **Bronze** por upload manual (Lab 1).

<p align="center">
  <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/modelo_er.png" alt="Modelo de Dados — Workshop Eneva" width="100%">
</p>

</br>

## Pré-requisitos

| Requisito | Detalhes |
| -- | -- |
| Workspace | Databricks com **Unity Catalog** habilitado |
| Compute | Cluster DBR 14.0+ ou **Serverless** |
| SQL Warehouse | Necessário para Labs 03 (Genie) e 04 (AI/BI) |

### Permissões necessárias por Lab

| Permissão | Recurso | Labs |
| -- | -- | -- |
| `CREATE CATALOG` | `workshop_eneva` (compartilhado — criado uma vez) | 00 |
| `CREATE SCHEMA` | `workshop_eneva.<nome>` (schema pessoal) | 00 |
| `USE CATALOG` / `USE SCHEMA` | Catálogo `workshop_eneva` e schema do participante | Todos |
| `CREATE TABLE` / `SELECT` / `MODIFY` | Tabelas no schema do participante (upload no Lab 1) | Todos |
| `CREATE PIPELINE` / `MANAGE` / `RUN` | Pipeline `pipeline_eneva_<nome>` | 02 |
| `CREATE GENIE` / `USE GENIE` | Genie Space com as tabelas Gold | 03 |
| `CREATE DASHBOARD` | AI/BI Dashboard | 04 |
| `USE CLUSTER` / `ATTACH` | Cluster ou Serverless | Todos |

> **Dica:** O catálogo `workshop_eneva` é **compartilhado** e criado uma única vez (reaproveitado nas próximas execuções). Cada participante trabalha em um **schema com o próprio nome** (`workshop_eneva.<nome>`). O perfil de permissões mais simples é conceder **`ALL PRIVILEGES`** no catálogo `workshop_eneva`, além de acesso a compute, Pipelines, Genie e Dashboards.

</br>

## Estrutura do Projeto

```
workshop-eneva/
│
├── dados/                                # Dados prontos para upload manual (CSV + XLSX)
│   ├── fato_geracao.csv / .xlsx          # FATO: leituras horárias de geração
│   ├── dim_usinas.csv / .xlsx            # Dimensão: usinas
│   ├── dim_unidades_geradoras.csv / .xlsx# Dimensão: unidades geradoras
│   ├── enriquecimento_municipios.csv / .xlsx
│   ├── enriquecimento_fabricantes.csv / .xlsx
│   └── gerar_dados.py                    # Script que (re)gera os arquivos CSV/XLSX
│
├── 00_Setup/
│   └── 00_configuracao_catalogo.py       # Catálogo workshop_eneva + schema pessoal (seu nome)
│
├── 01_Lab_Ingestao/
│   ├── 01a_guia_upload_dados.py          # Guia passo-a-passo do upload manual (Create table)
│   └── 01b_validacao.py                  # Validação das tabelas Bronze ingeridas
│
├── 02_Lab_Transformacao/
│   ├── 02a_guia_lakeflow_designer.py     # Guia visual passo-a-passo do LakeFlow Designer
│   ├── 02b_transformacao_to_do.py        # Pipeline com TO-DOs — 4 transformações (exercício)
│   └── 02c_transformacao_completo.py     # Pipeline completo (referência)
│
├── 03_Lab_Genie/
│   ├── 03a_genie_to_do.py                # Preparação + instruções do Genie — TO-DOs (exercício)
│   └── 03b_genie_completo.py             # Genie completo com instruções curadas (referência)
│
├── 04_Lab_AIBI/
│   ├── 04a_dashboard_to_do.py            # Dashboard com TO-DOs (exercício)
│   └── 04b_dashboard_completo.py         # Dashboard completo com queries (referência)
```

</br>

## Como Começar

### Passo 1: Importar os notebooks (Git folder)

1. No Databricks, vá em **Workspace** > **Users** > seu usuário
2. Clique em **Create** > **Git folder**
3. Cole a **URL do repositório** no campo *Git repository URL* (use o botão de copiar 📋 abaixo):

   ```
   https://github.com/juliandrof/workshop-eneva.git
   ```

4. Confirme em **Create Git folder** — todos os notebooks e a pasta `dados/` serão clonados

### Passo 2: Preparar seu schema pessoal

1. Abra o notebook `00_Setup/00_configuracao_catalogo.py`
2. **Execute a primeira célula** para que o widget **nome_participante** apareça no topo do notebook
3. Preencha o widget **nome_participante** com seu primeiro nome
   > ⚠️ Sem espaços, sem acentos, minúsculo. Ex: `joao`, `maria`, `carlos`
4. Execute as demais células
5. O catálogo compartilhado `workshop_eneva` é criado (ou reaproveitado, se já existir) e o
   seu schema pessoal fica em: `workshop_eneva.<seu_nome>` — é ali que ficarão todas as suas tabelas

### Passo 3: Baixar os dados do workshop

Os dados já estão prontos na pasta [`dados/`](dados/) deste repositório, cada tabela em
**CSV** e **XLSX**. Como você importou o repositório via **Git folder** (Passo 1), os arquivos
já estão no seu Workspace. Para fazer o upload no Lab 1, baixe-os para o seu computador em ZIP:

1. No Databricks, abra **Workspace** e navegue até a sua **Git folder** `workshop-eneva`
2. Clique com o botão direito na pasta **`dados`** (ou no menu **⋮** ao lado dela)
3. Selecione **Export** > **Source file** — o Databricks gera um **arquivo `.zip`** com o conteúdo da pasta
4. Salve o `.zip` no seu computador e **descompacte** (duplo clique no Windows/macOS)
5. Dentro da pasta descompactada estarão os 10 arquivos (5 tabelas × CSV + XLSX):

| Arquivo | Registros | Tipo | Descrição |
| -- | -- | -- | -- |
| `fato_geracao` | 5.832 | **Fato** | Leituras horárias de geração por unidade (72h × 81 unidades) |
| `dim_usinas` | 15 | Dimensão | Usinas termelétricas (gás/carvão) e solares |
| `dim_unidades_geradoras` | 81 | Dimensão | Motores, turbinas e inversores por usina |
| `enriquecimento_municipios` | 9 | Enriquecimento | Região, submercado do SIN e população |
| `enriquecimento_fabricantes` | 7 | Enriquecimento | País, eficiência e disponibilidade de referência |

> **Alternativa:** na página do repositório no GitHub, clique em **Code** > **Download ZIP** e
> descompacte — os arquivos ficam na subpasta `dados/`.

> Para **regenerar** os arquivos, rode `python3 dados/gerar_dados.py`.

</br>

---

## Lab 01 — Ingestão de Dados

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Ingerir os 5 arquivos (CSV/XLSX) na camada Bronze via **upload manual** |
| **Guia de upload** | `01_Lab_Ingestao/01a_guia_upload_dados.py` |
| **Notebook de validação** | `01_Lab_Ingestao/01b_validacao.py` |
| **Dados** | pasta [`dados/`](dados/) — 5 tabelas em CSV e XLSX |

### Instruções

1. **Suba cada arquivo** da pasta `dados/` para o **seu schema** (`workshop_eneva.<seu_nome>`):
   1. No menu lateral, abra **Catalog** > `workshop_eneva` > schema **`<seu_nome>`**
   2. Clique em **Create** > **Create table** (Upload files)
   3. Arraste o arquivo (ex.: `fato_geracao.csv`), mantenha **First row = header**
   4. **Table name** = nome do arquivo (ex.: `fato_geracao`) → **Create table**
   5. Repita para os 5 arquivos

| Arquivo | Tabela resultante |
| -- | -- |
| `fato_geracao.csv` / `.xlsx` | `workshop_eneva.<nome>.fato_geracao` |
| `dim_usinas.csv` / `.xlsx` | `workshop_eneva.<nome>.dim_usinas` |
| `dim_unidades_geradoras.csv` / `.xlsx` | `workshop_eneva.<nome>.dim_unidades_geradoras` |
| `enriquecimento_municipios.csv` / `.xlsx` | `workshop_eneva.<nome>.enriquecimento_municipios` |
| `enriquecimento_fabricantes.csv` / `.xlsx` | `workshop_eneva.<nome>.enriquecimento_fabricantes` |

2. **Valide** a ingestão executando `01b_validacao.py` (confere as 5 tabelas)

### Conceitos abordados
- Upload manual de arquivos (CSV / Excel) no Databricks
- Catalog Explorer > Create table
- Inferência de schema e tipos
- Camada Bronze (Medallion Architecture)

</br>

---

## Lab 02 — Transformação com LakeFlow Designer

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Construir as camadas Silver e Gold com **4 transformações** no LakeFlow Designer |
| **Guia visual** | `02_Lab_Transformacao/02a_guia_lakeflow_designer.py` |
| **Notebook (exercício)** | `02_Lab_Transformacao/02b_transformacao_to_do.py` |
| **Notebook (referência)** | `02_Lab_Transformacao/02c_transformacao_completo.py` |

### As 4 transformações

| # | Transformação | Camada | O que faz |
| -- | -- | -- | -- |
| 1 | **Limpeza + Tempo** | Silver | Cast de tipos, extração de ano/mês/dia/hora/**turno** e Data Quality (descarta leituras inválidas) |
| 2 | **Enriquecimento de Usinas** | Silver | Join de `dim_usinas` com `enriquecimento_municipios` → região + submercado do SIN + população |
| 3 | **Fator de Capacidade** | Silver | Join com `enriquecimento_fabricantes` e cálculo de `fator_capacidade` vs referência do fabricante |
| 4 | **Ranking com Janela** | Gold | Agregação por usina + `row_number()` (ranking) + `% de participação` na matriz |

### Instruções

1. **Leia o guia visual** `02a_guia_lakeflow_designer.py` — passo a passo no Designer
2. **Complete os TO-DOs** no notebook `02b_transformacao_to_do.py` (ou monte visualmente no Designer)
3. **Crie o pipeline (LakeFlow / SDP)**:
   1. Vá em **Jobs & Pipelines** > **ETL pipeline**
   2. **Pipeline name**: `pipeline_eneva_<seu_nome>`
   3. **Source code**: selecione `02c_transformacao_completo.py` (ou `02b_transformacao_to_do.py`)
   4. **Target catalog**: `workshop_eneva`
   5. **Target schema**: `<seu_nome>` (o mesmo do Lab 1)
   6. Em **Configuration**, adicione: Key `pipeline.nome_participante` → Value `<seu_nome>`
   7. **Compute**: Serverless (recomendado)
   8. Clique em **Create** e depois em **Start**

### Conceitos abordados
- LakeFlow Designer (low-code / no-code)
- Spark Declarative Pipelines (SDP)
- Cast de tipos, `join`, funções de janela (`window`)
- Data Quality Expectations
- Medallion Architecture (Silver / Gold)

</br>

---

## Lab 03 — Genie Space

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Criar e curar uma Genie Space para consultar a geração em linguagem natural |
| **Notebook (exercício)** | `03_Lab_Genie/03a_genie_to_do.py` |
| **Notebook (referência)** | `03_Lab_Genie/03b_genie_completo.py` |

### Instruções

1. **Complete os TO-DOs** no notebook `03a_genie_to_do.py`:

| TO-DO | Descrição |
| -- | -- |
| 1 | Criar view `vw_desempenho_usinas` |
| 2 | Adicionar **comentários** às tabelas Gold |
| 3 | Adicionar **comentários** em colunas-chave |
| 4 | Revisar as **instruções customizadas** do Genie |

2. **Crie a Genie Space**: **Genie** > **New** > adicione as tabelas Gold e views
3. **Cole as instruções customizadas** (contexto Eneva + glossário do setor elétrico)
4. **Teste o Genie** com perguntas como:
   - *"Qual usina gerou mais energia no período?"*
   - *"Qual a participação de cada fonte na matriz de geração?"*
   - *"Compare a geração de gás natural com a de carvão mineral"*
   - *"Qual submercado do SIN concentra mais geração?"*

### Conceitos abordados
- AI/BI Genie (linguagem natural)
- Instruções customizadas e glossário de domínio
- Curadoria de metadados (comentários de tabela/coluna)
- Sample Questions

</br>

---

## Lab 04 — AI/BI Dashboards

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Criar um AI/BI Dashboard interativo sobre a geração do parque Eneva |
| **Notebook (exercício)** | `04_Lab_AIBI/04a_dashboard_to_do.py` |
| **Notebook (referência)** | `04_Lab_AIBI/04b_dashboard_completo.py` |

### Instruções

1. **Complete os TO-DOs** no notebook `04a_dashboard_to_do.py` (queries de submercado e turno)
2. **Crie o Dashboard**: **Dashboards** > **Create dashboard**
3. **Crie um dataset** para cada query e monte os widgets seguindo o layout de referência
4. **Explore** os filtros e a interatividade

### Layout de referência

<p align="center">
  <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/dashboard_layout.png" alt="Layout do Dashboard — Workshop Eneva" width="100%">
</p>

| Dataset | Tipo de Visualização |
| -- | -- |
| KPI - Resumo Geral | Counter (4 counters) |
| Geração por Fonte | Pie Chart |
| Ranking de Usinas | Bar Chart (horizontal) |
| Geração por Submercado | Bar Chart |
| Geração por Turno | Bar Chart (agrupado por fonte) |
| Disponibilidade por Usina | Table |

### Conceitos abordados
- AI/BI Dashboards
- Datasets (queries SQL)
- Visualizações: Counter, Bar, Pie, Table
- Interatividade e filtros

</br>

---

## Dicas Importantes

> **Use sempre o mesmo `nome_participante`** em todos os notebooks para garantir que seu catálogo seja consistente.

> **Se travar em algum TO-DO**, consulte a versão completa do notebook (sufixo `_completo.py`).

> **No Lab 1**, use exatamente os nomes de arquivo como nome de tabela (ex.: `fato_geracao`) — os notebooks dos labs seguintes dependem desses nomes.

</br>

## Limpeza (Pós-Workshop)

```sql
-- Substitua <seu_nome> pelo nome usado no workshop.
-- Apague apenas o SEU schema — o catálogo workshop_eneva é compartilhado.
DROP SCHEMA IF EXISTS workshop_eneva.<seu_nome> CASCADE;
```

</br>

## Referências

* [Documentação LakeFlow / Spark Declarative Pipelines](https://docs.databricks.com/delta-live-tables/index.html)
* [LakeFlow Designer](https://docs.databricks.com/ingestion/lakeflow-designer/index.html)
* [Criar tabela via upload de arquivo](https://docs.databricks.com/ingestion/add-data/upload-data.html)
* [AI/BI Genie](https://docs.databricks.com/genie/index.html)
* [AI/BI Dashboards](https://docs.databricks.com/dashboards/index.html)
* [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)

</br>

---

<p align="center">
  <img src="https://raw.githubusercontent.com/juliandrof/workshop-eneva/main/images/databricks_logo.png" height="45" alt="Databricks">
</p>

<p align="center">
  <strong>Workshop Hands-On Databricks — Eneva</strong><br>
  <em>Data & AI na prática</em>
</p>
