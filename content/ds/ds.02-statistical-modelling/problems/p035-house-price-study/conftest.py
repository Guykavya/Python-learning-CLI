import numpy as np
import pandas as pd

def make_houses(n=1200, seed=2025):
    rng = np.random.default_rng(seed)
    area = np.clip(rng.lognormal(mean=np.log(1000), sigma=0.35, size=n), 350, 4000).round()
    bedrooms = np.clip(np.round(area / 450 + rng.normal(0, 0.6, n)), 1, 6).astype(int)
    bathrooms = np.clip(np.round(bedrooms * 0.7 + rng.normal(0, 0.5, n)), 1, 5).astype(int)
    age = rng.integers(0, 40, n)
    distance = rng.exponential(6, n).round(1)
    parking = (rng.random(n) < 0.55).astype(int)
    loc_score = distance + rng.normal(0, 3, n)
    locality = np.where(loc_score < 3, "Central", np.where(loc_score < 9, "Suburb", "Outskirts"))
    loc_eff = pd.Series(locality).map({"Central": 0.15, "Suburb": 0.0, "Outskirts": -0.10}).to_numpy()
    log_price = (3.4 + 0.85 * np.log(area / 1000) + 0.03 * bedrooms + 0.05 * bathrooms
                 - 0.008 * age - 0.025 * distance + 0.10 * parking + loc_eff
                 + rng.normal(0, 0.18, n))
    price = np.exp(log_price)
    price[940] *= 3                      # genuine luxury flat
    area[17] *= 10                       # data-entry error: an extra zero typed
    return pd.DataFrame({"price_lakh": price.round(2), "area_sqft": area, "bedrooms": bedrooms,
                         "bathrooms": bathrooms, "age_years": age, "distance_km": distance,
                         "parking": parking, "locality": locality})
