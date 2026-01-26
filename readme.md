# Hipótesis: #
La valoración media (stars) no es suficiente para medir el éxito de un negocio. El volumen total y la consistencia de las valoraciones aportan una señal más fiable.

## 💡 Review Power Score (RPS) ##

> Partimos de una métrica conocida, las estrellas, y demostramos que aislada es engañosa. Al introducir volumen y estabilidad mediante una métrica propia, obtenemos una visión más realista del éxito de un negocio.

Basado en la hipótesis planteada, proponemos una métrica que utiliza la valoración media y el volumen de reviews:

> Review Power Score (RPS), que nos permite encontrar aquellos negocios que presentan una percepción de calidad real y una fiabilidad estadística.

📌 ¿Por qué?

- Porque penaliza negocios con pocas reviews
- Porque escala bien
- Porque es fácil de explicar


> El valor del RPS penaliza a aquellos negocios que tienen muy pocas valoraciones, ya que éstos no representan una calidad percibida real, por mucho que estas valoraciones sean de 5 estrellas. Sin embargo, el uso del logaritmo aplica un rendimiento decreciente a medida que aumenta el volumen de reseñas.

Definimos el RPS como es el producto entre la valoración media y el logaritmo del número de reseñas.

```RPS = stars × log(review_count)```

La función matemática cumple con las siguientes características: 

1. Monotonía positiva
    - Si aumentan las estrellas, el score debe aumentar
    - Si aumentan las reviews, el score debe aumentar

2. Penalización de baja representación
    - Un negocio con pocas reviews no debe competir en igualdad con uno con muchas

3. Rendimientos decrecientes
    - Pasar de 10 a 20 reviews no tiene el mismo impacto que 1000 a 1010

4. Escala comparable
    - El score no explota numéricamente
    - Permite la comparación directa entre negocios


## 🧹 Carga, limpieza y tratamiento de los datos  ##

En una base de datos de MongoDB, cargamos los datos desde los archivos JSON proporcionados por el dataset de Yelp usando el método de lectura por lotes para manejar grandes volúmenes de datos.

A continuación realizamos el tratamiento de los datos, agrupando las reviews de un mismo negocio, calculando la valoración media real y el número de reseñas exacto, ya que el dataset de business nos ofrece valoraciones redondeadas.

Seguidamente, ejecutamos una limpieza básica de los datos, eliminando los negocios que estén cerrados o que tengan menos de 10 reseñas, ya que estos no son para nada representativos. Además, también descartamos entradas con valores nulos o inconsistentes en el campo 'stars'.

Posteriormente, calculamos el RPS para cada negocio utilizando la fórmula definida anteriormente.

Por último, empleamos el algoritmo K-means para dividir los negocios en 4 clústers a partir de los campos stars y review_count. Dicha clusterización nos permite agrupar los negocios en categorías de desempeño similares, basándose en su valoración media y volumen de reseñas. Esto ayuda a identificar patrones, tendencias y segmentos diferenciados dentro del conjunto de negocios, facilitando el análisis comparativo y la toma de decisiones basada en datos reales y no solo en la valoración media.


## 📈 Visualización de los datos ##
Utilizamos Streamlit para crear un dashboard interactivo que permite explorar y visualizar los datos de manera intuitiva. El dashboard incluye:
- **Gráficos de dispersión**: para visualizar la relación entre la valoración media, el número de reseñas y el RPS.
- **Histogramas**: para mostrar la distribución de las valoraciones y el RPS.
- **Filtros interactivos**: para seleccionar categorías específicas de negocios y ajustar los parámetros de visualización.
- **Mapa**: para geolocalizar los negocios y observar patrones geográficos.



## ⚙️ Ejecución

### 1. Clonar el repositorio: ###

```
git clone https://github.com/davidnaviaweb/gvd-practica-final
```

### 2. Navegar al directorio del proyecto: ###

```
cd gvd-practica-final
```

### 3. Copiar los archivos JSON del dataset de Yelp: ###

Descargar el dataset de Yelp desde [aquí](https://www.yelp.com/dataset) y copiar a la carpeta `data/raw/` del los archivos JSON necesarios:

- yelp_academic_dataset_business.json
- yelp_academic_dataset_review.json

### 4. Construir y ejecutar la aplicación con Docker Compose: ###

Requisitos:
- Docker
- Docker Compose

Ejecutar:
`docker compose up --build`

Acceder al dashboard:
http://localhost:8501
