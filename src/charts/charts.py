# Renderização de gráficos com Altair
# Descrição: funções utilitárias para gráficos de linhas e colunas.

import altair as alt

# Gráfico de linhas: séries com ponto e tooltip
def line_chart(df, x_column, y_column, category_column, title=None):

    chart = (alt.Chart(df).mark_line(point=True).encode(
            
            # X (categorias)
            x=alt.X(f'{x_column}:O', title=x_column),
            
            # Y quantitativo com título
            y=alt.Y(f'{y_column}:Q', title=y_column),
            
            # Cor por categoria (N) para comparar séries
            color=alt.Color(f'{category_column}:N', title=category_column),
            
            # Tooltip: mostra X e Y ao passar o mouse
            tooltip=[x_column, y_column])
            
            # Título e dimensões padrão do gráfico
            .properties(title=title, width=700, height=400)
            
            # Estilo do título (tamanho, alinhamento, cor)
            .configure_title(fontSize=20, anchor='start', color='gray')
            
            # Estilo dos eixos (tamanhos das fontes)
            .configure_axis(labelFontSize=12, titleFontSize=14)
            )
    
    # Retorna o objeto Altair configurado
    return chart


# Gráfico de colunas (barras), com rótulos opcionais
def column_chart(df, x_column, y_column, title=None, show_labels=True, label_format=',.0f', label_position='outside', label_color=None, aggregation=None, width=700, height=400):

    # Campo do eixo Y: agrega se informado (sum, mean), senão usa a coluna bruta
    y_field = f'{aggregation}({y_column}):Q' if aggregation else f'{y_column}:Q'

    # Base (eixos e tooltip)
    base = alt.Chart(df).encode(

            # X (categorias)
        x=alt.X(f'{x_column}:O', title=x_column, axis=alt.Axis(labelAngle=0)),

            # Y quantitativo com título amigável
        y=alt.Y(y_field, title=y_column),
            
            # Tooltip: mostra X e Y ao passar o mouse
        tooltip=[
            alt.Tooltip(f'{x_column}:O', title=x_column),
            alt.Tooltip(y_field, title=y_column, format=label_format),])

    # Camada principal: barras
    bars = base.mark_bar()

    # Lista de camadas que comporão o gráfico (barras + textos opcionais)
    layers = [bars]

    # Opcional: adiciona rótulos de valor nas barras
    if show_labels:
        # Posição do rótulo: fora (acima) ou dentro da barra
        if label_position == 'outside':
            # Baseline para texto acima da barra e deslocamento vertical
            baseline = 'bottom'
            dy = -5
            default_color = 'black'
        else:
            # Baseline para texto dentro da barra e deslocamento vertical
            baseline = 'top'
            dy = 3
            default_color = 'white'

        # Camada de texto: centraliza e aplica cor determinada
        text = base.mark_text(
            align='center',
            baseline=baseline,
            dy=dy,
            color=label_color or default_color
        ).encode(
            # Valor formatado conforme `label_format` (ex: 1.2k, 1.000)
            text=alt.Text(y_field, format=label_format)
        )

        # Adiciona os rótulos à lista de camadas
        layers.append(text)

    # Combina camadas e aplica título, tamanho e estilos globais
    chart = alt.layer(*layers).properties(title=title, width=width, height=height).configure_title(fontSize=20, anchor='start', color='gray').configure_axis(labelFontSize=12, titleFontSize=14)

    return chart