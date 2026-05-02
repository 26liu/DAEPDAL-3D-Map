import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import scipy.interpolate as spi
import math
import os

st.set_page_config(page_title="Plateforme D.Æᵖ.D.A.L.", layout="wide")

# ==========================================
# 1. 多语言字典配置 (Multilingual Configuration)
# ==========================================
# 【修改注记】：将 H2 标题中的巡航高度阈值从 120m 调整为 40m，以匹配新的 45m 基准巡航高度
t_dict = {
    'Français': {
        'title': "D.Æᵖ.D.A.L. - Plateforme de Diagnostic de l'Air Local 3D",
        'desc': "Ce système présente les données météorologiques et de pollution spatiale multidimensionnelles collectées par le drone à aile pivotante (VTOL).",
        'err_file': "⚠️ Fichier introuvable. Veuillez vérifier le chemin du fichier CSV.",
        'lang': "🌐 Langue / Language / 语言",
        'params': "⚙️ Paramètres",
        'sel_metric': "Sélectionner l'indicateur",
        'metrics': ['Température (°C)', 'Humidité (%)', 'Pression Atmos. (hPa)', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'SO2 (µg/m³)'],
        'h1': "1. Vue 3D globale : ",
        'h2': "2. Cartographie 2D de Zone (Croisière > 40m)",
        'warn_2d': "Aucune donnée valide pour {} dans cette zone.",
        'h3': "3. Profils Verticaux : Histogrammes Thermiques",
        'p_a': "**📍 Profil A : Décollage / Atterrissage**",
        'p_b': "**📍 Profil B : Sondage Vertical**",
        'lon': 'Longitude', 'lat': 'Latitude', 'alt': 'Altitude (m)'
    },
    'English': {
        'title': "D.Æᵖ.D.A.L. - 3D Local Air Diagnostic Platform",
        'desc': "This system presents multidimensional meteorological and spatial pollution data collected by the tilt-rotor drone (VTOL).",
        'err_file': "⚠️ File not found. Please check the CSV file path.",
        'lang': "🌐 Langue / Language / 语言",
        'params': "⚙️ Parameters",
        'sel_metric': "Select the indicator",
        'metrics': ['Temperature (°C)', 'Humidity (%)', 'Atmos Pressure (hPa)', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'SO2 (µg/m³)'],
        'h1': "1. Global 3D View: ",
        'h2': "2. 2D Zone Mapping (Cruise > 40m)",
        'warn_2d': "No valid data for {} in this zone.",
        'h3': "3. Vertical Profiles: Thermal Histograms",
        'p_a': "**📍 Profile A: Takeoff / Landing**",
        'p_b': "**📍 Profile B: Vertical Sounding**",
        'lon': 'Longitude', 'lat': 'Latitude', 'alt': 'Altitude (m)'
    },
    '中文': {
        'title': "D.Æᵖ.D.A.L. - 三维局部空气环境诊断平台",
        'desc': "该系统展示了倾转旋翼无人机 (VTOL) 在飞行过程中采集的多维度气象与空间污染数据。",
        'err_file': "⚠️ 找不到文件。请确保 CSV 文件与代码在同一目录下。",
        'lang': "🌐 Langue / Language / 语言",
        'params': "⚙️ 参数设置",
        'sel_metric': "选择数据指标",
        'metrics': ['温度 (°C)', '湿度 (%)', '气压 (hPa)', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'SO2 (µg/m³)'],
        'h1': "1. 3D 全景视图：",
        'h2': "2. 二维区域热力图 (巡航高度 > 40m)",
        'warn_2d': "该区域无 {} 的有效数据。",
        'h3': "3. 垂直剖面：热力直方图",
        'p_a': "**📍 剖面 A：起飞与降落**",
        'p_b': "**📍 剖面 B：垂直定点探测**",
        'lon': '经度', 'lat': '纬度', 'alt': '高度 (m)'
    }
}

lang = st.sidebar.radio(t_dict['Français']['lang'], ['Français', 'English', '中文'], index=0)
t = t_dict[lang]

st.title(t['title'])
st.markdown(t['desc'])

# ==========================================
# 2. 数据加载与预处理 (Data Loading & Preprocessing)
# ==========================================
@st.cache_data
def load_data():
    file_path = "UAV_Meteorological_Data_20260503_Realistic_new2.csv"
    df = pd.read_csv(file_path)

    rename_dict = {
        '标准时间': 'Horodatage',
        '经度(Longitude)': 'Longitude',
        '纬度(Latitude)': 'Latitude',
        '高度(Altitude_m)': 'Altitude (m)',
        '大气温度(℃)': 'Température (°C)',
        '大气湿度(%)': 'Humidité (%)',
        '大气压(hPa)': 'Pression Atmos. (hPa)',
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
    st.error(t['err_file'])
    st.stop()

logo_path = "logo.jpg"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.header(t['params'])
base_metrics = [
    'Température (°C)', 'Humidité (%)', 'Pression Atmos. (hPa)',
    'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'SO2 (µg/m³)'
]
display_metrics = t['metrics']
display_to_base = dict(zip(display_metrics, base_metrics))

selected_display = st.sidebar.selectbox(t['sel_metric'], display_metrics)
selected_metric = display_to_base[selected_display]

df_sample = df

# ==========================================
# 3. 3D 全景视图渲染 (Global 3D View Rendering)
# ==========================================
st.subheader(f"{t['h1']}{selected_display}")

fig_3d = px.scatter_3d(
    df_sample, x='Longitude', y='Latitude', z='Altitude (m)',
    color=selected_metric, color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.7,
    labels={'Longitude': t['lon'], 'Latitude': t['lat'], 'Altitude (m)': t['alt'], selected_metric: selected_display}
)
fig_3d.update_traces(marker=dict(size=3, line=dict(width=0)))
fig_3d.update_layout(
    scene=dict(
        xaxis_title=t['lon'], yaxis_title=t['lat'], zaxis_title=t['alt'],
        bgcolor='white'
    ),
    paper_bgcolor='white', height=600, margin=dict(l=0, r=0, b=0, t=0)
)
st.plotly_chart(fig_3d, use_container_width=True)

st.markdown("---")

# ==========================================
# 4. 二维区域热力图 (2D Zone Heatmap)
# ==========================================
st.subheader(t['h2'])

# 【核心修改 1】：过滤条件适配新的巡航高度。由于新轨迹巡航在 45m 左右，提取大于 40m 的平飞阶段数据
df_fw_cruise = df[df['Altitude (m)'] > 40.0]
df_valid_cruise = df_fw_cruise.dropna(subset=[selected_metric])

if not df_valid_cruise.empty:
    lons = df_valid_cruise['Longitude'].values
    lats = df_valid_cruise['Latitude'].values
    vals = df_valid_cruise[selected_metric].values

    grid_lon, grid_lat = np.mgrid[lons.min():lons.max():100j, lats.min():lats.max():100j]

    # 三次样条插值算法 (Cubic Spline Interpolation) 进行空间平滑
    grid_z = spi.griddata((lons, lats), vals, (grid_lon, grid_lat), method='cubic')
    grid_z_fill = spi.griddata((lons, lats), vals, (grid_lon, grid_lat), method='nearest')
    grid_z = np.where(np.isnan(grid_z), grid_z_fill, grid_z)

    grid_z = np.clip(grid_z, a_min=vals.min(), a_max=vals.max())

    fig_contour = go.Figure(data=go.Contour(
        x=np.linspace(lons.min(), lons.max(), 100),
        y=np.linspace(lats.min(), lats.max(), 100),
        z=grid_z.T,
        colorscale='RdYlBu_r',
        line=dict(width=0),
        contours=dict(showlines=False, coloring='heatmap'),
        colorbar=dict(title=selected_display)
    ))

    fig_contour.update_layout(
        xaxis_title=t['lon'], yaxis_title=t['lat'],
        plot_bgcolor='white', height=500, margin=dict(l=0, r=0, b=0, t=30)
    )
    st.plotly_chart(fig_contour, use_container_width=True)
else:
    st.warning(t['warn_2d'].format(selected_display))

st.markdown("---")

# ==========================================
# 5. 垂直剖面热力直方图 (Vertical Profile Histograms)
# ==========================================
st.subheader(t['h3'])

lon_origin, lat_origin = df['Longitude'].iloc[0], df['Latitude'].iloc[0]

# 【一致性修改】：将纬度基准对齐为底层生成的坐标基准 30.365800（原为 30.4115346），确保距离计算更精确
base_lat = 30.365800
lat_m_per_deg = 111320.0
lon_m_per_deg = 111320.0 * math.cos(math.radians(base_lat))

dist_to_origin = np.sqrt(
    ((df['Longitude'] - lon_origin) * lon_m_per_deg) ** 2 + ((df['Latitude'] - lat_origin) * lat_m_per_deg) ** 2)

# 【核心修改 2】：剖面 B（垂直探测深潜点）识别逻辑变更。
# 由于深潜谷底目前是 20m 左右，寻找距离起点最远且高度低于 30m 的点作为探测井中心
mask_dive = df['Altitude (m)'] < 30.0
idx_dive = dist_to_origin[mask_dive].idxmax()
lon_dive = df.loc[idx_dive, 'Longitude']
lat_dive = df.loc[idx_dive, 'Latitude']

df_a = df[dist_to_origin < 100.0].copy()
df_b = df[np.sqrt(((df['Longitude'] - lon_dive) * lon_m_per_deg)**2 + ((df['Latitude'] - lat_dive) * lat_m_per_deg)**2) < 100.0].copy()

def plot_vertical_heat_strip(df_subset, point_name):
    if df_subset.empty:
        return None

    df_clean = df_subset.dropna(subset=[selected_metric])
    if df_clean.empty:
        return None

    df_clean['alt_bin'] = df_clean['Altitude (m)'].round(0)
    v_profile = df_clean.groupby('alt_bin')[selected_metric].mean().reset_index()

    # 【核心修改 3】：坐标轴高度映射压缩。生成 0 到 50 米的高度网格阵列，取代原先的 0 到 150 米
    all_altitudes = np.arange(0, 51, 1)
    full_profile = pd.DataFrame({'alt_bin': all_altitudes})
    final_data = pd.merge(full_profile, v_profile, on='alt_bin', how='left')

    fig = go.Figure(data=go.Heatmap(
        z=final_data[selected_metric].values.reshape(-1, 1),
        x=[point_name],
        y=final_data['alt_bin'],
        colorscale='RdYlBu_r',
        showscale=True,
        colorbar=dict(title=selected_display),
        connectgaps=False
    ))

    # 【核心修改 4】：动态调整 Y 轴的可视化极限 (Limit Range)，顶部预留 5 米的余量，设置范围为 [0, 55]
    fig.update_layout(
        yaxis_title=t['alt'],
        plot_bgcolor='white', height=550,
        margin=dict(l=50, r=50, b=30, t=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', range=[0, 55])
    )
    return fig

col1, col2 = st.columns(2)
with col1:
    st.markdown(t['p_a'])
    fig_a = plot_vertical_heat_strip(df_a, "A")
    if fig_a: st.plotly_chart(fig_a, use_container_width=True)

with col2:
    st.markdown(t['p_b'])
    fig_b = plot_vertical_heat_strip(df_b, "B")
    if fig_b: st.plotly_chart(fig_b, use_container_width=True)