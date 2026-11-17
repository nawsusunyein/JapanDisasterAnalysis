import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import calendar

from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from pathlib import Path

st.set_page_config(
    page_title="Japan Earthquake Dashboard",
    page_icon="🌏",
    layout="wide"
)


# Custom CSS 

st.markdown("""
<style>

/* Main dashboard background */
.stApp {
    background-color: #080d18;
    color: #f1f5f9;
}

/* Main content spacing */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #101827;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

/* General text */
.stApp p,
.stApp span,
.stApp label,
.stApp .stMarkdown {
    color: #e2e8f0;
}

/* Dashboard headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #f8fafc;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #151f30;
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 12px;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #38bdf8 !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

/* Metric delta */
[data-testid="stMetricDelta"] {
    color: #4ade80 !important;
}

/* Selectbox background */
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
}

/* Selectbox selected text */
div[data-baseweb="select"] input,
div[data-baseweb="select"] div {
    color: #ffffff !important;
}

/* Selectbox dropdown menu */
div[data-baseweb="popover"] {
    background-color: #1e293b !important;
}

div[data-baseweb="menu"] {
    background-color: #1e293b !important;
}

div[data-baseweb="menu"] * {
    color: #f1f5f9 !important;
}

/* Selectbox and slider titles */
.stSelectbox label,
.stSlider label {
    color: #38bdf8 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Slider */
[data-testid="stSlider"] {
    padding-top: 10px;
}

[data-testid="stSlider"] [data-baseweb="slider"] {
    color: #38bdf8;
}

/* Input boxes */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
}

/* Buttons */
.stButton button {
    background-color: #0e7490 !important;
    color: #ffffff !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 8px;
}

.stButton button:hover {
    background-color: #0369a1 !important;
    color: #ffffff !important;
}

/* Filter container */
.filter-container {
    background-color: #111c2e;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 25px;
}

/* Section titles */
.section-title {
    color: #38bdf8 !important;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 15px;
}

/* Chart container */
.chart-container {
    background-color: #111c2e;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Alert and information boxes */
[data-testid="stAlert"] {
    background-color: #172a40 !important;
    color: #f1f5f9 !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #94a3b8 !important;
    padding: 25px 0 10px 0;
    border-top: 1px solid #334155;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


#localizations
translations = {
      "EN": {
          "title":"Japan Earthquake Analysis Dashboard",
          "filters":"Earthquake Filters",
          "year":"Selected Year",
          "month":"Selected Month",
          "magnitude":"Selected Magnitude",
          "region":"Selected Region",
          "overview":"Earthquake Overview",
          "total":"Total Earthquakes",
          "average":"Average Magnitude",
          "active_year":"Most Active Year",
          "active_month":"Most Active Month",
          "map":"Earthquake Location Map",
          "year_chart":"Number of Earthquakes per Year",
          "month_chart":"Number of Earthquakes per Month",
          "region_chart":"Number of Earthquakes by Region",
          "magnitude_chart":"Number of Earthquakes by Magnitude",
          "all":"All",
          "footer":"Analysed by Naw Su Su Nyein",
          "no_data":"No earthquake records found for the selected filters.",
          "earthquake_data_visualization": "Earthquake Data Visualization",
          "earthquake_filtered_records":"Displaying 11,904 earthquake locations out of 11,904 filtered records.",
          "earthquake_analysis_dashboard":"Japan Earthquake Analysis Dashboard"
          
      },
      "JP" : {
          "title":"日本の地震分析ダッシュボード",
          "filters":"地震フィルター",
          "year":"年を選択",
          "month":"月を選択",
          "magnitude":"マグニチュードを選択",
          "region":"地域を選択",
          "overview":"地震の概要",
          "total":"地震の総数",
          "average":"平均マグニチュード",
          "active_year":"最も地震が多い年",
          "active_month":"最も地震が多い月",
          "map":"地震発生場所マップ",
          "year_chart":"年別の地震発生数",
          "month_chart":"月別の地震発生数",
          "region_chart":"地域別の地震発生数",
          "magnitude_chart":"マグニチュード別の地震発生数",
          "all":"すべて",
          "footer":"分析者：Naw Su Su Nyein",
          "no_data":"選択した条件に該当する地震データはありません。",
          "earthquake_data_visualization": "地震データの可視化",
          "earthquake_filtered_records":"絞り込み後の11,904件のデータのうち、11,904件の地震発生地点を表示しています。",
          "earthquake_analysis_dashboard":"日本の地震分析ダッシュボード"
      },
      "MM" : {
          "title":"ဂျပန်နိုင်ငံ ငလျင်ဆိုင်ရာ ခွဲခြမ်းစိတ်ဖြာမှု Dashboard",
          "filters":"ငလျင် စစ်ထုတ်မှုများ",
          "year":"ခုနှစ် ရွေးချယ်ရန်",
          "month":"လ ရွေးချယ်ရန်",
          "magnitude":"ငလျင်ပြင်းအား ရွေးချယ်ရန်",
          "region":"ဒေသ ရွေးချယ်ရန်",
          "overview":"ငလျင် အကျဉ်းချုပ်",
          "total":"ငလျင် စုစုပေါင်း",
          "average":"ပျမ်းမျှ ငလျင်ပြင်းအား",
          "active_year":"ငလျင်အများဆုံး ဖြစ်ပွားသည့်နှစ်",
          "active_month":"ငလျင်အများဆုံး ဖြစ်ပွားသည့်လ",
          "map":"ငလျင်ဖြစ်ပွားသည့် နေရာမြေပုံ",
          "year_chart":"နှစ်အလိုက် ငလျင်ဖြစ်ပွားမှု",
          "month_chart":"လအလိုက် ငလျင်ဖြစ်ပွားမှု",
          "region_chart":"ဒေသအလိုက် ငလျင်ဖြစ်ပွားမှု",
          "magnitude_chart":"ပြင်းအားအလိုက် ငလျင်ဖြစ်ပွားမှု",
          "all":"အားလုံး",
          "footer":"လေ့လာဆန်းစစ်သူ - Naw Su Su Nyein",
          "no_data":"ရွေးချယ်ထားသော စစ်ထုတ်မှုများအတွက် ငလျင်မှတ်တမ်း မရှိပါ။",
          "earthquake_data_visualization": "ငလျင်ဒေတာ ဖော်ပြခြင်း",
          "earthquake_filtered_records":"စစ်ထုတ်ထားသော မှတ်တမ်း ၁၁,၉၀၄ ခုအနက် ငလျင်ဖြစ်ပွားသည့် တည်နေရာ ၁၁,၉၀၄ ခုကို ပြသထားသည်။",
          "earthquake_analysis_dashboard":"ဂျပန်နိုင်ငံ ငလျင်ဆိုင်ရာ ခွဲခြမ်းစိတ်ဖြာမှု ဒက်ရှ်ဘုတ်"
      }
  }

#Dashboard Title

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

    df = df.dropna(subset = ["time"]).copy()
    
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["latitude"] = pd.to_numeric(
        df["latitude"] , errors = "coerce"
    )
    df["longitude"] = pd.to_numeric(
        df["longitude"], errors="coerce"
    )
    df["mag"] = pd.to_numeric(
        df["mag"], errors="coerce"
    )

    df["region"] = (
         df["place"] 
          .fillna("")
          .astype(str)
          .str.replace(r"^.*?\bof\s+","",regex=True)
          .str.replace(r",\s*Japan$","",regex=True)
          .str.strip()
     )
    
    return df


# Display Dataset

try:
     df = load_data()
    
except FileNotFoundError:
    st.error(
        "Earthquake CSV file not found. Pleaase check the file path"
    )

except Exception as e:
    st.error(f"Error loading dataset:{e}")


#header : title + language

header_col1, header_col2 = st.columns([5,1])

with header_col2:

     language = st.selectbox(
         "Language",
         ["EN","JP","MM"],
         index = 1,
         format_func=lambda x: {
             "EN": "English",
             "JP":"日本語",
             "MM":"မြန်မာ"
         }[x]
     )
     t = translations[language]
with header_col1:

     st.title(t["title"])
st.markdown("---")

#Filter Section

st.markdown(
    f'<p class="section-title">{t["filters"]}</p>',
    unsafe_allow_html = True
)

with st.container(border=True):
    #First row: Year and Month

    filter_col1, filter_col2 = st.columns(2)
    years = sorted(
        df["year"].dropna().unique().astype(int).tolist()
    )

    months = list(range(1,13))

    with filter_col1:
        selected_year = st.selectbox(
            t["year"],
            [t["all"]] + years
        )

    with filter_col2:
        selected_month = st.selectbox(
            t["month"],
            [t["all"]] + months,
            format_func=lambda x: (
                t["all"] if x == t["all"]
                else calendar.month_name[x]
            )
        )

    st.markdown("---")

    #Second row: Magnitude and Region

    filter_col3, filter_col4 = st.columns(2)

    valid_magnitudes = df["mag"].dropna()

    if valid_magnitudes.empty:
        min_mag, max_mag = 0.0, 10.0
    else : 
        min_mag = float(valid_magnitudes.min())
        max_mag = float(valid_magnitudes.max())

    with filter_col3:
        if min_mag == max_mag:
            selected_magnitude = (min_mag, max_mag)
            st.caption(f"{t['magnitude']}:{min_mag:.1f}")
        else :
            selected_magnitude = st.slider(
                t["magnitude"],
                min_value = min_mag,
                max_value = max_mag,
                value=(min_mag, max_mag),
                step=0.1
            )

    with filter_col4:
         regions = sorted(
             df.loc[
                 df["region"] != "",
                 "region"
             ].dropna().unique().tolist()
         )

         selected_region = st.selectbox(
             t["region"],
             [t["all"]] + regions
         )

#Apply Filters

    filtered_df = df.copy()
    if selected_year != t["all"] :
            filtered_df = filtered_df[
              filtered_df["year"] == selected_year
            ]

    if selected_month != t["all"]:
         filtered_df = filtered_df[
             filtered_df["month"] == selected_month
         ]

    if selected_region != t["all"]:
         filtered_df = filtered_df[
           filtered_df["region"] == selected_region
         ]

    filtered_df = filtered_df[
        filtered_df["mag"].between(
            selected_magnitude[0],
            selected_magnitude[1]
        )
    ]

#overview section

st.markdown(
     f'<p class="section-title">{t["overview"]}</p>',
     unsafe_allow_html=True
 )
if filtered_df.empty:
        st.warning(t["no_data"])
        st.stop()
    

#Calculate key statistics
total_earthquakes = len(filtered_df)

average_magnitude = filtered_df["mag"].mean()

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

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric(
            "Total Earthquakes",
            f"{total_earthquakes:,}"
        )

with metric_col2:
    st.metric(
        t["average"],
        f"{average_magnitude:.2f}"
    )

metric_col3, metric_col4 = st.columns(2)
with metric_col3:
    st.metric(
        t["active_year"],
        int(most_active_year)
    )

with metric_col4:
    st.metric(
        t["active_month"],
        most_active_month
    )

st.markdown("---")

#Earthquake map

st.markdown(
    f'<p class="section-title">{t["map"]}</p>',
    unsafe_allow_html=True
)

map_df = filtered_df.copy()
map_df["latitude"] = pd.to_numeric(
  map_df["latitude"],errors = "coerce"
)
map_df["longitude"] = pd.to_numeric(
         map_df["longitude"], errors="coerce"
)
map_df = map_df.dropna(
         subset = ["latitude", "longitude"]
)

if not map_df.empty:
         # default map
         map_center = [36.2, 138.2]
         zoom_level = 5

        # zoom into selected region
         if selected_region != "All Regions":
            map_center = [
                map_df["latitude"].mean(),
                map_df["longitude"].mean()
            ]
            zoom_level = 8

        #Create one map
         earthquake_map = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles="OpenStreetMap"
         )

        #Create marker cluster
         marker_cluster = MarkerCluster().add_to(
            earthquake_map
         )

        #Limit markers for performance
         if len(map_df) > 2000:
            display_df = map_df.sample(
                n=2000,
                random_state=42
            )
         else:
            display_df = map_df

        #Add earthquake markers
         for _, row in display_df.iterrows():
            popup_text=f"""
                <b>Location:</b> {row['place']}<br>
                <b>Date:</b>{row['time']}<br>
                <b>Magnitude:</b>{row['mag']}<br>
                <b>Depth:</b>{row['depth']} km
            """

            folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                radius=5,
                color="red",
                fill=True,
                fill_color="orange",
                fill_opacity=0.7,
                tooltip=str(row["region"]),
                popup=folium.Popup(
                    popup_text,
                    max_width=300
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

st.markdown("---")

#Graph Section

st.markdown(
    f'<p class="section-title">{t["earthquake_data_visualization"]}</p>',
    unsafe_allow_html=True
)

chart_layout = {
    "template": "plotly_dark",
    "paper_bgcolor": "#111c2e",
    "plot_bgcolor": "#111c2e",
    "font": {
        "color":"#ffffff"
    },
    "margin": {
        "l":30,
        "r":20,
        "t":55,
        "b":40
    }
}

#graph 1 : earthquakes per year

yearly_frequency = (
       filtered_df.groupby("year")
         .size()
         .reset_index(name="Earthquakes")
)

fig_year = px.bar(
         yearly_frequency,
         x="year",
         y="Earthquakes",
         title=t["year_chart"],
         labels={
             "year": "Year",
             "Earthquakes": "Number of Earthquakes"
         },
         color="Earthquakes",
         color_continuous_scale="Teal"
)

fig_year.update_layout(
    **chart_layout,
    title_font=dict(
        color="#ffffff",
        size=12
    )
)

#graph 2 : earthquakes per month

monthly_frequency = (
       filtered_df.groupby("month")
         .size()
         .reset_index(name="Earthquakes")
)

fig_month = px.bar(
         monthly_frequency,
         x="month",
         y="Earthquakes",
         title=t["month_chart"],
         labels={
             "month":"Month",
             "Earthquakes":"Number of Earthquakes"
         },
         color="Earthquakes",
         color_continuous_scale = "Teal"
)

fig_month.update_layout(
    **chart_layout,
    title_font=dict(
        color="#ffffff",
        size=12
    )
)

#graph 3: earthquakes by region

region_frequency = (
    filtered_df[
      filtered_df["region"] != ""
    ]
    .groupby("region")
    .size()
    .reset_index(name="Earthquakes")
    .sort_values(
        "Earthquakes",
        ascending  = False
    )
    .head(10)
)

fig_region = px.bar(
    region_frequency.sort_values(
        "Earthquakes",
        ascending = True
    ),
    x="Earthquakes",
    y="region",
    orientation="h",
    title=t["region_chart"],
    color="Earthquakes",
    color_continuous_scale="Viridis"
)

fig_region.update_layout(
    **chart_layout,
    title_font=dict(
        color="#ffffff",
        size=12
    )
)

#graph 4: earthquakes by magnitude
magnitude_df = filtered_df.dropna(
    subset=["mag"]
).copy()

fig_magnitude = px.histogram(
    magnitude_df,
    x="mag",
    nbins=20,
    title=t["magnitude_chart"],
    color_discrete_sequence=['#38bdf8']
)

fig_magnitude.update_layout(
    **chart_layout,
    title_font=dict(
        color="#ffffff",
        size=12
    )
)

#display graphs in two rows
graph_col1,graph_col2 = st.columns(2)

with graph_col1:
    st.plotly_chart(
        fig_year,
        use_container_width = True
    )

with graph_col2:
    st.plotly_chart(
        fig_month,
        use_container_width = True
    )

graph_col3, graph_col4 = st.columns(2)
with graph_col3:
    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

with graph_col4:
    st.plotly_chart(
        fig_magnitude,
        use_container_width = True
    )

#Footer
st.markdown(
    f"""
    <div class="footer">
        {t["footer"]}
        <br>
        {t["earthquake_analysis_dashboard"]}
    </div>
    """,
    unsafe_allow_html = True
)