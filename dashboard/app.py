import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AtlasWeather Dashboard",
    layout="wide"
)

def connect():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "atlasweather")
    pwd = os.getenv("POSTGRES_PASSWORD", "atlasweather123")
    db = os.getenv("POSTGRES_DB", "atlasweather")
    url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url)

def loadData():
    engine = connect()
    query = """
        SELECT 
            c.city,
            c.latitude,
            c.longitude,
            c.admin_name,
            c.population,
            wf.date,
            wf.temp_max,
            wf.temp_min,
            wf.precip,
            wf.precip_prob,
            wf.wind_speed,
            wf.wind_gusts,
            wf.weather_code,
            wf.risk_score,
            wf.temp_category,
            wf.rain_category,
            wf.wind_category
        FROM weather_forecast wf
        JOIN cities c ON wf.city_id = c.city_id
        ORDER BY wf.risk_score DESC, wf.date ASC
    """
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df

st.title("AtlasWeather Dashboard")
st.write("Weather risk for delivery operations in Moroccan cities.")

df = loadData()

st.subheader("Filters")
f1, f2, f3 = st.columns(3)

cities = ["All"] + sorted(df["city"].unique().tolist())
selected_city = f1.selectbox("City", cities)

dates = ["All"] + sorted(df["date"].unique().tolist())
selected_date = f2.selectbox("Date", dates)

risk_levels = ["All", "Low", "Medium", "High"]
selected_risk = f3.selectbox("Risk Level", risk_levels)

filtered_df = df.copy()

if selected_city != "All":
    filtered_df = filtered_df[filtered_df["city"] == selected_city]

if selected_date != "All":
    filtered_df = filtered_df[filtered_df["date"] == selected_date]

if selected_risk == "Low":
    filtered_df = filtered_df[filtered_df["risk_score"] < 20]
elif selected_risk == "Medium":
    filtered_df = filtered_df[(filtered_df["risk_score"] >= 20) & (filtered_df["risk_score"] < 40)]
elif selected_risk == "High":
    filtered_df = filtered_df[filtered_df["risk_score"] >= 40]

st.subheader("KPIs")
col1, col2, col3, col4, col5 = st.columns(5)

total_cities = filtered_df["city"].nunique()
max_temp = filtered_df["temp_max"].max() if len(filtered_df) > 0 else 0
max_precip = filtered_df["precip"].max() if len(filtered_df) > 0 else 0
risk_count = len(filtered_df[filtered_df["risk_score"] >= 20])

if len(filtered_df) > 0:
    top_city_row = filtered_df.sort_values(by="risk_score", ascending=False).iloc[0]
    top_city = f"{top_city_row['city']} - {top_city_row['risk_score']}"
else:
    top_city = "None"

col1.metric("Cities", total_cities)
col2.metric("Max Temp", f"{max_temp}")
col3.metric("Max Rain", f"{max_precip}")
col4.metric("Risk Periods", risk_count)
col5.metric("Highest Risk City", top_city)

st.write("---")

st.subheader("Top Cities by Risk")
if len(filtered_df) > 0:
    top10 = filtered_df.groupby("city")["risk_score"].max().reset_index()
    top10 = top10.sort_values(by="risk_score", ascending=False).head(10)
    st.bar_chart(top10.set_index("city")["risk_score"])

st.subheader("Forecast Table")
cols = [
    "city", "admin_name", "date", "risk_score",
    "temp_max", "temp_min", "precip", "precip_prob",
    "wind_speed", "wind_gusts", "temp_category", "rain_category", "wind_category"
]
st.dataframe(filtered_df[cols])