# Pipeline de Limpeza e Integração de Dados
**Autores:** Esdras Uday, Caue Reis, Baruc Nunes, Ana Soares  
**Data:** 03/10/2025

## 1. Objetivo do Projeto

Este projeto demonstra um pipeline completo para limpeza, transformação, integração e visualização de dados de vendas de uma empresa. O objetivo é consolidar quatro fontes de dados distintas (`clientes`, `vendas`, `produtos` e `avaliacoes`) em um único conjunto de dados coeso e confiável, pronto para análise de negócios e geração de insights.

O script `pipeline_limpeza_integracao.py` automatiza todo o processo, desde a leitura dos arquivos brutos até a exportação de um CSV consolidado e a geração de gráficos analíticos.

## 2. Estrutura do Script

O script é organizado de forma modular em 5 seções principais:

1.  **Carregamento dos Dados**: Leitura dos arquivos de origem.
2.  **Limpeza e Transformação**: Tratamento individual de cada conjunto de dados.
3.  **Integração dos Dados**: Junção das tabelas em uma base única.
4.  **Visualização dos Dados**: Criação de gráficos a partir dos dados consolidados.
5.  **Função Principal (main)**: Orquestra a execução de todo o pipeline.

## 3. Detalhamento das Funções

### `carregar_dados()`

Esta função é responsável por ler os quatro arquivos-fonte:
-   `clientes.csv`, `vendas.csv`, `produtos.csv`: São lidos como DataFrames do Pandas. É especificado o separador `sep=';'` para interpretar corretamente arquivos CSV formatados no padrão brasileiro/europeu. Também é usado `encoding='latin-1'` para evitar erros com caracteres especiais.
-   `avaliacoes.json`: É lido diretamente para um DataFrame.

A função inclui um bloco `try-except` para garantir que o programa exiba uma mensagem de erro amigável e encerre a execução caso algum dos arquivos não seja encontrado.

### Funções de Limpeza (`limpar_*`)

Cada tabela possui sua própria função de limpeza, garantindo a modularidade e a clareza do processo.

#### `limpar_clientes(df)`

Aplica as seguintes transformações na tabela de clientes:
-   **Correção de E-mails**: Insere o caractere `@` em e-mails que não o possuem (ex: `cliente@email.com`).
-   **Validação de Idade**: Remove clientes com idades consideradas inválidas (menores de 10 ou maiores de 120 anos).
-   **Padronização de 'Ativo'**: Converte diferentes representações textuais ('Yes', 'Sim', 'No', 'Não') para um padrão único ("Sim" ou "Não").
-   **Correção de 'Estado'**: Utiliza um dicionário para corrigir a sigla do estado com base na cidade do cliente, garantindo consistência.
-   **Formatação de Datas**: Converte a `Data_Cadastro` para o formato `dd/mm/yyyy`. Datas inválidas são transformadas em `NaN` (nulo).
-   **Tratamento de Nulos**: Converte o texto 'N/A' na coluna `Telefone` para o valor nulo padrão (`NaN`).
-   **Correção de Renda**: Transforma valores negativos de `Renda_Mensal` em positivos usando o valor absoluto.
-   **Remoção de Duplicados**: Exclui clientes duplicados com base no `ID_Cliente`.

#### `limpar_vendas(df)`

Aplica as seguintes transformações na tabela de vendas:
-   **Remoção de Vendas Inválidas**: Exclui registros onde a `Quantidade` ou o `Valor_Unitario` são zero ou negativos.
-   **Criação de 'Receita_Total'**: Calcula a receita da venda (`Quantidade` * `Valor_Unitario`) e arredonda o resultado para duas casas decimais, garantindo o formato monetário correto.

#### `limpar_produtos(df)`

Aplica as seguintes transformações na tabela de produtos:
-   **Correção de 'Preco_Custo'**: Converte o preço de texto para número, tratando a vírgula como separador decimal.
-   **Correção de 'Estoque_Atual'**: Transforma valores de estoque negativos em `0`.
-   **Padronização de 'Categoria'**: Agrupa categorias similares (ex: 'Informática', 'Telefonia') em uma única categoria ('Eletrônicos').

#### `limpar_avaliacoes(df)`

Aplica as seguintes transformações na tabela de avaliações:
-   **Padronização de 'Recomenda'**: Converte o texto ('Sim'/'Não') para valores booleanos (`True`/`False`).
-   **Tratamento de 'Comentario'**: Preenche comentários vazios com o texto "Sem comentário".

### `integrar_dados(...)`

Esta é a função central que une todas as tabelas limpas.
-   **Junção Vendas-Clientes**: Usa um `inner merge` para conectar vendas e clientes pelo `ID_Cliente`. Isso garante que apenas vendas de clientes existentes sejam mantidas.
-   **Junção com Produtos**: Usa um `inner merge` para adicionar os detalhes dos produtos. Isso garante que apenas vendas de produtos existentes no catálogo sejam mantidas.
-   **Junção com Avaliações**: Usa um `left merge` para adicionar a nota média dos produtos. O `left merge` é usado aqui para manter todas as vendas, mesmo que um produto ainda não tenha recebido avaliações (nesses casos, a nota será `NaN`). A nota média é pré-calculada para evitar a duplicação de linhas.
-   **Formatação da Nota**: A `Nota_Media_Produto` é arredondada para duas casas decimais.

### `visualizar_dados(df)`

Após a integração, esta função gera visualizações para uma análise exploratória inicial:
-   Cria uma pasta chamada `visualizacoes` para salvar os gráficos.
-   **Gráfico 1**: Um gráfico de barras que mostra a `Receita Total` por `Categoria de Produto`.
-   **Gráfico 2**: Um gráfico de barras horizontais que mostra o `Número de Vendas` por `Vendedor`.

### `main()`

A função `main` orquestra a execução de todo o pipeline na ordem correta. Ao final, ela salva o DataFrame consolidado no arquivo `dados_consolidados.csv`, pronto para ser utilizado.

## 4. Como Executar o Script

1.  Certifique-se de que os arquivos `clientes.csv`, `vendas.csv`, `produtos.csv`, e `avaliacoes.json` estão na mesma pasta que o script `pipeline_limpeza_integracao.py`.
2.  Tenha a biblioteca `pandas` e `matplotlib` instalada. Se não, instale com o comando:
    ```bash
    pip install pandas matplotlib
    ```
3.  Execute o script através do terminal:
    ```bash
    python pipeline_limpeza_integracao.py
    ```
4.  Ao final da execução, um novo arquivo chamado `dados_consolidados.csv` será gerado, e uma pasta `visualizacoes` conterá os gráficos analíticos.
