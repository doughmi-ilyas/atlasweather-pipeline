import os
import json
import pandas as pd

def bronzedata(path):
    jsonFile = []
    for file in os.listdir(path):
        if ".json" in file and "-failed.json" not in file:
            jsonFile.append(file)

    return jsonFile

def checkquality(df):
    bad = df[df["precipitation_sum"] < 0]
    print(f"negative precipitation : {len(bad)} rows")

    bad = df[(df["temperature_2m_max"] < -5) | (df["temperature_2m_max"] > 55)]
    print(f"wild temps : {len(bad)} rows")

    bad = df[(df["latitude"] < 21) | (df["latitude"] > 36) | (df["longitude"] < -17) | (df["longitude"] > -1)]
    print(f"coords outside Morocco : {len(bad)} rows")

    dup = df.duplicated(subset=["city", "time"])
    print(f"duplicate city+date : {dup.sum()} rows")

def buildrows(path,files):
    frames = []

    for file in files:
        with open(f"{path}/{file}","r", encoding="utf-8") as f:
            data = json.load(f)
            daily = data["response"]["daily"]
            df = pd.DataFrame([daily])
            df["city"] = data["city"]
            df["latitude"] = data["lat"]
            df["longitude"] = data["lon"]
            df["fetched_at"] = data["fetched_at"]
            frames.append(df) 
    combine = pd.concat(frames, ignore_index=True)
    combine = combine.explode(["time","temperature_2m_max","temperature_2m_min","precipitation_sum","precipitation_probability_max","wind_speed_10m_max","wind_gusts_10m_max","weather_code"])
    combine["fetched_at"] = pd.to_datetime(combine["fetched_at"])
    combine["time"] = pd.to_datetime(combine["time"])

    num_cols = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "weather_code"]
    for col in num_cols:
        combine[col] = pd.to_numeric(combine[col])

    checkquality(combine)
    combine = combine.drop_duplicates(subset=["city", "time"])

    cities = pd.read_csv("data/ma-cities.csv", encoding="utf-8")
    cities = cities[["city", "admin_name", "population"]]
    combine = combine.merge(cities, on="city", how="left")

    os.makedirs("silver", exist_ok=True)
    combine.to_csv("silver/data.csv", index=False)
    return combine

def main():
    os.makedirs("silver", exist_ok=True)
    files = bronzedata("bronze")
    df = buildrows("bronze", files)
    print(f"Silver transformation completed with {len(df)} rows")
    return df

if __name__ ==  "__main__":
    main()