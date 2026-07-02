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
| 00 | **Setup** | Configuração do catálogo personalizado e geração de dados sintéticos | 15 min |
| 01 | **Ingestão de Dados** | Auto Loader, ingestão incremental, camada Bronze | 30 min |
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
(`silver_geracao`, com as leituras horárias de geração), **2 dimensões** (`dim_usinas` e
`dim_unidades_geradoras`) e **2 tabelas de enriquecimento** (`enriquecimento_municipios` e
`enriquecimento_fabricantes`), usadas para enriquecer as dimensões durante as transformações
do Lab 2.

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
| `CREATE CATALOG` | `workshop_eneva_<nome>` | 00 |
| `CREATE SCHEMA` | `raw`, `bronze`, `silver`, `gold` | 00 |
| `USE CATALOG` / `USE SCHEMA` | Catálogo e schemas do participante | Todos |
| `CREATE TABLE` / `SELECT` / `MODIFY` | Tabelas em todos os schemas | Todos |
| `CREATE VOLUME` / `READ` / `WRITE` | Volume `raw.geracao_json` | 00, 01 |
| `CREATE PIPELINE` / `MANAGE` / `RUN` | Pipeline `pipeline_eneva_<nome>` | 02 |
| `CREATE GENIE` / `USE GENIE` | Genie Space com tabelas Gold | 03 |
| `CREATE DASHBOARD` | AI/BI Dashboard | 04 |
| `USE CLUSTER` / `ATTACH` | Cluster ou Serverless | Todos |

> **Dica:** O perfil de permissões mais simples é conceder **`USE CATALOG`** + **`ALL PRIVILEGES`** no catálogo pessoal do participante, além de acesso a compute e às funcionalidades de Pipelines, Genie e Dashboards.

</br>

## Estrutura do Projeto

```
workshop-eneva/
│
├── 00_Setup/
│   ├── 00_configuracao_catalogo.py       # Criação do catálogo personalizado + schemas + volume
│   └── 01_dados_cadastrais.py            # Geração das 4 tabelas cadastrais (dimensões + enriquecimento)
│
├── 01_Lab_Ingestao/
│   ├── 01a_gerador_geracao_streaming.py  # Gerador de JSONs de geração (1 por usina a cada ciclo)
│   ├── 01b_ingestao_to_do.py             # Ingestão com Auto Loader — TO-DOs (exercício)
│   └── 01c_ingestao_completo.py          # Ingestão completa (referência)
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

### Passo 1: Importar os notebooks

1. No Databricks, vá em **Workspace** > **Users** > seu usuário
2. Clique em **Import** > selecione **URL** e cole o link deste repositório
3. Ou clone via Git: `Repos` > `Add Repo` > cole a URL do GitHub

### Passo 2: Configurar seu catálogo personalizado

1. Abra o notebook `00_Setup/00_configuracao_catalogo.py`
2. Preencha o widget **nome_participante** com seu primeiro nome
   > ⚠️ Sem espaços, sem acentos, minúsculo. Ex: `joao`, `maria`, `carlos`
3. Execute todas as células
4. Seu catálogo será criado como: `workshop_eneva_<seu_nome>`

### Passo 3: Gerar dados cadastrais

1. Abra o notebook `00_Setup/01_dados_cadastrais.py`
2. Use o **mesmo nome** do Passo 2
3. Execute todas as células
4. Verifique no **Catalog Explorer**:

| Tabela | Registros | Tipo | Descrição |
| -- | -- | -- | -- |
| `dim_usinas` | 15 | Dimensão | Usinas termelétricas (gás/carvão) e solares |
| `dim_unidades_geradoras` | ~60 | Dimensão | Motores, turbinas e inversores por usina |
| `enriquecimento_municipios` | 9 | Enriquecimento | Região, submercado do SIN e população |
| `enriquecimento_fabricantes` | 7 | Enriquecimento | País, eficiência e disponibilidade de referência |

> A **tabela fato** (`silver_geracao`) não é criada aqui — as leituras chegam em
> **streaming** no Lab 1 e são transformadas no Lab 2.

</br>

---

## Lab 01 — Ingestão de Dados

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Ingerir leituras de geração via Auto Loader e materializar a camada Bronze |
| **Notebook (exercício)** | `01_Lab_Ingestao/01b_ingestao_to_do.py` |
| **Notebook (referência)** | `01_Lab_Ingestao/01c_ingestao_completo.py` |
| **Gerador de dados** | `01_Lab_Ingestao/01a_gerador_geracao_streaming.py` |

### Instruções

1. **Inicie o gerador de dados** — execute `01a_gerador_geracao_streaming.py` e **deixe rodando**
2. **Complete os TO-DOs** no notebook `01b_ingestao_to_do.py`:

| TO-DO | Descrição | Dica |
| -- | -- | -- |
| 1 | Completar a leitura com **Auto Loader** (`cloudFiles`) | Use `.option("cloudFiles.format", "json")` + `.schema()` + `.load()` |
| 2 | Ingerir `dim_unidades_geradoras` → `bronze_unidades` | Siga o padrão de `bronze_usinas` |
| 3 | Ingerir as **2 tabelas de enriquecimento** para Bronze | `bronze_municipios` e `bronze_fabricantes` |

3. **Verifique** a camada Bronze com a célula de verificação ao final do notebook

### Conceitos abordados
- Auto Loader / CloudFiles
- Ingestão incremental e *exactly-once*
- Schema Enforcement
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
| 1 | **Explode + Tempo** | Silver | "Explode" o array de leituras em linhas e extrai ano/mês/dia/hora/**turno** |
| 2 | **Enriquecimento de Usinas** | Silver | Join de `bronze_usinas` com `bronze_municipios` → região + submercado do SIN + população |
| 3 | **Fator de Capacidade** | Silver | Join com `bronze_fabricantes` e cálculo de `fator_capacidade` vs referência do fabricante |
| 4 | **Ranking com Janela** | Gold | Agregação por usina + `row_number()` (ranking) + `% de participação` na matriz |

### Instruções

1. **Leia o guia visual** `02a_guia_lakeflow_designer.py` — passo a passo no Designer
2. **Complete os TO-DOs** no notebook `02b_transformacao_to_do.py` (ou monte visualmente no Designer)
3. **Crie o pipeline (LakeFlow / SDP)**:
   1. Vá em **Jobs & Pipelines** > **ETL pipeline**
   2. **Pipeline name**: `pipeline_eneva_<seu_nome>`
   3. **Source code**: selecione `02c_transformacao_completo.py` (ou `02b_transformacao_to_do.py`)
   4. **Target catalog**: `workshop_eneva_<seu_nome>`
   5. **Target schema**: `default` (obrigatório na UI)
   6. Em **Configuration**, adicione: Key `pipeline.nome_participante` → Value `<seu_nome>`
   7. **Compute**: Serverless (recomendado)
   8. Clique em **Create** e depois em **Start**

### Conceitos abordados
- LakeFlow Designer (low-code / no-code)
- Spark Declarative Pipelines (SDP)
- `explode`, `join`, funções de janela (`window`)
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

> **O gerador de geração** precisa ficar rodando durante o Lab 1. Para gerar mais dados, execute-o novamente.

</br>

## Limpeza (Pós-Workshop)

```sql
-- Substitua <seu_nome> pelo nome usado no workshop
DROP CATALOG IF EXISTS workshop_eneva_<seu_nome> CASCADE;
```

</br>

## Referências

* [Documentação LakeFlow / Spark Declarative Pipelines](https://docs.databricks.com/delta-live-tables/index.html)
* [LakeFlow Designer](https://docs.databricks.com/ingestion/lakeflow-designer/index.html)
* [Auto Loader](https://docs.databricks.com/ingestion/auto-loader/index.html)
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
