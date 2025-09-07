import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from PIL import Image
import sqlite3
from streamlit_javascript import st_javascript  # Import the JS package for live client time

st.set_page_config(page_title="Weight Loss Tracker", layout="wide")

DB_NAME = 'tracker.db'

# --- Database setup and operations ---

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
    c.execute('''
        INSERT INTO food_entries 
        (date, time, food_items, calories, protein, carbs, fat, meal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (entry['date'], entry['time'], ','.join(entry['food_items']),
          entry['calories'], entry['protein'], entry['carbs'], entry['fat'], entry['meal_type']))
    conn.commit()
    conn.close()

def insert_weight_entry(entry):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO weight_entries 
        (date, time, weight, context, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (entry['date'], entry['time'], entry['weight'], entry['context'], entry['notes']))
    conn.commit()
    conn.close()

def insert_sleep_entry(entry):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sleep_entries 
        (date, sleep_time, wake_time, duration, quality, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (entry['date'], entry['sleep_time'], entry['wake_time'],
          entry['duration'], entry['quality'], entry['notes']))
    conn.commit()
    conn.close()

def load_entries(table_name):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql(f'SELECT * FROM {table_name} ORDER BY date DESC, time DESC', conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# --- Initialize DB and load data to session ---

init_db()

if 'food_entries' not in st.session_state:
    df_food = load_entries('food_entries')
    st.session_state.food_entries = df_food.to_dict(orient='records') if not df_food.empty else []

if 'weight_entries' not in st.session_state:
    df_weight = load_entries('weight_entries')
    st.session_state.weight_entries = df_weight.to_dict(orient='records') if not df_weight.empty else []

if 'sleep_entries' not in st.session_state:
    df_sleep = load_entries('sleep_entries')
    st.session_state.sleep_entries = df_sleep.to_dict(orient='records') if not df_sleep.empty else []

# --- Sidebar navigation ---

page = st.sidebar.selectbox("Navigate", ["Food Tracker", "Weight Logger", "Sleep Tracker", "Analytics"])

# --- Pages ---

def display_food_tracker():
    st.title("Food Tracker")
    uploaded_file = st.file_uploader("Upload food photo", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Photo", use_column_width=True)
        food_items = st.text_input("Detected food items (comma separated)", "Apple, Banana")
        calories = st.number_input("Calories", min_value=0, value=250)
        protein = st.number_input("Protein (g)", min_value=0.0, value=5.0)
        carbs = st.number_input("Carbs (g)", min_value=0.0, value=30.0)
        fat = st.number_input("Fat (g)", min_value=0.0, value=3.0)
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        date = st.date_input("Date", datetime.today())
        time_ = st.time_input("Time", datetime.now().time())
        if st.button("Log Food Entry"):
            entry = {
                "date": date.strftime("%Y-%m-%d"),
                "time": time_.strftime("%H:%M"),
                "food_items": [item.strip() for item in food_items.split(",")],
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "meal_type": meal_type
            }
            insert_food_entry(entry)
            st.session_state.food_entries.insert(0, entry)
            st.success("Food entry logged!")
    if st.session_state.food_entries:
        df_food = pd.DataFrame(st.session_state.food_entries)
        st.subheader("Recent Food Entries")
        st.dataframe(df_food.head(10))

def display_weight_logger():
    st.title("Weight Logger")
    today = datetime.today().date()
    st.write(f"Today: {today}")
    weight = st.number_input("Weight (kg)", min_value=0.0, format="%.1f")
    context = st.selectbox("Measurement Context", [
        "Wake up",
        "Before breakfast",
        "After breakfast",
        "Before lunch",
        "After lunch",
        "Before dinner",
        "After dinner",
        "Before gym",
        "After gym",
        "Before sleep"
    ])
    date = st.date_input("Date", today)
    time_ = st.time_input("Time", datetime.now().time())
    notes = st.text_area("Notes (optional)", "", max_chars=200)
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
    if st.session_state.weight_entries:
        df_weight = pd.DataFrame(st.session_state.weight_entries)
        st.subheader("Recent Weight Entries")
        st.dataframe(df_weight.head(10))
        df_weight_sorted = df_weight.sort_values(by=["date", "time"], ascending=[False, False])
        latest_weight = df_weight_sorted.iloc[0]["weight"]
        st.write(f"Latest weight: {latest_weight} kg")

def display_sleep_tracker():
    st.title("Sleep Tracker")
    date = st.date_input("Date", datetime.today())
    sleep_time = st.time_input("Sleep Time", time(22, 0))
    wake_time = st.time_input("Wake Time", time(6, 0))
    quality = st.slider("Sleep Quality (1-10)", min_value=1, max_value=10, value=7)
    notes = st.text_area("Sleep Notes (optional)", "")
    if st.button("Log Sleep Entry"):
        sleep_dt = datetime.combine(date, sleep_time)
        wake_dt = datetime.combine(date, wake_time)
        if wake_dt <= sleep_dt:
            wake_dt = wake_dt.replace(day=wake_dt.day + 1)
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
    if st.session_state.sleep_entries:
        df_sleep = pd.DataFrame(st.session_state.sleep_entries)
        st.subheader("Recent Sleep Entries")
        st.dataframe(df_sleep.head(10))

def display_analytics():
    st.title("Analytics Dashboard")
    col1, col2 = st.columns(2)

    if st.session_state.weight_entries:
        df_weight = pd.DataFrame(st.session_state.weight_entries)
        df_weight["datetime"] = pd.to_datetime(df_weight["date"] + " " + df_weight["time"])
        df_weight = df_weight.sort_values("datetime")
        fig1 = px.line(df_weight, x="datetime", y="weight", markers=True, title="Weight Over Time")
        col1.plotly_chart(fig1, use_container_width=True)
    else:
        col1.write("No weight data to display")

    if st.session_state.food_entries:
        df_food = pd.DataFrame(st.session_state.food_entries)
        calories_day = df_food.groupby("date").calories.sum().reset_index()
        fig2 = px.bar(calories_day, x="date", y="calories", title="Daily Calorie Intake")
        col2.plotly_chart(fig2, use_container_width=True)
    else:
        col2.write("No food data to display")

    if st.session_state.sleep_entries:
        df_sleep = pd.DataFrame(st.session_state.sleep_entries)
        df_sleep["date"] = pd.to_datetime(df_sleep["date"])
        fig3 = px.line(df_sleep, x="date", y="duration", title="Sleep Duration Over Time")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.write("No sleep data to display")

    st.markdown("---")
    st.subheader("Current Client Device Time (Live)")

    # Live client time using streamlit-javascript
    client_time = st_javascript("new Date().toLocaleString()", key="js_client_time")
    if client_time:
        st.write(client_time)
    else:
        st.write("Fetching client time...")

# --- Page dispatcher ---

if page == "Food Tracker":
    display_food_tracker()
elif page == "Weight Logger":
    display_weight_logger()
elif page == "Sleep Tracker":
    display_sleep_tracker()
else:
    display_analytics()
