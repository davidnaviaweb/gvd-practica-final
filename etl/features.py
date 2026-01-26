import pandas as pd
import numpy as np

df = pd.read_csv("data/reviews_business.csv")

df["review_power_score"] = df["stars"] * np.log1p(df["review_count"])

df.to_csv("data/featured_business.csv", index=False)

print("✅ Features generadas")
