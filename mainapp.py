import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.figure_factory as ff
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import datetime, time
from PIL import Image
from pathlib import Path
import os

st.set_page_config(page_title="Comprehensive Health Tracker & Analytics", layout="wide")

DB_NAME = 'tracker.db'

# --- Database setup ---

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_entries (
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            food_items TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            meal_type TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS weight_entries (
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            weight REAL,
            context TEXT,
            notes TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sleep_entries (
            id INTEGER PRIMARY KEY,
            date TEXT,
            sleep_time TEXT,
            wake_time TEXT,
            duration REAL,
            quality INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_food_entry(entry):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO food_entries(date, time, food_items, calories, protein, carbs, fat, meal_type)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (entry['date'], entry['time'], ','.join(entry['food_items']),
               entry['calories'], entry['protein'], entry['carbs'], entry['fat'], entry['meal_type']))
    conn.commit()
    conn.close()

def insert_weight_entry(entry):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO weight_entries(date, time, weight, context, notes)
                 VALUES (?, ?, ?, ?, ?)''',
              (entry['date'], entry['time'], entry['weight'], entry['context'], entry['notes']))
    conn.commit()
    conn.close()

def insert_sleep_entry(entry):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO sleep_entries(date, sleep_time, wake_time, duration, quality, notes)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (entry['date'], entry['sleep_time'], entry['wake_time'],
               entry['duration'], entry['quality'], entry['notes']))
    conn.commit()
    conn.close()

def load_entries(table_name):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY date DESC, time DESC", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# Initialize DB and load cached entries
init_db()
if 'food_entries' not in st.session_state:
    st.session_state.food_entries = load_entries('food_entries').to_dict(orient='records')
if 'weight_entries' not in st.session_state:
    st.session_state.weight_entries = load_entries('weight_entries').to_dict(orient='records')
if 'sleep_entries' not in st.session_state:
    st.session_state.sleep_entries = load_entries('sleep_entries').to_dict(orient='records')

# --- Sidebar navigation ---
page = st.sidebar.selectbox("Navigate", ["Food Tracker", "Weight Logger", "Sleep Tracker", "Advanced Analytics"])

# --- Helper function to convert session state lists to DataFrames ---
def session_to_df(key):
    if key in st.session_state and st.session_state[key]:
        return pd.DataFrame(st.session_state[key])
    return pd.DataFrame()

# --- Pages ---

def food_tracker():
    st.title("Food Tracker")
    uploaded_file = st.file_uploader("Upload food photo", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Photo", use_column_width=True)

    food_items = st.text_input("Food Items (comma separated)")
    calories = st.number_input("Calories", min_value=0, value=250)
    protein = st.number_input("Protein (g)", min_value=0.0, value=5.0)
    carbs = st.number_input("Carbs (g)", min_value=0.0, value=30.0)
    fat = st.number_input("Fat (g)", min_value=0.0, value=3.0)
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    date = st.date_input("Date", datetime.today())
    time_ = st.time_input("Time", datetime.now().time())

    if st.button("Log Food Entry"):
        if not food_items:
            st.error("Please enter food items.")
            return
        entry = {
            "date": date.strftime("%Y-%m-%d"),
            "time": time_.strftime("%H:%M"),
            "food_items": [f.strip() for f in food_items.split(",")],
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "meal_type": meal_type
        }
        insert_food_entry(entry)
        st.session_state.food_entries.insert(0, entry)
        st.success("Food entry logged!")

    df_food = session_to_df('food_entries')
    if not df_food.empty:
        st.subheader("Recent Food Entries")
        st.dataframe(df_food.head(10))


def weight_logger():
    st.title("Weight Logger")
    today = datetime.today().date()
    weight = st.number_input("Weight (kg)", min_value=0.0, format="%.1f")
    context = st.selectbox("Measurement Context", [
        "Wake up", "Before breakfast", "After breakfast", "Before lunch", "After lunch",
        "Before dinner", "After dinner", "Before gym", "After gym", "Before sleep"
    ])
    date = st.date_input("Date", today)
    time_ = st.time_input("Time", datetime.now().time())
    notes = st.text_area("Notes (optional)", "")

    if st.button("Log Weight Entry"):
        entry = {
            "date": date.strftime("%Y-%m-%d"),
            "time": time_.strftime("%H:%M"),
            "weight": weight,
            "context": context,
            "notes": notes
        }
        insert_weight_entry(entry)
        st.session_state.weight_entries.insert(0, entry)
        st.success("Weight entry logged!")

    df_weight = session_to_df('weight_entries')
    if not df_weight.empty:
        st.subheader("Recent Weight Entries")
        st.dataframe(df_weight.head(10))
        df_sorted = df_weight.sort_values(["date","time"], ascending=[False, False])
        latest_w = df_sorted.iloc[0]['weight']
        st.write(f"Latest weight: {latest_w} kg")


def sleep_tracker():
    st.title("Sleep Tracker")
    date = st.date_input("Date", datetime.today())
    sleep_time = st.time_input("Sleep Time", time(22,0))
    wake_time = st.time_input("Wake Time", time(6,0))
    quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)
    notes = st.text_area("Sleep Notes (optional)", "")

    if st.button("Log Sleep Entry"):
        sleep_dt = datetime.combine(date, sleep_time)
        wake_dt = datetime.combine(date, wake_time)
        if wake_dt <= sleep_dt:
            from datetime import timedelta
            wake_dt += timedelta(days=1)
        duration = (wake_dt - sleep_dt).total_seconds() / 3600
        entry = {
            "date": date.strftime("%Y-%m-%d"),
            "sleep_time": sleep_time.strftime("%H:%M"),
            "wake_time": wake_time.strftime("%H:%M"),
            "duration": round(duration, 2),
            "quality": quality,
            "notes": notes
        }
        insert_sleep_entry(entry)
        st.session_state.sleep_entries.insert(0, entry)
        st.success("Sleep entry logged!")

    df_sleep = session_to_df('sleep_entries')
    if not df_sleep.empty:
        st.subheader("Recent Sleep Entries")
        st.dataframe(df_sleep.head(10))

# --- Advanced Analytics ---

def advanced_analytics():
    st.title("Advanced Analytics & Trends")

    # Fetch and prepare data
    df_food = session_to_df('food_entries')
    df_weight = session_to_df('weight_entries')
    df_sleep = session_to_df('sleep_entries')

    # Convert date columns to datetime, add sorting
    def prep_df(df, date_col='date'):
        if df.empty:
            return df
        df[date_col] = pd.to_datetime(df[date_col])
        return df.sort_values(date_col).reset_index(drop=True)

    df_food = prep_df(df_food)
    df_weight = prep_df(df_weight)
    df_sleep = prep_df(df_sleep)

    if df_weight.empty:
        st.warning("No weight data to analyze.")
        return

    # Sidebar filters for date range
    st.sidebar.header("Analytics Date Range")
    min_date = min(df_weight['date'].min(), df_food['date'].min() if not df_food.empty else df_weight['date'].min())
    max_date = max(df_weight['date'].max(), df_food['date'].max() if not df_food.empty else df_weight['date'].max())
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    if start_date > end_date:
        st.sidebar.error("Start date must be before end date")
        return

    def date_filter(df, start, end):
        if df.empty:
            return df
        return df[(df['date'] >= pd.to_datetime(start)) & (df['date'] <= pd.to_datetime(end))]

    food_df_filt = date_filter(df_food, start_date, end_date)
    weight_df_filt = date_filter(df_weight, start_date, end_date)
    sleep_df_filt = date_filter(df_sleep, start_date, end_date)

    # --- Weight trend with rolling average ---
    weight_df_filt = weight_df_filt.sort_values('date')
    weight_df_filt['rolling_avg'] = weight_df_filt['weight'].rolling(window=7, min_periods=1).mean()

    fig_weight = px.line(weight_df_filt, x='date', y=['weight', 'rolling_avg'],
                         labels={'value':'Weight (kg)', 'date':'Date'},
                         title='Weight and 7-Day Rolling Average')
    st.plotly_chart(fig_weight, use_container_width=True)

    # --- Nutrition trend ---
    if not food_df_filt.empty:
        fig_nutrition = px.line(food_df_filt, x='date', y=['calories', 'protein', 'carbs', 'fat'],
                                labels={'value':'Amount', 'date':'Date'},
                                title='Daily Nutritional Intake Over Time')
        st.plotly_chart(fig_nutrition, use_container_width=True)
    else:
        st.info("No food data in the selected date range.")

    # --- Correlation analysis ---
    if not food_df_filt.empty and len(weight_df_filt) >= 2:
        weight_corr_df = weight_df_filt.copy()
        weight_corr_df['weight_change'] = weight_corr_df['weight'].diff()
        corr_df = food_df_filt.set_index('date').join(weight_corr_df.set_index('date')['weight_change'], how='inner').reset_index()
        corr_data = corr_df[['calories', 'protein', 'carbs', 'fat', 'weight_change']].corr()
        corr_fig = ff.create_annotated_heatmap(
            z=corr_data.values,
            x=list(corr_data.columns),
            y=list(corr_data.columns),
            colorscale='Viridis',
            showscale=True
        )
        st.plotly_chart(corr_fig, use_container_width=True)
        st.markdown("**Correlation Interpretation:** Positive values imply a direct relationship; negative values imply inverse relationship.")
    else:
        st.info("Not enough data to perform correlation analysis.")

    # --- Weight forecasting ---
    if len(weight_df_filt) >= 30:
        ts_data = weight_df_filt.set_index('date').resample('D').mean().fillna(method='ffill')['weight']
        model = ExponentialSmoothing(ts_data, trend='add', seasonal=None)
        fit = model.fit()
        forecast = fit.forecast(14)

        fig_forecast = px.line(title='Weight Forecast - Next 14 Days')
        fig_forecast.add_scatter(x=ts_data.index, y=ts_data.values, mode='lines+markers', name='Actual')
        fig_forecast.add_scatter(x=forecast.index, y=forecast.values, mode='lines+markers', name='Forecast')
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.info("At least 30 days of weight data required for forecasting.")

    # --- Meal pattern (average calories by day of week) ---
    if not food_df_filt.empty:
        food_df_filt['day_of_week'] = food_df_filt['date'].dt.day_name()
        calorie_day_avg = food_df_filt.groupby('day_of_week')['calories'].mean().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        fig_meal = px.bar(x=calorie_day_avg.index, y=calorie_day_avg.values,
                          labels={'x':'Day of Week', 'y':'Avg Calories'}, title='Average Calories By Day of Week')
        st.plotly_chart(fig_meal, use_container_width=True)

    # --- Sleep analysis ---
    if not sleep_df_filt.empty:
        sleep_df_filt = sleep_df_filt.sort_values('date')
        sleep_df_filt['duration_rolling'] = sleep_df_filt['duration'].rolling(7, min_periods=1).mean()
        fig_sleep = px.line(sleep_df_filt, x='date', y=['duration', 'duration_rolling'],
                            labels={'value':'Hours', 'date':'Date'}, title='Sleep Duration and 7-Day Rolling Avg')
        st.plotly_chart(fig_sleep, use_container_width=True)

        fig_quality = px.histogram(sleep_df_filt, x='quality', nbins=5,
                                   labels={'quality': 'Sleep Quality'}, title='Sleep Quality Distribution', marginal='box')
        st.plotly_chart(fig_quality, use_container_width=True)
    else:
        st.info("No sleep data in the selected date range.")

    # --- Data export ---
    st.header("Export Data")
    if st.button("Download Food Data CSV"):
        csv_food = food_df_filt.to_csv(index=False).encode('utf-8')
        st.download_button("Download Food Data CSV", data=csv_food, file_name="food_data.csv", mime="text/csv")

    if st.button("Download Weight Data CSV"):
        csv_weight= weight_df_filt.to_csv(index=False).encode('utf-8')
        st.download_button("Download Weight Data CSV", data=csv_weight, file_name="weight_data.csv", mime="text/csv")

    if st.button("Download Sleep Data CSV"):
        csv_sleep = sleep_df_filt.to_csv(index=False).encode('utf-8')
        st.download_button("Download Sleep Data CSV", data=csv_sleep, file_name="sleep_data.csv", mime="text/csv")


# --- Main App Navigation ---

if page == "Food Tracker":
    food_tracker()
elif page == "Weight Logger":
    weight_logger()
elif page == "Sleep Tracker":
    sleep_tracker()
else:
    advanced_analytics()
