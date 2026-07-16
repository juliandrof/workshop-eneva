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
| 01 | **Ingestão de Dados** | Upload manual de arquivos (CSV + Excel) via Catalog (Create table), camada Bronze | 30 min |
| 02 | **Transformação — LakeFlow Designer** | Visual data prep (no-code): Silver/Gold, 3 transformações | 40 min |
| 03 | **Genie Agent** | Consumo de dados em linguagem natural, instruções customizadas | 30 min |
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
| `CREATE TABLE` / `SELECT` / `MODIFY` | Tabelas no schema do participante (upload no Lab 1, saídas do Lab 2) | Todos |
| `CREATE GENIE` / `USE GENIE` | Genie Agent com as tabelas Gold | 03 |
| `CREATE DASHBOARD` | AI/BI Dashboard | 04 |
| `USE CLUSTER` / `ATTACH` | Cluster ou Serverless | Todos |

> **Dica:** O catálogo `workshop_eneva` é **compartilhado** e criado uma única vez (reaproveitado nas próximas execuções). Cada participante trabalha em um **schema com o próprio nome** (`workshop_eneva.<nome>`). O perfil de permissões mais simples é conceder **`ALL PRIVILEGES`** no catálogo `workshop_eneva`, além de acesso a compute, Pipelines, Genie e Dashboards.

</br>

## Estrutura do Projeto

```
workshop-eneva/
│
├── dados/                                # Dados prontos para upload manual
│   ├── fato_geracao.csv                  # FATO: leituras horárias de geração (CSV)
│   ├── dim_usinas.xlsx                    # Dimensão: usinas (Excel)
│   ├── dim_unidades_geradoras.xlsx       # Dimensão: unidades geradoras (Excel)
│   ├── enriquecimento_municipios.xlsx    # Enriquecimento: municípios (Excel)
│   ├── enriquecimento_fabricantes.xlsx   # Enriquecimento: fabricantes (Excel)
│   └── gerar_dados.py                    # Script que (re)gera os arquivos de dados
│
├── 00_Setup/
│   └── 00_configuracao_catalogo.py       # Catálogo workshop_eneva + schema pessoal (seu nome)
│
├── 01_Lab_Ingestao/
│   ├── 01a_guia_upload_dados.py          # Guia passo-a-passo do upload manual (Create table)
│   └── 01b_validacao.py                  # Validação das tabelas Bronze ingeridas
│
├── 02_Lab_Transformacao/
│   └── 02a_guia_lakeflow_designer.py     # Resumo de apoio (passo a passo completo no README)
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

Os dados já estão prontos na pasta [`dados/`](dados/) deste repositório: a **tabela fato** em
**CSV** e as **dimensões/enriquecimento** em **XLSX** (Excel). Como você importou o repositório
via **Git folder** (Passo 1), os arquivos já estão no seu Workspace. Para fazer o upload no
Lab 1, baixe-os para o seu computador em ZIP:

1. No Databricks, abra **Workspace** e navegue até a sua **Git folder** `workshop-eneva`
2. **Selecione a pasta `dados`**
3. Clique nos **três pontos (⋮)** no lado direito
4. Selecione **Download as** > **Zip - Source**
5. Salve o `.zip` no seu computador e **descompacte** (duplo clique no Windows/macOS)
6. Dentro da pasta descompactada estarão os 5 arquivos de dados:

| Arquivo | Formato | Registros | Tipo | Descrição |
| -- | -- | -- | -- | -- |
| `fato_geracao.csv` | CSV | 5.832 | **Fato** | Leituras horárias de geração por unidade (72h × 81 unidades) |
| `dim_usinas.xlsx` | XLSX | 15 | Dimensão | Usinas termelétricas (gás/carvão) e solares |
| `dim_unidades_geradoras.xlsx` | XLSX | 81 | Dimensão | Motores, turbinas e inversores por usina |
| `enriquecimento_municipios.xlsx` | XLSX | 9 | Enriquecimento | Região, submercado do SIN e população |
| `enriquecimento_fabricantes.xlsx` | XLSX | 7 | Enriquecimento | País, eficiência e disponibilidade de referência |

> **Alternativa:** na página do repositório no GitHub, clique em **Code** > **Download ZIP** e
> descompacte — os arquivos ficam na subpasta `dados/`.

> Para **regenerar** os arquivos, rode `python3 dados/gerar_dados.py`.

</br>

---

## Lab 01 — Ingestão de Dados

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Ingerir os 5 arquivos (fato em CSV, dimensões em Excel) na camada Bronze via **upload manual** |
| **Guia de upload** | `01_Lab_Ingestao/01a_guia_upload_dados.py` |
| **Notebook de validação** | `01_Lab_Ingestao/01b_validacao.py` |
| **Dados** | pasta [`dados/`](dados/) — 5 tabelas (1 CSV + 4 XLSX) |

### Instruções

1. **Suba cada arquivo** da pasta `dados/` para o **seu schema** (`workshop_eneva.<seu_nome>`):
   1. No menu lateral, abra **Catalog** > `workshop_eneva` > schema **`<seu_nome>`**
   2. Clique em **Create** > **Create table** (Upload files)
   3. Arraste o arquivo (ex.: `fato_geracao.csv`), mantenha **First row = header**
   4. **Table name** = nome do arquivo sem a extensão (ex.: `fato_geracao`) → **Create table**
   5. Repita para os 5 arquivos

| Arquivo | Tabela resultante |
| -- | -- |
| `fato_geracao.csv` | `workshop_eneva.<nome>.fato_geracao` |
| `dim_usinas.xlsx` | `workshop_eneva.<nome>.dim_usinas` |
| `dim_unidades_geradoras.xlsx` | `workshop_eneva.<nome>.dim_unidades_geradoras` |
| `enriquecimento_municipios.xlsx` | `workshop_eneva.<nome>.enriquecimento_municipios` |
| `enriquecimento_fabricantes.xlsx` | `workshop_eneva.<nome>.enriquecimento_fabricantes` |

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
| **Objetivo** | Construir as camadas Silver e Gold com **3 transformações** no LakeFlow Designer |
| **Passo a passo** | Detalhado abaixo neste README |
| **Notebook de apoio** | `02_Lab_Transformacao/02a_guia_lakeflow_designer.py` (resumo + verificação) |

### As 3 transformações

| # | Transformação | Camada | O que faz |
| -- | -- | -- | -- |
| 1 | **Enriquecimento de Usinas** | Silver | Join de `dim_usinas` com `enriquecimento_municipios` → região + submercado do SIN + população |
| 2 | **Fator de Capacidade** | Silver | Join com `enriquecimento_fabricantes` e cálculo de `fator_capacidade` vs referência do fabricante |
| 3 | **Ranking com Janela** | Gold | Agregação por usina + `row_number()` (ranking) + `% de participação` na matriz |

> Antes das transformações, há um passo simples de **preparação** (`silver_geracao`): derivar as
> colunas de tempo (`ano/mês/dia/hora/turno`) e aplicar um **Filter** de qualidade.

### Passo a passo — LakeFlow Designer (visual, recomendado)

#### 1. Abrir o LakeFlow Designer (Visual data prep)

1. Na **barra lateral esquerda**, clique no ícone **+ (New)**
2. Selecione **Visual data prep**
3. Abre o **canvas** em branco com a tela de boas-vindas

> O rascunho é salvo automaticamente. Renomeie no topo para `visual_prep_eneva_<seu_nome>`.

#### 2. Adicionar as fontes de dados (operador Source)

Para cada tabela que você ingeriu no Lab 1:

1. Clique em **Select a source** (ou, em **operadores**, no menu da esquerda, escolha **Source**)
2. Na aba de configuração, escolha **Browse** e selecione a tabela existente em
   `workshop_eneva` > `<seu_nome>`
3. Repita para as **5 tabelas** de entrada: `fato_geracao`, `dim_usinas`,
   `dim_unidades_geradoras`, `enriquecimento_municipios`, `enriquecimento_fabricantes`

#### 3. Usar o Genie Code (assistente em linguagem natural)

O LakeFlow Designer tem o **Genie Code** — uma barra onde você **descreve em português** o que
quer fazer e ele cria a transformação para você. É assim que vamos montar cada etapa, **sem
escrever código**.

Como usar, para cada etapa abaixo:

1. No canvas do Visual data prep, abra a barra do **Genie Code**
2. **Cole o prompt** da etapa (use o botão de copiar 📋 nas caixas abaixo)
3. Use o botão **@** para **mencionar as tabelas** citadas no prompt (ex.: `@fato_geracao`) —
   assim o Genie sabe exatamente de quais dados você fala
4. Envie e revise a etapa gerada; se estiver de acordo, **aceite** para adicioná-la ao fluxo
5. Confira a **prévia dos dados** no painel inferior

> Dica: se o resultado não sair como esperado, ajuste o texto do prompt e envie de novo — é uma
> conversa. Você pode iniciar um novo tópico a qualquer momento.

#### 4. Preparação — `silver_geracao` (tempo + qualidade)

**Source:** `fato_geracao` — comece adicionando esta tabela com o operador **Source**.

Prompt para o **Genie Code**:

```text
Usando a tabela @fato_geracao, crie uma nova tabela chamada silver_geracao com:
- colunas de tempo derivadas de data_hora: ano, mês, dia e hora
- uma coluna "turno" a partir da hora: 6 às 11 = "Manhã", 12 às 17 = "Tarde",
  18 às 23 = "Noite" e o restante = "Madrugada"
- mantenha apenas as linhas em que geracao_mwh é maior ou igual a zero e
  disponibilidade está entre 0 e 1
```

#### 5. As 3 transformações

As camadas são identificadas pelo **prefixo** do nome da tabela de saída (`silver_*`, `gold_*`),
todas no seu schema `workshop_eneva.<seu_nome>`. Descreva cada uma no **Genie Code**.

**Transformação 1 — `silver_usinas`** · **Sources:** `dim_usinas` e `enriquecimento_municipios`

```text
Junte @dim_usinas com @enriquecimento_municipios pelas colunas municipio e uf,
trazendo regiao, submercado_sin e populacao. Adicione uma coluna idade_anos igual
ao ano atual menos ano_operacao. Salve o resultado como silver_usinas.
```

**Transformação 2 — `silver_desempenho_unidades`**
· **Sources:** `silver_geracao`, `dim_unidades_geradoras` e `enriquecimento_fabricantes`

```text
A partir de @silver_geracao, calcule por unidade geradora (id_unidade, id_usina) a
geração média (geracao_media_mwh), a geração total (geracao_total_mwh), a
disponibilidade média e a quantidade de leituras. Junte com @dim_unidades_geradoras
(por id_unidade e id_usina) e com @enriquecimento_fabricantes (por fabricante).
Adicione o fator_capacidade = geracao_media_mwh dividido pela potencia_nominal_mw e
o gap_vs_referencia = fator_capacidade menos fator_disponibilidade_ref, ambos
arredondados com 4 casas. Salve como silver_desempenho_unidades.
```

**Transformação 3 — `gold_geracao_por_usina`**
· **Sources:** `silver_geracao` e `silver_usinas`

```text
A partir de @silver_geracao, some a geração por usina (geracao_total_mwh), calcule a
disponibilidade média e o consumo de combustível total. Junte com @silver_usinas
para trazer nome_usina, fonte, combustivel, uf, regiao, submercado_sin e
potencia_instalada_mw. Crie um ranking das usinas da maior para a menor geração e uma
coluna pct_participacao com o percentual de cada usina no total gerado. Salve como
gold_geracao_por_usina.
```

**Tabelas Gold adicionais** (usadas nos Labs 3 e 4) · **Sources:** `silver_geracao` e `silver_usinas`

```text
A partir de @silver_geracao (juntando com @silver_usinas para obter fonte e
combustivel), agrupe por fonte e combustivel somando a geração total, a geração média,
a quantidade de usinas distintas e a disponibilidade média. Salve como
gold_geracao_por_fonte.
```

```text
A partir de @silver_geracao (juntando com @silver_usinas para obter submercado_sin e
regiao), agrupe por submercado_sin e regiao somando a geração total, a quantidade de
usinas distintas, a quantidade de estados distintos e a disponibilidade média. Salve
como gold_geracao_por_submercado.
```

#### 6. Pré-visualizar os resultados

- Clique em qualquer operador para ver a **prévia dos dados** no painel inferior
- Use o seletor **Rows scanned** para controlar o volume processado na prévia

#### 7. Publicar cada saída (operador Output) e executar

Cada prompt do Genie Code já gera a tabela de saída indicada. Confirme que cada resultado
(Silver e Gold) tem um operador **Output** apontando para o seu schema:

1. Adicione um operador **Output** ligado ao último operador da transformação
2. Configure:
   - **Table name**: ex. `silver_geracao`, `gold_geracao_por_usina`, …
   - **Output location**: catálogo `workshop_eneva` + schema `<seu_nome>`
3. Clique em **Run** — cada execução **cria ou substitui** a tabela gerenciada
4. (Opcional) Clique em **Schedule** para agendar execuções recorrentes

> O Designer mostra o **grafo de linhagem** (lineage) entre as tabelas automaticamente.

### Conceitos abordados
- LakeFlow Designer (Visual data prep — low-code / no-code)
- **Genie Code**: construir transformações em linguagem natural (prompts)
- Enriquecimento (join), agregações e ranking
- Qualidade de dados (descarte de linhas inválidas)
- Medallion Architecture (Silver / Gold)

</br>

---

## Lab 03 — Genie Agent

| Item | Detalhes |
| -- | -- |
| **Objetivo** | Criar e curar uma Genie Agent para consultar a geração em linguagem natural |
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

2. **Crie a Genie Agent**: **Genie** > **New** > adicione as tabelas Gold e views
3. **Cole as instruções customizadas** no campo **Instructions** da Genie (contexto Eneva +
   glossário do setor elétrico) — copie o texto abaixo:

   ```text
   ## Contexto do Negócio
   Você é um assistente de análise de dados da Eneva, uma das maiores empresas privadas de
   geração de energia do Brasil, com foco em geração termelétrica a gás natural e carvão, além
   de usinas solares. Os dados representam a geração horária das unidades geradoras do parque
   gerador da Eneva.

   ## Glossário (jargão do setor)
   - MWh: megawatt-hora, unidade de energia gerada no período.
   - Fonte: tipo de geração — "Termelétrica" ou "Solar".
   - Combustível: insumo da usina — "Gás Natural", "Carvão Mineral" ou "Fotovoltaica".
   - SIN: Sistema Interligado Nacional. O Brasil é dividido em submercados
     (Norte, Nordeste, Sudeste/Centro-Oeste, Sul) além de sistemas isolados (ex.: Manaus).
   - Fator de capacidade: razão entre geração média e potência nominal (0 a 1).
   - Disponibilidade: fração do tempo em que a unidade esteve apta a gerar (0 a 1).
   - Despacho: acionamento de uma usina pelo ONS para gerar energia.

   ## Regras de Resposta
   - Sempre expresse energia em MWh e potência em MW, com separador de milhar.
   - Percentuais com uma casa decimal (ex.: 12,5%).
   - Quando perguntarem por "maior/melhor usina", use geracao_total_mwh como métrica padrão.
   - "Participação na matriz" = coluna pct_participacao de gold_geracao_por_usina.
   - Usinas solares só geram durante o dia — geração noturna zero é esperada, não é erro.
   - Ao comparar térmica vs solar, deixe claro que são perfis de geração diferentes.

   ## Exemplos de Perguntas
   - "Qual usina gerou mais energia no período?"
   - "Qual a participação de cada fonte na matriz de geração?"
   - "Compare a geração de Gás Natural com a de Carvão Mineral."
   - "Qual submercado do SIN concentra mais geração?"
   - "Qual a disponibilidade média das usinas termelétricas?"
   - "Quanto gás natural foi consumido no total?"
   - "Quais usinas têm fator de capacidade abaixo da referência do fabricante?"
   - "Como varia a geração solar ao longo dos turnos do dia?"
   ```

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
