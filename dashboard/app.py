# python
import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
import numpy as np

global filtered, all_cats

# Page config
st.set_page_config(
    page_title="El mito de las 5 estrellas",
    layout="wide"
)

# Data load
df = pd.read_csv("data/business_clustered.csv")

# Percentiles usados para la clasificación
mean_review = df["review_count"].mean()
outstanding_review = mean_review * 10

mean_rps = df["review_power_score"].mean()

p25_reviews = df["review_count"].quantile(0.25)
# st.text("Percentil 25 de reviews:")
# st.text(p25_reviews)
p95_reviews = df["review_count"].quantile(0.95)
# st.text("Percentil 95 de reviews:")
# st.text(p95_reviews)
p25_stars = df["stars_avg"].quantile(0.25)
# st.text("Percentil 25 de stars:")
# st.text(p25_stars)
p90_stars = df["stars_avg"].quantile(0.90)
# st.text("Percentil 90 de stars:")
# st.text(p90_stars)
p80_stars = df["stars_avg"].quantile(0.80)
# st.text("Percentil 80 de stars:")
# st.text(p80_stars)
p90_rps = df["review_power_score"].quantile(0.95)
# st.text("Percentil 90 de RPS:")
# st.text(p90_rps)
p25_rps = df["review_power_score"].quantile(0.25)
# st.text("Percentil 25 de RPS:")
# st.text(p25_rps)

# Clasificación de negocios según criterios definidos
CLASSIFICATION = {
    "overrated": "Sobrevalorados",
    "bad_business": "Mal negocio",
    "best_perceived_quality": "Mejor calidad percibida (RPS)",
    "best_rated": "Mejor valorados",
    "worst_rated": "Peor valorados",
    "others": "Otros",
}

# Mapa de colores por clasificación
color_map = {
    CLASSIFICATION["best_perceived_quality"]: "#4CAF50",
    CLASSIFICATION["best_rated"]: "#1E88E5",
    CLASSIFICATION["overrated"]: "#FF9800",
    CLASSIFICATION["bad_business"]: "#E53935",
    CLASSIFICATION["worst_rated"]: "#6D4C41",
    CLASSIFICATION["others"]: "#9E9E9E",
}

# Derivados del color_map para usar en Altair
color_domain = list(color_map.keys())
color_range = list(color_map.values())
color_scale = alt.Scale(domain=color_domain, range=color_range)

# Clasificación basada en las reglas definidas
def classify(row):
    if row["review_power_score"] >= p90_rps and row["stars_avg"] >= 4.0:
        return CLASSIFICATION["best_perceived_quality"]
    if row["review_count"] <= p25_reviews and row["stars_avg"] >= p80_stars:
        return CLASSIFICATION["overrated"]
    if row["review_count"] >= mean_review and row["stars_avg"] >= p80_stars:
        return CLASSIFICATION["best_rated"]
    if row["review_count"] >= p95_reviews and row["stars_avg"] <= p25_stars:
        return CLASSIFICATION["bad_business"]
    if row["stars_avg"] <= p25_stars and row["review_count"] <= p25_reviews:
        return CLASSIFICATION["worst_rated"]
    return CLASSIFICATION["others"]

# Aplicar clasificación
df["sector"] = df.apply(classify, axis=1)

# Funciones auxiliares
def separator():
    st.markdown(" \n")
    st.markdown(" \n")
    st.markdown(" \n")
    st.markdown(" \n")

def legend_item(label, sector_counts):
    count = sector_counts.get(label, 0)
    color = color_map.get(label, "#9E9E9E")
    dot = (
        "<span style='display:inline-block;width:10px;height:10px;"
        f"border-radius:50%;background:{color};margin-right:8px;'></span>"
    )
    return f"<div style='margin:4px 0;'>{dot}{label} ({count})</div>"


# Header
st.title("⭐ El mito de las 5 estrellas")
st.markdown(
    "## ¿Realmente los negocios con más estrellas son los mejores?\n"
    "Este dashboard muestra cómo el **volumen de opiniones** cambia de forma sustancial cómo percibimos la calidad de un negocio.\n\n"
    "Para demostrarlo, hemos creado un nuevo indicador llamado **Review Power Score (RPS)**, que combina la valoración media y la cantidad de opiniones para ofrecer una visión más completa de la calidad de un negocio."
    "\n\n\n\n"
)

# Datos generales
st.markdown("### 📊 Visión general de los datos")
st.markdown("En primer lugar, veamos algunos indicadores clave de los datos:")
c1, c2, c3, c4 = st.columns(4)

c1.metric("🏢 Total de negocios", len(df))
c2.metric("⭐ Valoración media", round(df["stars_avg"].mean(), 2))
c3.metric("🧾 Cantidad de reviews media", int(df["review_count"].mean()))
c4.metric("📈 RPS medio", round(mean_rps, 2))

separator()

with st.container(border=True):
    c1, spacer, c2 = st.columns([2,0.2,2])

    with c1:
        st.markdown("#### Distribución de valoraciones (estrellas)")
        star_chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("stars:O", title="Valoración (⭐)"),
                y=alt.Y("count():Q", title="Cantidad de negocios"),
                color=alt.Color(
                    "stars:Q",
                    scale=alt.Scale(range=["#E53935", "#4CAF50"]),
                    legend=None
                ),
                tooltip=[alt.Tooltip("count():Q", title="Cantidad de negocios")],
            )
        )
        st.altair_chart(star_chart, width='stretch')

    with c2:
        st.markdown("#### Distribución por RPS")
        rps_chart = (
            alt.Chart(df)
            .mark_line(interpolate="monotone")
            .encode(
                x=alt.X("review_power_score:Q", bin=alt.Bin(maxbins=50), title="Review Power Score (RPS)"),
                y=alt.Y("count():Q", title="Cantidad de negocios"),
                tooltip=[alt.Tooltip("count():Q", title="Cantidad de negocios")],
            )
        )
        st.altair_chart(rps_chart, width='stretch')
        # review_chart = (
        #     alt.Chart(df)
        #     .mark_bar()
        #     .encode(
        #         x=alt.X("review_count:Q", bin=alt.Bin(maxbins=50), title="Cantidad de reviews"),
        #         y=alt.Y("count():Q", title="Cantidad de negocios"),
        #         tooltip=[alt.Tooltip("count():Q", title="Cantidad de negocios")],
        #     )
        # )
        # st.altair_chart(review_chart, width='stretch')

separator()

# Oportunidades de oro
st.markdown("## 🥇 Oportunidades de ORO Globales (Top 10 RPS)")
st.markdown("##### Estos negocios muestran la mayor calidad percibida, por lo que son una excelente opción de inversión candidato a la expansión comercial:")

with st.container(border=True):

    gold = df.sort_values("review_power_score", ascending=False).head(10)

    st.dataframe(
        gold[[ "review_power_score", "name", "categories", "city", "stars_avg", "review_count"]],
        width='stretch',
        hide_index=True,
        column_config={
            "review_power_score": st.column_config.NumberColumn(label="RPS", format="%.2f"),
            "name": st.column_config.TextColumn(label="Nombre"),
            "categories": st.column_config.TextColumn(label="Categorías"),
            "city": st.column_config.TextColumn(label="Ciudad"),
            "stars_avg": st.column_config.NumberColumn(label="Valoración (⭐)", format="%.2f"),
            "review_count": st.column_config.NumberColumn(label="Reseñas"),
        },
    )

    st.download_button(
        "📥 Descargar oportunidades en CSV",
        gold.to_csv(index=False),
        key="gold_download",
        file_name="oportunidades_oro.csv",
        type="primary"
    )

separator()

st.markdown("## 📈 Segmentación por clusters VS RPS y percentiles")
# Explicación del uso de percentiles y reglas de clasificación actuales
st.info(
    "Se usan **percentiles** \\(p25, p80, p95\\) para detectar extremos y el **RPS** para capturar la combinación de cantidad y calidad de reseñas.\n"
    "- *💎 Mejor calidad percibida*: RPS por encima del percentilr \\(≥ p95\\) y valoración total ≥ 4.\n"
    "- *📈 Mejor valorados*: reseñas por encima de la media y valoración superior al percentil \\(≥ p80\\).\n"
    "- *⚠️ Sobrevalorados*: reseñas por debajo del percentil inferior \\(≤ p25\\) y valoración superior al percentil \\(≥ p80\\).\n"
    "- *📉 Mal negocio*: reseñas por debajo del percentil superior \\(≥ p95\\) y valoración inferior al percentil \\(≤ p25\\).\n"
    "- *🗑️ Peor valorados*: reseñas por debajo del percentil inferior\\(≤ p25\\) y valoración inferior \\(≤ p25\\).\n"
)

st.warning(
    "Para facilitar la visualización, la escala de la cantidad de reseñas está en logaritmo base 10 debido a la dispersión de los datos en esta magnitud. "
)
with st.container(border=True):

    c1, c2 = st.columns(2)
    with c1:
        # Mapeo de nombres y colores por cluster
        cluster_name_map = {
            0: "Pocas reseñas, alta valoración",
            1: "Pocas reseñas, baja valoración",
            2: "Muchas reseñas, baja valoración",
            3: "Muchas reseñas, alta valoración",
        }
        cluster_color_map = {
            "Pocas reseñas, alta valoración": "#FFEB3B",  # amarillo
            "Pocas reseñas, baja valoración": "#E53935",  # rojo
            "Muchas reseñas, baja valoración": "#1E88E5",  # azul
            "Muchas reseñas, alta valoración" : "#4CAF50",  # verde
        }
        cluster_domain = list(cluster_color_map.keys())
        cluster_range = list(cluster_color_map.values())

        # Preparar datos con etiqueta del cluster
        plot_cluster_df = df.assign(
            log_review_count=np.log10(df["review_count"]) - 1,
            cluster_label=df["cluster"].map(cluster_name_map).fillna("Otros")
        )

        custom_legend = alt.Legend(
            title="Cluster",
            orient="right",
            columns=1,  # reparte en 2 columnas para más espacio
            labelLimit=0,  # 0 = sin límite de truncado
            titleLimit=0,  # evita cortar el título
            labelExpr="replace(datum.label, ', ', '\\n')"  # parte la etiqueta en 2 líneas
        )

        # Dispersión con leyenda de cluster personalizada
        cluster_scatter = (
            alt.Chart(plot_cluster_df)
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X("log_review_count:Q", title="Cantidad de reseñas (log10) - 1"),
                y=alt.Y("stars_avg:Q", title="Valoración (⭐)", scale=alt.Scale(domain=[0.5, 5.5])),
                color=alt.Color(
                    "cluster_label:N",
                    scale=alt.Scale(domain=cluster_domain, range=cluster_range),
                    legend=custom_legend
                ),
                tooltip=[
                    alt.Tooltip("name:N", title="Nombre"),
                    alt.Tooltip("cluster_label:N", title="Cluster"),
                    alt.Tooltip("stars_avg:Q", title="Valoración", format=".2f"),
                    alt.Tooltip("review_count:Q", title="Reviews"),
                    alt.Tooltip("review_power_score:Q", title="RPS", format=".2f"),
                ],
            )
        )

        st.altair_chart(cluster_scatter, width='stretch')

    with c2:
        custom_legend = alt.Legend(
            title="Segmentación",
            orient="right",
            columns=1,
            labelLimit=0,  # sin truncado
            titleLimit=0,
            labelExpr="replace(datum.label, ' (', '\\n(')"  # salto de línea antes del paréntesis
        )

        plot_df = df.assign(log_review_count=np.log10(df["review_count"]) - 1)
        # plot_df = filtered.assign(log_review_count=filtered["review_count"])
        chart = (
            alt.Chart(plot_df)
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X("log_review_count:Q", title="Cantidad de reseñas (log10) - 1"),
                y=alt.Y("stars_avg:Q", title="Valoración", scale=alt.Scale(domain=[0.5, 5.5])),
                color=alt.Color(
                    "sector:N",
                    scale=color_scale,
                    legend=custom_legend
                ),
                tooltip=[
                    alt.Tooltip("name:N", title="Nombre"),
                    alt.Tooltip("stars_avg:Q", title="Valoración", format=".2f"),
                    alt.Tooltip("review_count:Q", title="Reviews"),
                    alt.Tooltip("review_power_score:Q", title="RPS", format=".2f"),
                    alt.Tooltip("sector:N", title="Clasificación"),
                ],
            )
        )

        st.altair_chart(chart, width='stretch')


def render_filters():
    global filtered, all_cats

    st.header("Filtros")

    # Instrucciones de uso de filtros
    st.info(
        " Usa los filtros para refinar. Los datos y gráficos se actualizan automáticamente."
        "- Selecciona `Estado` para acotar la región.\n"
        "- Tras elegir `Estado`, podrás filtrar por `Ciudad`.\n"
        "- La `Categoría` se construye dinámicamente a partir de los negocios visibles.\n"
    )

    # State filter
    states = ["Todos"] + sorted(df["state"].dropna().unique())
    state = st.selectbox("Estado", states)

    filtered = df.copy()
    if state != "Todos":
        filtered = filtered[filtered["state"] == state]

    # City filter (based on state filter)
    if state != "Todos":
        cities = ["Todas"] + sorted(filtered["city"].dropna().unique())
        city = st.selectbox("Ciudad", cities)
        if city != "Todas":
            filtered = filtered[filtered["city"] == city]
    else:
        city = "Todas"

    # Category filter (based on state and city filter)
    if "categories" in filtered.columns:
        all_cats = set()
        filtered["categories"].dropna().apply(
            lambda x: all_cats.update([c.strip() for c in x.split(",")])
        )
        category = st.selectbox("Categoría", ["Todas"] + sorted(all_cats))
        if category != "Todas":
            filtered = filtered[filtered["categories"].str.contains(category, na=False)]
    else:
        category = "Todas"

    # Aplicación final de filtros combinados
    filtered = df.copy()
    if state != "Todos":
        filtered = filtered[filtered["state"] == state]
    if city != "Todas":
        filtered = filtered[filtered["city"] == city]
    if category != "Todas":
        filtered = filtered[filtered["categories"].str.contains(category, na=False)]

# Segmentación por valoración y cantidad de reseñas
st.markdown("## 🔍 Datos segmentados por RPS y percentiles")
with st.container(border=True):
    # Gráfica a la izquierda y leyenda a la derecha
    col_left, col_center, spacer, col_right = st.columns([2, 4,0.2, 2])

    with col_right:
        render_filters()

    with col_center:
        st.markdown("### Gráfica de dispersión")

        plot_df = filtered.assign(log_review_count=np.log10(filtered["review_count"]) - 1)
        # plot_df = filtered.assign(log_review_count=filtered["review_count"])
        chart = (
            alt.Chart(plot_df)
            .mark_circle(size=60, opacity=0.7)
            .encode(
                x=alt.X("log_review_count:Q", title="Cantidad de reseñas (log10) - 1"),
                y=alt.Y("stars_avg:Q", title="Valoración", scale=alt.Scale(domain=[0.5, 5.5])),
                color=alt.Color("sector:N", scale=color_scale, legend=None),
                tooltip=[
                    alt.Tooltip("name:N", title="Nombre"),
                    alt.Tooltip("stars_avg:Q", title="Valoración", format=".2f"),
                    alt.Tooltip("review_count:Q", title="Reviews"),
                    alt.Tooltip("review_power_score:Q", title="RPS", format=".2f"),
                    alt.Tooltip("sector:N", title="Clasificación"),
                ],
            )
            .interactive()
        )

        st.altair_chart(chart, width='stretch')

    with col_left:
        # Contadores por etiqueta y etiquetas enriquecidas
        sector_counts = filtered["sector"].value_counts()
        legend_html = "".join(legend_item(lbl,sector_counts) for lbl in color_domain)

        st.markdown("### Leyenda y conteos")
        st.markdown(legend_html, unsafe_allow_html=True)



    separator()

    st.markdown("## 🥇 Top 10 RPS (Filtrados)")
    st.markdown("Estos negocios muestran la mayor calidad percibida según el RPS, filtrados según los criterios seleccionados:")
    mean_rps_str = "N/A" if pd.isna(mean_rps) else f"{mean_rps:.2f}"

    st.warning(
        f"Un RPS por debajo de la media (≈ {mean_rps_str}) puede indicar que no son las mejores oportunidades de inversión.")
    filtered_gold = filtered.sort_values("review_power_score", ascending=False).head(10)

    st.dataframe(
        filtered_gold[[ "review_power_score", "name", "categories", "city", "stars_avg", "review_count"]],
        width='stretch',
        hide_index=True,
        column_config={
            "review_power_score": st.column_config.NumberColumn(label="RPS", format="%.2f"),
            "name": st.column_config.TextColumn(label="Nombre"),
            "categories": st.column_config.TextColumn(label="Categorías"),
            "city": st.column_config.TextColumn(label="Ciudad"),
            "stars_avg": st.column_config.NumberColumn(label="Valoración (⭐)", format="%.2f"),
            "review_count": st.column_config.NumberColumn(label="Reseñas"),
        },
    )

    st.download_button(
        "📥 Descargar oportunidades en CSV",
        filtered_gold.to_csv(index=False),
        key="filtered_gold_download",
        file_name="oportunidades_oro.csv",
        type="secondary"
    )

    separator()

    # Mapa de distribución geográfica
    if {"latitude", "longitude"}.issubset(filtered.columns):
        st.markdown("## 🗺️ Distribución geográfica")
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=filtered["latitude"].mean(),
                    longitude=filtered["longitude"].mean(),
                    zoom=4,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=filtered,
                        get_position="[longitude, latitude]",
                        get_radius=60,
                        get_color="[255, 99, 71, 160]",
                        pickable=True,
                    )
                ],
            )
        )
