import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Leitura e preparação dos dados
# =========================
CSV_FILE = 'ecommerce_estatistica.csv'

try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    # fallback para o nome que veio no upload desta conversa
    df = pd.read_csv('ecommerce_estatistica.csv')

if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

numeric_cols = ['Preço', 'Nota', 'N_Avaliações', 'Desconto']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=numeric_cols).copy()

# =========================
# Insights para destaque
# =========================
preco_medio = df['Preço'].mean()
nota_media = df['Nota'].mean()
maior_marca = df['Marca'].value_counts().idxmax()
qtd_maior_marca = df['Marca'].value_counts().max()
correl_preco_desconto = df[['Preço', 'Desconto']].corr().iloc[0, 1]

# =========================
# Gráficos
# =========================
fig_hist = px.histogram(
    df,
    x='Preço',
    nbins=20,
    title='Histograma da Distribuição de Preços',
    labels={'Preço': 'Preço', 'count': 'Frequência'}
)
fig_hist.update_layout(template='plotly_white')

fig_scatter = px.scatter(
    df,
    x='Preço',
    y='N_Avaliações',
    color='Nota',
    hover_data=['Título', 'Marca', 'Gênero'],
    title='Relação entre Preço e Número de Avaliações',
    labels={'Preço': 'Preço', 'N_Avaliações': 'Número de Avaliações', 'Nota': 'Nota'}
)
fig_scatter.update_layout(template='plotly_white')

corr = df[['Preço', 'Nota', 'N_Avaliações', 'Desconto']].corr().round(2)
fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        text=corr.values,
        texttemplate='%{text}',
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    )
)
fig_heatmap.update_layout(
    title='Mapa de Calor das Correlações',
    template='plotly_white'
)

marca_counts = df['Marca'].value_counts().head(10).sort_values(ascending=True)
fig_bar = px.bar(
    x=marca_counts.values,
    y=marca_counts.index,
    orientation='h',
    title='Top 10 Marcas com Mais Produtos',
    labels={'x': 'Quantidade de Produtos', 'y': 'Marca'}
)
fig_bar.update_layout(template='plotly_white')

# pizza com agrupamento em "Outros" para ficar legível
_genero = df['Gênero'].fillna('Não informado').astype(str).str.strip()
genero_counts = _genero.value_counts()
top5 = genero_counts.head(5)
outros = genero_counts.iloc[5:].sum()
if outros > 0:
    pizza_data = pd.concat([top5, pd.Series({'Outros': outros})])
else:
    pizza_data = top5

fig_pie = px.pie(
    values=pizza_data.values,
    names=pizza_data.index,
    title='Distribuição dos Produtos por Gênero (Top 5 + Outros)'
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(template='plotly_white')

fig_density = px.histogram(
    df,
    x='Preço',
    marginal='violin',
    histnorm='probability density',
    nbins=20,
    title='Densidade da Distribuição de Preços',
    labels={'Preço': 'Preço', 'count': 'Densidade'}
)
fig_density.update_layout(template='plotly_white')

fig_reg = px.scatter(
    df,
    x='Preço',
    y='Desconto',
    trendline='ols',
    hover_data=['Título', 'Marca'],
    title='Relação entre Preço e Desconto com Linha de Regressão',
    labels={'Preço': 'Preço', 'Desconto': 'Desconto'}
)
fig_reg.update_layout(template='plotly_white')

# =========================
# Aplicação Dash
# =========================
app = Dash(__name__)
server = app.server

card_style = {
    'backgroundColor': 'white',
    'borderRadius': '16px',
    'padding': '18px',
    'boxShadow': '0 2px 12px rgba(0,0,0,0.08)',
    'marginBottom': '20px'
}

app.layout = html.Div(
    style={'backgroundColor': '#f5f7fb', 'padding': '24px', 'fontFamily': 'Arial, sans-serif'},
    children=[
        html.H1('Dashboard de Análise de E-commerce', style={'textAlign': 'center', 'marginBottom': '8px'}),
        html.P(
            'Aplicação Dash desenvolvida a partir do arquivo ecommerce_estatistica.csv para visualização interativa dos principais gráficos da análise.',
            style={'textAlign': 'center', 'marginBottom': '24px', 'color': '#555'}
        ),

        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '16px', 'marginBottom': '24px'},
            children=[
                html.Div([html.H4('Preço médio'), html.P(f'R$ {preco_medio:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))], style=card_style),
                html.Div([html.H4('Nota média'), html.P(f'{nota_media:.2f}')], style=card_style),
                html.Div([html.H4('Marca com mais produtos'), html.P(f'{maior_marca} ({qtd_maior_marca})')], style=card_style),
                html.Div([html.H4('Correlação preço x desconto'), html.P(f'{correl_preco_desconto:.2f}')], style=card_style),
            ]
        ),

        html.Div([
            html.H3('Principais destaques da análise'),
            html.Ul([
                html.Li('Os preços apresentam concentração em faixas específicas, o que pode indicar padronização de catálogo ou segmentação de produto.'),
                html.Li('A relação entre preço e número de avaliações ajuda a entender se produtos mais caros também são mais populares.'),
                html.Li('O mapa de calor permite identificar correlações entre preço, nota, desconto e quantidade de avaliações.'),
                html.Li('As marcas mais frequentes mostram quais fabricantes possuem maior presença na base de produtos.'),
                html.Li('No gráfico de pizza, os gêneros menos frequentes foram agrupados em “Outros” para melhorar a leitura visual.')
            ])
        ], style=card_style),

        html.Div([dcc.Graph(figure=fig_hist)], style=card_style),
        html.Div([dcc.Graph(figure=fig_scatter)], style=card_style),
        html.Div([dcc.Graph(figure=fig_heatmap)], style=card_style),
        html.Div([dcc.Graph(figure=fig_bar)], style=card_style),
        html.Div([dcc.Graph(figure=fig_pie)], style=card_style),
        html.Div([dcc.Graph(figure=fig_density)], style=card_style),
        html.Div([dcc.Graph(figure=fig_reg)], style=card_style),
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
