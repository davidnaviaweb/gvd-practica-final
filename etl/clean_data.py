from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://mongo:27017/")
db = client["yelp"]

def normalize_city(city):
    if not isinstance(city, str):
        return ""
    return city.strip().replace(",", "").lower().title()

def aggregate_reviews_from_mongo() -> pd.DataFrame:
    """
    Agrega métricas por business_id desde la colección db.review:
      - stars_avg: promedio de estrellas por negocio
      - review_count: total de reviews por negocio
      - useful_sum, funny_sum, cool_sum: suma de votos por negocio
    """
    pipeline = [
        {"$match": {"business_id": {"$ne": None}, "stars": {"$ne": None}}},
        {"$group": {
            "_id": "$business_id",
            "stars_sum": {"$sum": "$stars"},
            "stars_count": {"$sum": 1},
            "review_count": {"$sum": 1},
        }},
        {"$project": {
            "business_id": "$_id",
            "_id": 0,
            "stars_avg": {"$round": [{"$divide": ["$stars_sum", "$stars_count"]}, 3]},
            "review_count_sum": "$review_count",
        }}
    ]
    agg = list(db.review.aggregate(pipeline))

    return pd.DataFrame(agg)

def load_business_from_mongo() -> pd.DataFrame:
    """
    Carga negocios base desde db.business.
    """
    cursor = db.business.find(
        {"review_count": {"$gt": 0}, "is_open": 1},
        {
            "business_id": 1, "name": 1, "city": 1, "state": 1,
            "longitude": 1, "latitude": 1, "categories": 1,
            "stars": 1, "review_count": 1
        }
    )
    df = pd.DataFrame(list(cursor))

    if not df.empty:
        df.dropna(subset=["business_id"], inplace=True)
    return df

def build_reviews_business_csv():
    business_df = load_business_from_mongo()
    reviews_df = aggregate_reviews_from_mongo()

    # Fusiona y actualiza campos desde reviews
    merged_df = business_df.merge(reviews_df, on="business_id", how="left")

    # Actualiza review_count con agregados
    merged_df["review_count"] = merged_df["review_count_sum"].fillna(merged_df["review_count"])

    # Filtra por mínimo de reviews
    merged_df = merged_df[merged_df["review_count"] >= 10]

    cols_keep = [
        "business_id", "name", "city", "state", "longitude", "latitude", "categories", "stars", "stars_avg", "review_count"
    ]
    merged_df = merged_df[cols_keep]
    merged_df["city"] = merged_df["city"].apply(normalize_city)


    print(f"Total de registros cargados: {len(merged_df)}")
    merged_df.dropna()

    # Normaliza ciudad y categorías

    return merged_df

def clean_business():
    cursor = db.business.find(
        {
            "review_count": {"$gt": 10},
            "is_open": 1,
            "stars": {"$ne": None}
        },
        {
            "business_id": 1,
            "name": 1,
            "stars": 1,
            "review_count": 1,
            "city": 1,
            "state": 1,
            "longitude": 1,
            "latitude": 1,
            "categories": 1
        }
    )

    df = pd.DataFrame(list(cursor))
    print(f"Total de registros cargados: {len(df)}")
    df.dropna(inplace=True)

    # Normaliza ciudad y categorías
    df["city"] = df["city"].apply(normalize_city)

    return df

if __name__ == "__main__":
    # df = clean_business()
    # df.to_csv("data/reviews_business.csv", index=False)

    df = build_reviews_business_csv()
    df.to_csv("data/reviews_business.csv", index=False)

    print("✅ Datos limpios guardados")
