import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
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

     #Extract unique regions from place column
     regions = sorted(
         df["place"]
          .dropna()
          .astype(str)
          .unique()
     )

     df["region"] = (
         df["place"] 
          .fillna("")
          .astype(str)
          .str.replace(r"^.*?\bof\s+","",regex=True)
          .str.replace(r",\s*Japan$","",regex=True)
          .str.strip()
     )

     regions = sorted(
        df["region"]
          .loc[lambda x: x != ""]
          .dropna()
          .unique()
     )

     #Region Selection
     st.subheader("Select Region")
     selected_region = st.selectbox(
         "Search and select a region",
         options=["All Regions"] + regions,
         index=0,
         help="Type to search for a region"
     )

     #Year and Month Filters
     st.subheader("Filter Earthquake Data")
     col1, col2 = st.columns(2)
     with col1:
        selected_year = st.selectbox(
            "Selected  Year",
            options=["All"] + sorted(df["year"].unique().tolist())
        )

     with col2:
         selected_month = st.selectbox(
             "Select Month",
             options=["All"] + list(range(1,13))
         )

     
     #Apply Filters
     filtered_df = df.copy()
     if selected_year != "All":
         filtered_df = filtered_df[
           filtered_df["year"] == selected_year
         ]

     if selected_month != "All":
         filtered_df = filtered_df[
             filtered_df["month"] == selected_month
         ]

     if selected_region != "All Regions":
         filtered_df = filtered_df[
           filtered_df["region"] == selected_region
         ]

     st.write(
         f"Earthquakes found:{len(filtered_df):,}"
     )

     st.subheader("Earthquake Overview")

    #Calculate key statistics
     total_earthquakes = len(filtered_df)
     most_active_year  = (
         filtered_df["year"].value_counts().idxmax()
         if not filtered_df.empty else "N/A"
     )

     most_active_month = (
         filtered_df["month"].value_counts().idxmax()
         if not filtered_df.empty else "N/A"
     )

     average_magnitude = (
         filtered_df["mag"].mean()
         if not filtered_df.empty else 0
     )

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
       filtered_df.groupby("year")
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

     fig_yearly.update_xaxes(
         type="category"
     )
    
     st.plotly_chart(fig_yearly, use_container_width=True)
   

    #Monthly Earthquake Frquency
     st.subheader("Earthquake Frequency by Month")
     yearly_frequency = (
       filtered_df.groupby("month")
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

     fig_monthly.update_xaxes(
         type="category",
         tickmode="linear",
         dtick=1
     )

    
     st.plotly_chart(fig_monthly, use_container_width=True)

     #Interactive Earthquake Map
     st.subheader("Earthquake Locations in Japan")
    
     if not filtered_df.empty: 
         earthquake_map = folium.Map(
             location=[36.2, 138.2],
             zoom_start=5,
             titles = "CartoDB position"
         )

     marker_cluster = MarkerCluster().add_to(earthquake_map)

    #Limit markers for better performance
     map_df = filtered_df

     if len(map_df) > 2000 :
        map_df = map_df.sample(
            n = 2000,
            random_state = 42
        )
     for _, row in map_df.iterrows():
        popup_text = f"""
            <b>Location:</b>{row['place']}<br>
            <b>Date:</b>{row['time']}<br>
            <b>Magnitude:</b>{row['mag']}<br>
            <b>Depth:</b>{row['depth']} km
        """

        folium.CircleMarker(
            location = [
                row["latitude"],
                row["longitude"]
            ],
            tooltip=str(row["region"]),
            radius =  5,
            color = "red",
            fill = True,
            fill_color = "orange",
            fill_opacity = 0.7,
            popup = folium.Popup(
                popup_text ,
                max_width = 300
            )
        ).add_to(marker_cluster)

        folium_static(
            earthquake_map,
            width= None,
            height=600
        )

        st.caption(
            f"Displaying {len(map_df):,} earthquake locations"
            f"out of {len(filtered_df):,} filtered records."
        )
     else :
        st.warning("No earthquake records found for the selected filters")

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