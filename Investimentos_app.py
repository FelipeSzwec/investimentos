# Investimento_app.py
import pandas as pd
import streamlit as st
import altair as alt

# --- CONFIG ---
STYLES = {
    'lucro': '✅',
    'prejuizo': '❌'
}

@st.cache_data
def carregar_planilha(url):
    return pd.read_excel(url, sheet_name=None)

st.set_page_config(page_title="Painel de Investimentos", layout="wide")
st.title("📊 Painel de Investimentos - Futebol & Mercado Financeiro")

# URL para o arquivo no GitHub bruto (raw)
github_url = st.secrets["excel_url"]

# Carregar dados
sheets = carregar_planilha(github_url)
df = sheets["Lançamentos"]
config = sheets["Configuração"]

# Remover linhas em branco
df = df.dropna(subset=["Data"])

# Garantir os tipos corretos
config["Capital Inicial (R$)"] = config["Capital Inicial (R$)"].astype(float)
df["Lucro/Prejuízo (R$)"] = df["Lucro/Prejuízo (R$)"].astype(float)

# Mapear capital por subtipo
capital_por_subtipo = config.set_index("Subtipo")["Capital Inicial (R$)"].to_dict()
df["Capital"] = df["Subtipo"].map(capital_por_subtipo)

# Calcular % sobre capital
df["% sobre Capital"] = df.apply(lambda row: (row["Lucro/Prejuízo (R$)"] / row["Capital"] * 100) if row["Capital"] else 0, axis=1)

# Emoji Resultado
df["Resultado (Emoji)"] = df["Lucro/Prejuízo (R$)"].apply(lambda x: STYLES['lucro'] if x >= 0 else STYLES['prejuizo'])

# Filtros interativos
area = st.selectbox("Filtrar por Área:", ["Todas"] + sorted(df["Área"].unique()))
subtipo = st.selectbox("Filtrar por Subtipo:", ["Todos"] + sorted(df["Subtipo"].dropna().unique()))

# Aplicar filtros
if area != "Todas":
    df = df[df["Área"] == area]
if subtipo != "Todos":
    df = df[df["Subtipo"] == subtipo]

# Exibir tabela
st.dataframe(df.sort_values("Data", ascending=False), use_container_width=True)

# KPIs
st.subheader("📈 Resumo")
col1, col2, col3 = st.columns(3)
col1.metric("Lucro Total", f"R$ {df['Lucro/Prejuízo (R$)'].sum():.2f}")
col2.metric("% Retorno Total", f"{df['% sobre Capital'].sum():.2f}%")
col3.metric("Nº de Operações", int(df['Nº Operações/Jogos'].sum()))

# Gráficos
st.subheader("📅 Evolução Diária")
df_graf = df.groupby("Data").agg({"Lucro/Prejuízo (R$)": "sum"}).reset_index()
st.altair_chart(
    alt.Chart(df_graf).mark_line(point=True).encode(
        x='Data:T', y='Lucro/Prejuízo (R$):Q', tooltip=['Data', 'Lucro/Prejuízo (R$)']
    ).properties(height=300), use_container_width=True
)

st.caption("Painel interativo com dados do GitHub | Atualizado automaticamente")
