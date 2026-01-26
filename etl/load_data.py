import json
import os
from pymongo import MongoClient
from tqdm import tqdm

client = MongoClient("mongodb://mongo:27017/")
db = client["yelp"]

BASE_PATH = "/data/raw"
BATCH_SIZE = 10000

def load_json(filename, collection):
    path = os.path.join(BASE_PATH, filename)
    with open(path, "r", encoding="utf-8") as f:
        total = sum(1 for _ in f)
    coleccion_count = db[collection].count_documents({})
    if coleccion_count > 0:
        print(f"✅ La colección '{collection}' ya tiene {total} registros. No se cargan datos.")
        return
    if coleccion_count > 0:
        print(f"⚠️  La colección '{collection}' tiene {coleccion_count} registros. Se eliminará.")
        db[collection].drop()
    count = 0
    with open(path, "r", encoding="utf-8") as f, tqdm(total=total, desc=f"Cargando {collection}") as pbar:
        batch = []
        for line in f:
            batch.append(json.loads(line))
            if len(batch) == BATCH_SIZE:
                db[collection].insert_many(batch)
                count += len(batch)
                batch = []
                pbar.update(BATCH_SIZE)
        if batch:
            db[collection].insert_many(batch)
            count += len(batch)
            pbar.update(len(batch))
    print(f"Total de registros cargados en '{collection}': {count}")

if __name__ == "__main__":
    # load_json("yelp_academic_dataset_business.json", "business")
    # load_json("yelp_academic_dataset_review.json", "review")
    # load_json("yelp_academic_dataset_user.json", "user")
    print("✅ Datos cargados en MongoDB")
