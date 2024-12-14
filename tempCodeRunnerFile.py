import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import geopy
from geopy.geocoders import Nominatim
import os

# User Authentication Mock Database
users_db = {"admin": "password123"}  # Replace with real database or authentication system

# Save user data in Excel and PDF
def save_data_to_excel(user_data, filename="user_data.xlsx"):
    df = pd.DataFrame(user_data)
    df.to_excel(os.path.join("C:/Users/vadiraj/OneDrive/Desktop/Hackthon", filename), index=False)

def save_data_to_pdf(user_data, filename="user_data.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for key, value in user_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    
    pdf.output(os.path.join("C:/Users/vadiraj/OneDrive/Desktop/Hackthon", filename))

# User Authentication Functions
def signup(username, password):
    if username in users_db:
        st.error("User already exists. Please log in.")
    else:
        users_db[username] = password
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.success("Signup successful! You are now logged in.")

def login(username, password):
    if username in users_db and users_db[username] == password:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")

# Simulated API Data Fetch Functions
def get_weather(location, month):
    weather_data = {
        "Summer": "Hot and Dry",
        "Winter": "Cold and Snowy",
        "Spring": "Mild and Pleasant",
        "Autumn": "Cool and Windy"
    }
    if month in [12, 1, 2]:
        return weather_data["Winter"]
    elif month in [3, 4, 5]:
        return weather_data["Spring"]
    elif month in [6, 7, 8]:
        return weather_data["Summer"]
    else:
        return weather_data["Autumn"]

def get_festivals(location, month):
    # Simulate festivals based on the region (e.g., based on India)
    festivals = {
        "January": ["Pongal", "Makar Sankranti"],
        "August": ["Independence Day", "Raksha Bandhan"]
    }
    return festivals.get(str(month), [])

def detect_location_india(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return location.address
    else:
        return "Location not found"

def generate_grocery_data(weather, festival):
    # Simulate grocery suggestions based on weather and festival
    groceries = {
        "Winter": {"Wheat": 30, "Rice": 25, "Oats": 15, "Soup": 20},
        "Summer": {"Watermelon": 50, "Lemon": 20, "Tomato": 30, "Rice": 25},
        "Spring": {"Spinach": 30, "Carrot": 20, "Milk": 25, "Banana": 15},
        "Autumn": {"Pumpkin": 40, "Potato": 35, "Apple": 20, "Ginger": 25},
    }

    selected_items = groceries.get(weather, {})
    # Adjust quantity based on festival (just a simple model for demonstration)
    if "Pongal" in festival:
        selected_items["Rice"] += 10
    if "Independence Day" in festival:
        selected_items["Wheat"] += 5

    return selected_items

# Main Application
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("Welcome to Retail Inventory Forecasting")
    st.subheader("Signup or Login to continue")

    option = st.selectbox("Select an option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        if st.button("Signup"):
            signup(username, password)
            st.experimental_rerun()  # Re-run after signup to load the main page
    else:
        if st.button("Login"):
            login(username, password)
            st.experimental_rerun()  # Re-run after login to load the main page
else:
    # Main Page after Login
    st.title(f"Welcome, {st.session_state['username']}!")
    st.sidebar.header("User Input")

    # User inputs
    location = st.sidebar.text_input("Enter your location:")
    future_month = st.sidebar.number_input("Enter future month (1-12):", min_value=1, max_value=12, step=1)
    future_year = st.sidebar.number_input("Enter future year:", min_value=2023, max_value=2100, step=1)

    if location:
        weather = get_weather(location, future_month)
        festival = get_festivals(location, future_month)

        st.write("### External Factors")
        st.write(f"Weather Condition: {weather}")
        st.write(f"Festival: {festival}")

        # Generate grocery interest data
        grocery_data = generate_grocery_data(weather, festival)
        st.write("### Suggested Grocery Items with Prices")
        grocery_df = pd.DataFrame(list(grocery_data.items()), columns=["Item", "Price"])
        st.dataframe(grocery_df)

        # Visualization
        st.write("### Price Distribution")
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))

        sns.histplot(grocery_df["Price"], bins=10, kde=True, ax=ax[0])
        ax[0].set_title("Price Histogram")
        ax[0].set_xlabel("Price")
        ax[0].set_ylabel("Frequency")

        grocery_df.set_index("Item")["Price"].plot.pie(ax=ax[1], autopct='%1.1f%%', startangle=140)
        ax[1].set_title("Price Distribution by Item")
        ax[1].set_ylabel("")

        st.pyplot(fig)

        # Save Data and Verification
        save_data = st.sidebar.checkbox("Save data to Excel/PDF")

        if save_data:
            user_data = {
                "Location": location,
                "Weather": weather,
                "Festival": festival,
                "Grocery Data": grocery_data
            }
            save_data_to_excel(user_data, "grocery_data.xlsx")
            save_data_to_pdf(user_data, "grocery_data.pdf")
            st.success("Data saved to Excel and PDF successfully!")

        st.write("### Business Insights")
        st.write(f"- Focus on items like {', '.join(grocery_data.keys())} based on weather and festival.")
        st.write(f"- Prepare for increased demand during {', '.join(festival)} festivals.")
        st.write(f"- Factor in weather conditions: {weather}.")