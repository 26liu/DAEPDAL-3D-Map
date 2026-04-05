import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Global Page Configuration
st.set_page_config(page_title="Qing Xuan Tan Wei - Atmospheric Monitoring Platform", layout="wide")

# 2. Main Page Title
st.title("🚁 Qing Xuan Tan Wei - 3D Local Air Diagnostics Platform")
st.markdown(
    "This system presents multidimensional meteorological and spatial pollution data collected by the tilt-rotor UAV (VTOL) during flight."
)

# 3. Load Data
@st.cache_data
def load_data():
    # Using relative path to ensure compatibility with GitHub and Streamlit Cloud
    df = pd.read_csv("Simulated_UAV_Meteorological_Data.csv")

    # Rename original Chinese columns to standard English labels for tooltips and data table
    rename_dict = {
        '标准时间': 'Timestamp',
        '经度(Longitude)': 'Longitude',
        '纬度(Latitude)': 'Latitude',
        '高度(Altitude_m)': 'Altitude (m)',
        '大气温度(℃)': 'Temperature (°C)',
        '大气湿度(%)': 'Humidity (%)',
        '大气压(hPa)': 'Atmos. Pressure (hPa)',
        '工况PM2.5(ug/m3)': 'PM2.5 (µg/m³)',
        '工况PM10(ug/m3)': 'PM10 (µg/m³)',
        'NO2(ug/m3)': 'NO2 (µg/m³)',
        'SO2(ug/m3)': 'SO2 (µg/m³)'
    }
    df.rename(columns=rename_dict, inplace=True)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Data file not found. Please check the CSV file path!")
    st.stop()

# Downsample the data slightly to ensure smooth rendering
df_sample = df.iloc[::5, :]

# 4. Sidebar Control Panel
# Insert Team Logo at the top of the sidebar
try:
    # use_container_width=True makes the image auto-fit the sidebar width
    st.sidebar.image("logo.jpg", use_container_width=True)
except FileNotFoundError:
    # Fail silently if the image is missing to prevent app crash
    pass

st.sidebar.header("⚙️ Flight Parameters & Data Settings")
st.sidebar.markdown("Please select the meteorological/pollution indicator to render on the 3D trajectory:")

# Available metrics using the renamed English columns
available_metrics = [
    'Temperature (°C)',
    'Humidity (%)',
    'Atmos. Pressure (hPa)',
    'PM2.5 (µg/m³)',
    'PM10 (µg/m³)',
    'NO2 (µg/m³)',
    'SO2 (µg/m³)'
]

selected_metric = st.sidebar.selectbox("Select Data Type", available_metrics)

# 5. Dynamic 3D Plot Rendering
st.subheader(f"Current View: {selected_metric} 3D Spatial Heatmap")

fig = px.scatter_3d(
    df_sample,
    x='Longitude',
    y='Latitude',
    z='Altitude (m)',
    color=selected_metric,
    color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.85,
    labels={selected_metric: selected_metric} # Ensure correct hover tooltip text
)

# Remove marker borders for a smoother color blend
fig.update_traces(marker=dict(size=4, line=dict(width=0)))

# Configure minimalist scientific theme
fig.update_layout(
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Altitude (m)',
        bgcolor='white',
        xaxis=dict(backgroundcolor='white', gridcolor='#E5E5E5', showbackground=True, zerolinecolor='#E5E5E5'),
        yaxis=dict(backgroundcolor='white', gridcolor='#E5E5E5', showbackground=True, zerolinecolor='#E5E5E5'),
        zaxis=dict(backgroundcolor='white', gridcolor='#E5E5E5', showbackground=True, zerolinecolor='#E5E5E5')
    ),
    paper_bgcolor='white',
    font=dict(color='#333333'),
    margin=dict(l=0, r=0, b=0, t=0),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# 6. Raw Data Table Expander
with st.expander("📊 View Raw Data Log"):
    st.dataframe(df[['Timestamp', 'Longitude', 'Latitude', 'Altitude (m)', selected_metric]].head(50))
