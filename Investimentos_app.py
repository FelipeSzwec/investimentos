import pandas as pd
import streamlit as st
import altair as alt
import openpyxl

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

# Renomear coluna "Subtipo" para "Mercado"
df.rename(columns={"Subtipo": "Mercado"}, inplace=True)
config.rename(columns={"Subtipo": "Mercado"}, inplace=True)

# Remover linhas em branco
df = df.dropna(subset=["Data"])

# Garantir formato de data
df["Data"] = pd.to_datetime(df["Data"])

# Garantir os tipos corretos
config["Capital Inicial (R$)"] = config["Capital Inicial (R$)"].astype(float)
df["Lucro/Prejuízo (R$)"] = df["Lucro/Prejuízo (R$)"].astype(float)

# Mapear capital por mercado
capital_por_mercado = config.set_index("Mercado")["Capital Inicial (R$)"].to_dict()
df["Capital"] = df["Mercado"].map(capital_por_mercado)

# Calcular % sobre capital
df["% sobre Capital"] = df.apply(lambda row: (row["Lucro/Prejuízo (R$)"] / row["Capital"] * 100) if row["Capital"] else 0, axis=1)

# Emoji Resultado
df["Resultado (Emoji)"] = df["Lucro/Prejuízo (R$)"].apply(lambda x: STYLES['lucro'] if x >= 0 else STYLES['prejuizo'])

# Filtros interativos
area = st.selectbox("Filtrar por Área:", ["Todas"] + sorted(df["Área"].unique()))
mercado = st.selectbox("Filtrar por Mercado:", ["Todos"] + sorted(df["Mercado"].dropna().unique()))

# Aplicar filtros
if area != "Todas":
    df = df[df["Área"] == area]
if mercado != "Todos":
    df = df[df["Mercado"] == mercado]

# Exibir tabela
st.dataframe(df.sort_values("Data", ascending=False), use_container_width=True)

# KPIs
st.subheader("📈 Resumo")
col1, col2, col3 = st.columns(3)
col1.metric("Lucro Total", f"R$ {df['Lucro/Prejuízo (R$)'].sum():.2f}")
col2.metric("% Retorno Total", f"{df['% sobre Capital'].sum():.2f}%")
col3.metric("Nº de Operações", int(df['Nº Operações/Jogos'].sum()))

# Gráfico diário
st.subheader("📅 Evolução Diária")
df_graf = df.groupby("Data").agg({"Lucro/Prejuízo (R$)": "sum"}).reset_index()
st.altair_chart(
    alt.Chart(df_graf).mark_line(point=True).encode(
        x='Data:T', y='Lucro/Prejuízo (R$):Q', tooltip=['Data', 'Lucro/Prejuízo (R$)']
    ).properties(height=300), use_container_width=True
)

# Gráfico por mercado
st.subheader("📌 Lucro por Mercado")
df_mercado = df.groupby("Mercado").agg({"Lucro/Prejuízo (R$)": "sum"}).reset_index()
st.altair_chart(
    alt.Chart(df_mercado).mark_bar().encode(
        x=alt.X('Lucro/Prejuízo (R$):Q', title='Lucro Total (R$)'),
        y=alt.Y('Mercado:N', sort='-x', title=''),
        color='Mercado:N',
        tooltip=['Mercado', 'Lucro/Prejuízo (R$)']
    ).properties(height=400), use_container_width=True
)

# Gráfico mensal com mês por extenso
st.subheader("📅 Evolução Mensal")
df["Ano-Mês"] = df["Data"].dt.strftime('%b/%Y')  # Ex: Abr/2025
df_mensal = df.groupby("Ano-Mês").agg({"Lucro/Prejuízo (R$)": "sum"}).reset_index()
st.altair_chart(
    alt.Chart(df_mensal).mark_line(point=True).encode(
        x=alt.X('Ano-Mês:N', title="Mês"),
        y='Lucro/Prejuízo (R$):Q',
        tooltip=['Ano-Mês', 'Lucro/Prejuízo (R$)']
    ).properties(height=300), use_container_width=True
)

st.caption("Painel interativo com dados do GitHub | Atualizado automaticamente")