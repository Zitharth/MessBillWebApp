import streamlit as st
import pandas as pd
import os

# File to store data
FILE_PATH = "mess_bill_log.csv"

# Default meal prices
DEFAULT_PRICES = {"Breakfast": 30.0, "Lunch": 60.0, "Dinner": 50.0}


# Function to load existing data
def load_data():
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH, parse_dates=["Date"])
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
        return df
    else:
        return pd.DataFrame(columns=["Date", "Breakfast", "Lunch", "Dinner", "Total"])


# Function to save data
def save_data(df):
    df.to_csv(FILE_PATH, index=False)


# Streamlit UI
st.title("Mess Bill Logger")

# Load existing data
data = load_data()

data["Month"] = data["Date"].dt.strftime("%Y-%m") if not data.empty else None

# Define monthly_totals to avoid NameError
monthly_totals = data.groupby("Month")["Total"].sum().reset_index() if not data.empty else pd.DataFrame(
    columns=["Month", "Total"])

# Display monthly total amounts
if not monthly_totals.empty:
    st.write("### Monthly Mess Bill Summary")
    st.table(monthly_totals)

# Calculate total for the current month
current_month = pd.to_datetime("today").strftime("%Y-%m")
current_month_total = monthly_totals.loc[
    monthly_totals["Month"] == current_month, "Total"].sum() if not monthly_totals.empty else 0
st.write(f"### Total Mess Bill for {current_month}: ₹{current_month_total}")

# Input fields
date = st.date_input("Select Date")
breakfast = st.checkbox("Breakfast")
lunch = st.checkbox("Lunch")
dinner = st.checkbox("Dinner")

# Meal price customization
st.write("### Set Meal Prices")
breakfast_price = float(
    st.number_input("Breakfast Price", min_value=0.0, value=DEFAULT_PRICES["Breakfast"], format="%.2f"))
lunch_price = float(st.number_input("Lunch Price", min_value=0.0, value=DEFAULT_PRICES["Lunch"], format="%.2f"))
dinner_price = float(st.number_input("Dinner Price", min_value=0.0, value=DEFAULT_PRICES["Dinner"], format="%.2f"))

if st.button("Add Entry"):
    total = 0.0  # Ensure total is a float
    if breakfast:
        total += breakfast_price
    if lunch:
        total += lunch_price
    if dinner:
        total += dinner_price

    if total > 0:
        new_entry = pd.DataFrame(
            {"Date": [date], "Breakfast": [int(breakfast)], "Lunch": [int(lunch)], "Dinner": [int(dinner)],
             "Total": [total]})
        data = pd.concat([data, new_entry], ignore_index=True)
        save_data(data)
        st.success("Entry added successfully!")
        st.rerun()
    else:
        st.error("Please select at least one meal.")

# Option to clear bill
clear_bill = st.checkbox("Clear Bill")
if clear_bill and st.button("Reset Bill"):
    if not monthly_totals.empty:
        selected_month = st.selectbox("Select Month to Clear", monthly_totals["Month"].tolist())
        if selected_month != current_month:
            data = data[data["Month"] != selected_month]
            save_data(data)
            st.success(f"Bill for {selected_month} reset successfully!")
            st.rerun()
        else:
            st.error("You cannot clear the bill for the current month.")

# Display data
if not data.empty:
    st.write("### Log of Mess Bills")
    st.dataframe(data.drop(columns=["Month"]))

    # Display count of each meal
    meal_counts = {
        "Breakfast": data["Breakfast"].sum(),
        "Lunch": data["Lunch"].sum(),
        "Dinner": data["Dinner"].sum()
    }
    st.write("### Meal Counts")
    meal_counts_df = pd.DataFrame(list(meal_counts.items()), columns=["Meal", "Count"])
    st.table(meal_counts_df)
