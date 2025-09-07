import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from PIL import Image
import io

st.set_page_config(page_title="Weight Loss Tracker", layout="wide")

# Initialize session state for persistent data
if 'food_entries' not in st.session_state:
    st.session_state.food_entries = []
if 'weight_entries' not in st.session_state:
    st.session_state.weight_entries = []
if 'sleep_entries' not in st.session_state:
    st.session_state.sleep_entries = []

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Food Tracker", "Weight Logger", "Sleep Tracker", "Analytics"])

def display_food_tracker():
    st.title("Food Tracker")
    uploaded_file = st.file_uploader("Upload food photo", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Photo", use_column_width=True)
        # MOCK food items and nutrition for demo
        food_items = st.text_input("Detected food items (comma separated)", "Apple, Banana")
        calories = st.number_input("Calories", min_value=0, value=250)
        protein = st.number_input("Protein (g)", min_value=0.0, value=5.0)
        carbs = st.number_input("Carbs (g)", min_value=0.0, value=30.0)
        fat = st.number_input("Fat (g)", min_value=0.0, value=3.0)
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        date = st.date_input("Date", datetime.today())
        time_ = st.time_input("Time", datetime.now().time())
        if st.button("Log Food Entry"):
            st.session_state.food_entries.append({
                "date": date.strftime("%Y-%m-%d"),
                "time": time_.strftime("%H:%M"),
                "food_items": [item.strip() for item in food_items.split(",")],
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "meal_type": meal_type
            })
            st.success("Food entry logged!")
    if st.session_state.food_entries:
        df_food = pd.DataFrame(st.session_state.food_entries)
        st.subheader("Recent Food Entries")
        st.dataframe(df_food.tail(10))

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
        st.session_state.weight_entries.append({
            "date": date.strftime("%Y-%m-%d"),
            "time": time_.strftime("%H:%M"),
            "weight": weight,
            "context": context,
            "notes": notes
        })
        st.success("Weight entry logged!")
    if st.session_state.weight_entries:
        df_weight = pd.DataFrame(st.session_state.weight_entries)
        st.subheader("Recent Weight Entries")
        st.dataframe(df_weight.tail(10))
        # Show latest and difference from previous
        df_weight = df_weight.sort_values(by=["date", "time"])
        latest_weight = df_weight.iloc[-1]["weight"]
        st.write(f"Latest weight: {latest_weight} kg")

def display_sleep_tracker():
    st.title("Sleep Tracker")
    date = st.date_input("Date", datetime.today())
    sleep_time = st.time_input("Sleep Time", time(22, 0))
    wake_time = st.time_input("Wake Time", time(6, 0))
    quality = st.slider("Sleep Quality (1-10)", min_value=1, max_value=10, value=7)
    notes = st.text_area("Sleep Notes (optional)", "")
    if st.button("Log Sleep Entry"):
        # Calculate duration in hours
        sleep_dt = datetime.combine(date, sleep_time)
        wake_dt = datetime.combine(date, wake_time)
        if wake_dt <= sleep_dt:
            wake_dt = wake_dt.replace(day=wake_dt.day + 1)
        duration = (wake_dt - sleep_dt).total_seconds() / 3600
        st.session_state.sleep_entries.append({
            "date": date.strftime("%Y-%m-%d"),
            "sleep_time": sleep_time.strftime("%H:%M"),
            "wake_time": wake_time.strftime("%H:%M"),
            "duration": round(duration, 2),
            "quality": quality,
            "notes": notes
        })
        st.success("Sleep entry logged!")
    if st.session_state.sleep_entries:
        df_sleep = pd.DataFrame(st.session_state.sleep_entries)
        st.subheader("Recent Sleep Entries")
        st.dataframe(df_sleep.tail(10))

def display_analytics():
    st.title("Analytics Dashboard")
    col1, col2 = st.columns(2)

    if st.session_state.weight_entries:
        df_weight = pd.DataFrame(st.session_state.weight_entries)
        df_weight["datetime"] = pd.to_datetime(df_weight["date"] + " " + df_weight["time"])
        df_weight = df_weight.sort_values("datetime")
        fig1 = px.line(df_weight, x="datetime", y="weight", title="Weight Over Time")
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

# Page routing
if page == "Food Tracker":
    display_food_tracker()
elif page == "Weight Logger":
    display_weight_logger()
elif page == "Sleep Tracker":
    display_sleep_tracker()
else:
    display_analytics()
