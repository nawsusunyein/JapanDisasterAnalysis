import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Japan Earthquake Dashboard",
    page_icon="🌏",
    layout="wide"
)


#Dashboard Title

st.title("Japan Earthquake Analysis Dashboard")
st.markdown(
    """
      Explore earthquake activity across Japan 
      from 2001 to 2018
    """
)

# Load dataset

@st.cache_data
def load_data():
    file_path = (
        Path(__file__).parent
        / "data"
        / "processed"
        / "cleaned_japan_earthquakes_2001_2018.csv"
    )

    df = pd.read_csv(file_path)
    df["time"] = pd.to_datetime(
        df["time"],
        utc=True,
        errors = "coerce"
    )

    df = df.dropna(subset = ["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    return df


# Display Dataset

try:
     df = load_data()
     st.success("Earhtquake dataset loaded successfully!")
     st.subheader("Earthquake Overview")

    #Calculate key statistics
     total_earthquakes = len(df)
     most_active_year  = df["year"].value_counts().idxmax()
     most_active_month = df["month"].value_counts().idxmax()
     average_magnitude = df["mag"].mean()

    #Dsiplay KPI cards
     col1,col2,col3,col4 = st.columns(4)
     with col1:
        st.metric(
            "Total Earthquakes",
            f"{total_earthquakes:,}"
        )

     with col2:
        st.metric(
            "Most Active Year",
            int(most_active_year)
        )
     with col3:
        st.metric(
            "Most Active Month",
            int(most_active_month)
        )

     with col4:
        st.metric(
            "Averaage Magnitude",
            f"{average_magnitude:.2f}"
        )

    #Yearly Earthquake Frquency
     st.subheader("Earthquake Frequency by Year")
     yearly_frequency = (
       df.groupby("year")
         .size()
         .reset_index(name="earthquake_count")
     )

     fig_yearly = px.bar(
         yearly_frequency,
         x="year",
         y="earthquake_count",
         title="Number of Earthquakes per Year",
         labels={
             "year": "Year",
             "earthquake_count": "Number of Earthquakes"
         }
     )

     st.plotly_chart(fig_yearly, use_container_width=True)
   

    #Monthly Earthquake Frquency
     st.subheader("Earthquake Frequency by Month")
     yearly_frequency = (
       df.groupby("month")
         .size()
         .reset_index(name="earthquake_count")
     )

     fig_monthly = px.bar(
         yearly_frequency,
         x="month",
         y="earthquake_count",
         title="Number of Earthquakes per Month",
         labels={
             "year": "Month",
             "earthquake_count": "Number of Earthquakes"
         }
     )

     st.plotly_chart(fig_monthly, use_container_width=True)
     st.subheader("Earthquake Dataset Preview")

     st.dataframe(
        df.head(10),
        use_container_width=True
     )

except FileNotFoundError:
    st.error(
        "Earthquake CSV file not found. Pleaase check the file path"
    )

except Exception as e:
    st.error(f"Error loading dataset:{e}")