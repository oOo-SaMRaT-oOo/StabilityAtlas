import pandas as pd

df = pd.read_parquet("/Users/suman-mac/Projects/StabilityAtlas/data/raw/sim_batch_10000runs_20261017_113958.parquet")

print(df["is_unstable"].value_counts())
print(df["is_unstable"].mean())
