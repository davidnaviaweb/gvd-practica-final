#!/bin/bash
set -euo pipefail

export PYTHONUNBUFFERED=1

# Mensaje de bienvenida
echo ""
echo "🚀 Iniciando la aplicación de análisis de datos..."
echo ""

# Comprobación de existencia del fichero data/business_clustered.csv
if [ -f "data/business_clustered.csv" ]; then
  echo "✅ El fichero data/business_clustered.csv existe."
else
  echo "❌ El fichero data/business_clustered.csv NO existe."
  echo "🔄 Iniciando el proceso ETL y análisis de datos..."
  echo ""

  # Esperar a que MongoDB esté disponible
  echo "⏳ Esperando a MongoDB..."
  until python -c "from pymongo import MongoClient; MongoClient('mongo', 27017).admin.command('ping')" >/dev/null 2>&1; do
    sleep 2
  done

  echo "✅ MongoDB disponible"
  echo ""

  # Carga de datos inicial
  echo "📥 Cargando datos en MongoDB..."
  python -u etl/load_data.py
  echo ""

  # Pipeline de procesamiento de datos
  echo "🧹 Limpieza de datos..."
  python -u etl/clean_data.py
  echo ""

  echo "🧠 Generando features..."
  python -u etl/features.py
  echo ""

  echo "🤖 Ejecutando clustering..."
  python analysis/clustering.py
  echo ""
fi
echo ""


# Levantar el dashboard
echo "📊 Iniciando el dashboard de Streamlit..."
echo ""
echo "🚀 Accede aquí: http://localhost:8501"
exec streamlit run dashboard/app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.runOnSave=true

#exec streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0 > /dev/null 2>&1

