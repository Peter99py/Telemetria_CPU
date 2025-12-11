
import altair as alt

# Gráfico de linhas: séries com ponto e tooltip
def line_chart(df, x_column, y_column, category_column, title=None):

    chart = (alt.Chart(df).mark_line(point=True).encode(
            x=alt.X(f'{x_column}:O', title=x_column),
            y=alt.Y(f'{y_column}:Q', title=y_column),
            color=alt.Color(f'{category_column}:N', title=category_column),
            tooltip=[x_column, y_column])
            .properties(title=title, width=700, height=400)
            .configure_title(fontSize=20, anchor='start', color='gray')
            .configure_axis(labelFontSize=12, titleFontSize=14)
            )
    return chart


# Gráfico de colunas (barras), com rótulos opcionais
def column_chart(df, x_column, y_column, title=None, show_labels=True, label_format=',.0f', label_position='outside', label_color=None, aggregation=None, width=700, height=400):

    y_field = f'{aggregation}({y_column}):Q' if aggregation else f'{y_column}:Q'

    base = alt.Chart(df).encode(
        x=alt.X(f'{x_column}:O', title=x_column, axis=alt.Axis(labelAngle=0)),
        y=alt.Y(y_field, title=y_column),
        tooltip=[
            alt.Tooltip(f'{x_column}:O', title=x_column),
            alt.Tooltip(y_field, title=y_column, format=label_format),])

    bars = base.mark_bar()
    layers = [bars]

    if show_labels:
        if label_position == 'outside':
            baseline = 'bottom'
            dy = -5
            default_color = 'black'
        else:
            baseline = 'top'
            dy = 3
            default_color = 'white'

        text = base.mark_text(
            align='center',
            baseline=baseline,
            dy=dy,
            color=label_color or default_color
        ).encode(
            text=alt.Text(y_field, format=label_format)
        )
        layers.append(text)

    chart = alt.layer(*layers).properties(title=title, width=width, height=height).configure_title(fontSize=20, anchor='start', color='gray').configure_axis(labelFontSize=12, titleFontSize=14)

    return chart
