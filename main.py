"""Atividade 3 - Processamento de Dados com Python
Autor: Esdras Uday, Caue Reis , Baruc Nunes, Ana Soares
Data: 03/10/2025
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

CLIENTES_FILE = "clientes.csv"
VENDAS_FILE = "vendas.csv"
PRODUTOS_FILE = "produtos.csv"
AVALIACOES_FILE = "avaliacoes.json"

def carregar_dados():
    """Carrega os quatro conjuntos de dados de seus respectivos arquivos."""
    try:
        df_clientes = pd.read_csv(CLIENTES_FILE)
        df_vendas = pd.read_csv(VENDAS_FILE)
        df_produtos = pd.read_csv(PRODUTOS_FILE)
        df_avaliacoes = pd.read_json(AVALIACOES_FILE)
        print("Dados carregados com sucesso!")
        return df_clientes, df_vendas, df_produtos, df_avaliacoes
    
    except FileNotFoundError as e:
        print(f"Erro ao carregar os dados: {e}. Verifique se os arquivos estão no mesmo diretório do script.")
        return None, None, None, None


def limpar_clientes(df):
    """Aplica um pipeline completo de limpeza e transformação na base de clientes."""

    df_limpo = df.copy()

    def corrigir_email(email):
        if isinstance(email, str) and '@' not in email:
            if 'email.com' in email:
                return email.replace('email.com', '@email.com', 1)
        return email

    df_limpo['Email'] = df_limpo['Email'].apply(corrigir_email)

    if 'Idade' in df_limpo.columns:
        df_limpo = df_limpo[df_limpo['Idade'] <= 120].copy()
        df_limpo = df_limpo[df_limpo['Idade'] >= 10].copy()
    
    def padronizar_ativo(valor):
        if isinstance(valor, str):
            valor = valor.lower()
            if valor in ['yes', 'sim', 's']:
                return "Sim"
            elif valor in ['no', 'não', 'n']:
                return "Não"
        return "" #Coloquei pra retornar nada caso não seja nenhuma das condições
    df_limpo['Ativo'] = df_limpo['Ativo'].apply(padronizar_ativo)

    # Dicionário Cidade : Estado
    cidade_estado_map = {
        'Rio de Janeiro': 'RJ', 'São Paulo': 'SP', 'Belo Horizonte': 'MG', 'Brasília': 'DF',
        'Salvador': 'BA', 'Fortaleza': 'CE', 'Recife': 'PE', 'Porto Alegre': 'RS',
        'Curitiba': 'PR', 'Manaus': 'AM'}
    
    def corrigir_estado(row):
        cidade = row['Cidade']
        return cidade_estado_map.get(cidade, row['Estado'])
    
    df_limpo['Estado'] = df_limpo.apply(corrigir_estado, axis=1)
    datas_convertidas = pd.to_datetime(df_limpo['Data_Cadastro'], errors='coerce')
    df_limpo['Data_Cadastro'] = datas_convertidas.dt.strftime('%d/%m/%Y')
    df_limpo['Telefone'] = df_limpo['Telefone'].replace( np.nan,'N/A')
    df_limpo['Renda_Mensal'] = df_limpo['Renda_Mensal'].abs()
    df_limpo.drop_duplicates(subset='ID_Cliente', keep='first', inplace=True)

    return df_limpo

def limpar_vendas(df):
    """Aplica a limpeza e transformação na base de vendas."""
    df_limpo = df.copy()
    df_limpo = df_limpo[(df_limpo['Quantidade'] > 0) & (df_limpo['Valor_Unitario'] > 0)].copy()
    datas_convertidas = pd.to_datetime(df_limpo['Data_Venda'], errors='coerce')
    df_limpo['Data_venda'] = datas_convertidas.dt.strftime('%d/%m/%Y')
    df_limpo['Receita_Total'] = (df_limpo['Quantidade'] * df_limpo['Valor_Unitario']).round(2)
    return df_limpo

def limpar_produtos(df):
    """Aplica a limpeza e transformação na base de produtos."""
    df_limpo = df.copy()
    df_limpo['Preco_Custo'] = pd.to_numeric(df_limpo['Preco_Custo'].astype(str).str.replace(',', '.'), errors='coerce')
    datas_convertidas = pd.to_datetime(df_limpo['Data_Entrada_Estoque'], errors='coerce')
    df_limpo['Data_Entrada_Estoque'] = datas_convertidas.dt.strftime('%d/%m/%Y')
    df_limpo['Estoque_Atual'] = df_limpo['Estoque_Atual'].apply(lambda x: x if x > 0 else 0)
    df_limpo['Categoria'] = df_limpo['Categoria'].replace(['Informática', 'Telefonia', 'Acessórios'], 'Eletrônicos')
    return df_limpo

def limpar_avaliacoes(df):
    """Aplica a limpeza e transformação na base de avaliações."""
    df_limpo = df.copy()
    mapeamento_recomenda = {'Sim': True, 'Não': False}
    df_limpo['Recomenda'] = df_limpo['Recomenda'].map(mapeamento_recomenda).fillna(False).astype(bool)
    df_limpo['Comentario'].replace('', 'Sem comentário', inplace=True)
    df_limpo['Data_Avaliacao'] = pd.to_datetime(df_limpo['Data_Avaliacao'], errors='coerce')
    return df_limpo

def integrar_dados(df_clientes, df_vendas, df_produtos, df_avaliacoes):
    """ Une os dataframes limpos em um único dataframe consolidado."""
    df_integrado = pd.merge(df_vendas, df_clientes, on='ID_Cliente', how='inner')
    df_produtos_renomeado = df_produtos.rename(columns={'Nome_Produto': 'Produto'})
    df_integrado = pd.merge(df_integrado, df_produtos_renomeado, on='Produto', how='inner')
    df_avaliacoes_renomeado = df_avaliacoes.rename(columns={'Produto_Avaliado': 'Produto'})
    df_media_avaliacoes = df_avaliacoes_renomeado.groupby('Produto')['Nota'].mean().reset_index().rename(columns={'Nota': 'Nota_Media_Produto'})
    df_integrado = pd.merge(df_integrado, df_media_avaliacoes, on='Produto', how='left')
    df_integrado['Nota_Media_Produto'] = df_integrado['Nota_Media_Produto'].round(2)
    
    return df_integrado

def visualizar_dados(df):
    """Cria e salva gráficos a partir do DataFrame final e consolidado."""
    if not os.path.exists('visualizacoes'):
        os.makedirs('visualizacoes')
    #Gráfico 1
    plt.figure(figsize=(10, 6))
    receita_por_categoria = df.groupby('Categoria')['Receita_Total'].sum().sort_values(ascending=False)
    receita_por_categoria.plot(kind='bar', color='skyblue')
    plt.title('Receita Total por Categoria de Produto')
    plt.xlabel('Categoria')
    plt.ylabel('Receita Total (R$)')
    plt.xticks(rotation=45) 
    plt.tight_layout() 
    plt.savefig('visualizacoes/receita_por_categoria.png') 
    plt.close() 
    print("Gráfico 'Receita por Categoria' salvo em 'visualizacoes/receita_por_categoria.png'")

    #Gráfico 2
    plt.figure(figsize=(10, 6))
    vendas_por_vendedor = df['Vendedor'].value_counts().sort_values(ascending=True)
    vendas_por_vendedor.plot(kind='barh', color='lightgreen')
    plt.title('Número de Vendas por Vendedor')
    plt.xlabel('Número de Vendas')
    plt.ylabel('Vendedor')
    plt.tight_layout()
    plt.savefig('visualizacoes/vendas_por_vendedor.png')
    plt.close()
    print("Gráfico 'Vendas por Vendedor' salvo em 'visualizacoes/vendas_por_vendedor.png'")


def main():
    df_clientes, df_vendas, df_produtos, df_avaliacoes = carregar_dados()
    if df_clientes is None:
        return

    print("\nIniciando limpeza e processamento dos dados...")
    df_clientes_limpo = limpar_clientes(df_clientes)
    df_vendas_limpo = limpar_vendas(df_vendas)
    df_produtos_limpo = limpar_produtos(df_produtos)
    df_avaliacoes_limpo = limpar_avaliacoes(df_avaliacoes)
    print("Bases de dados limpas.")
    #dados finais
    df_final = integrar_dados(df_clientes_limpo, df_vendas_limpo, df_produtos_limpo, df_avaliacoes_limpo)
    df_final.to_csv('Dataset_Limpo.csv', index=False, sep=',', decimal='.', encoding='utf-8-sig')
    print("\nDados integrados e limpos salvos em Dataset_Limpo.csv")
    visualizar_dados(df_final)

if __name__ == '__main__':
    main()