import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================================
# 1. Configuration Globale & i18n (多语言资源配置)
# =====================================================================
st.set_page_config(page_title="Plateforme D.Æᵖ.D.A.L.", layout="wide")

# 文本资源字典
TEXTS = {
    "Français": {
        "main_title": "D.Æᵖ.D.A.L. - Plateforme de Diagnostic de l'Air Local 3D",
        "desc": "Ce système visualise les données météorologiques et de pollution multidimensionnelles collectées par le drone D.Æᵖ.D.A.L. lors de sa mission.",
        "sidebar_flight": "⚙️ Paramètres de Vol",
        "sidebar_select_ind": "Sélectionnez l'indicateur :",
        "sidebar_slice": "🔪 Section Transversale",
        "sidebar_analyze": "Analyse d'altitude :",
        "slider_quick": "Sélection Rapide (m)",
        "input_min": "Min Précis (m)",
        "input_max": "Max Précis (m)",
        "err_min_max": "Erreur : Min > Max",
        "title_3d": "Cartographie 3D : ",
        "title_2d": "Coupe 2D ({min:.1f}m - {max:.1f}m)",
        "title_2d_fig": "Distribution horizontale",
        "warn_no_data": "⚠️ Aucune donnée dans cette plage.",
        "expander_raw": "📊 Voir les Données Brutes",
        "btn_download": "📥 Télécharger le jeu de données complet",
        "err_file": "⚠️ Fichier de données introuvable sur le serveur !",
        "metric_names": {
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
    },
    "English": {
        "main_title": "D.Æᵖ.D.A.L. - 3D Air Diagnostic Platform",
        "desc": "This system visualizes multidimensional meteorological and pollution data collected by the D.Æᵖ.D.A.L. drone during its mission.",
        "sidebar_flight": "⚙️ Flight Parameters",
        "sidebar_select_ind": "Select indicator:",
        "sidebar_slice": "🔪 Cross Section",
        "sidebar_analyze": "Altitude analysis:",
        "slider_quick": "Quick Select (m)",
        "input_min": "Precise Min (m)",
        "input_max": "Precise Max (m)",
        "err_min_max": "Error: Min > Max",
        "title_3d": "3D Mapping: ",
        "title_2d": "2D Cut ({min:.1f}m - {max:.1f}m)",
        "title_2d_fig": "Horizontal distribution",
        "warn_no_data": "⚠️ No data in this range.",
        "expander_raw": "📊 View Raw Data Logs",
        "btn_download": "📥 Download Complete Dataset",
        "err_file": "⚠️ Data file not found on server!",
        "metric_names": {
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
    },
    "Chinois": {
        "main_title": "D.Æᵖ.D.A.L. - 三维局部空气质量诊断平台",
        "desc": "本系统可视化了 D.Æᵖ.D.A.L. 无人机在执行任务期间采集的多维气象和污染数据。",
        "sidebar_flight": "⚙️ 飞行参数",
        "sidebar_select_ind": "选择要显示的指标：",
        "sidebar_slice": "🔪 横截面分析",
        "sidebar_analyze": "分析特定高度的分布：",
        "slider_quick": "快速选择 (m)",
        "input_min": "精确最小值 (m)",
        "input_max": "精确最大值 (m)",
        "err_min_max": "错误：最小值 > 最大值",
        "title_3d": "3D 映射：",
        "title_2d": "2D 横截面 (高度：{min:.1f}m - {max:.1f}m)",
        "title_2d_fig": "目标高度的水平分布趋势",
        "warn_no_data": "⚠️ 此范围内无数据，请调整参数。",
        "expander_raw": "📊 查看原始数据日志",
        "btn_download": "📥 下载完整数据集",
        "err_file": "⚠️ 服务器上找不到数据文件！",
        "metric_names": {
            '标准时间': '标准时间',
            '经度(Longitude)': '经度',
            '纬度(Latitude)': '纬度',
            '高度(Altitude_m)': '高度 (m)',
            '大气温度(℃)': '大气温度 (°C)',
            '大气湿度(%)': '大气湿度 (%)',
            '大气压(hPa)': '大气压 (hPa)',
            '工况PM2.5(ug/m3)': 'PM2.5 (µg/m³)',
            '工况PM10(ug/m3)': 'PM10 (µg/m³)',
            'NO2(ug/m3)': 'NO2 (µg/m³)',
            'SO2(ug/m3)': 'SO2 (µg/m³)'
        }
    }
}

# =====================================================================
# 2. Pipeline de Données (数据加载)
# =====================================================================
@st.cache_data
def load_raw_data():
    # 相对路径适配云端环境
    file_name = "UAV_Meteorological_Data_20260503.csv"
    return pd.read_csv(file_name, encoding='utf-8-sig')

# =====================================================================
# 3. Sidebar (侧边栏)
# =====================================================================
logo_name = "logo.jpg"
if os.path.exists(logo_name):
    st.sidebar.image(logo_name, use_container_width=True)

# 语言选择器：首选法语 (index=0)
selected_lang = st.sidebar.radio("🌐 Langue / Language / 语言", ["Français", "English", "Chinois"], index=0)
t = TEXTS[selected_lang]

try:
    raw_df = load_raw_data()
    # 依据所选语言动态映射列名
    df = raw_df.rename(columns=t["metric_names"])
except Exception:
    st.error(t["err_file"])
    st.stop()

# 3D 渲染采样
df_sample = df.iloc[::5, :]

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_flight"])
st.sidebar.markdown(t["sidebar_select_ind"])

# 获取除时空维度外的监测指标列名
available_metrics = list(t["metric_names"].values())[4:]
selected_metric = st.sidebar.selectbox("Metric", available_metrics, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_slice"])
st.sidebar.markdown(t["sidebar_analyze"])

# 获取实时高度边界
col_alt_name = t['metric_names']['高度(Altitude_m)']
abs_min_alt = float(df[col_alt_name].min())
abs_max_alt = float(df[col_alt_name].max())

# 混合控制：快速选择滑动条
range_slider = st.sidebar.slider(
    t["slider_quick"], 
    abs_min_alt, abs_max_alt, 
    (abs_min_alt + 50.0, abs_min_alt + 60.0), 
    step=0.1
)

# 混合控制：精确数字输入
col1, col2 = st.sidebar.columns(2)
with col1:
    alt_min = st.number_input(t["input_min"], abs_min_alt, abs_max_alt, range_slider[0], step=0.1, format="%.1f")
with col2:
    alt_max = st.number_input(t["input_max"], abs_min_alt, abs_max_alt + 50.0, range_slider[1], step=0.1, format="%.1f")

# 逻辑校验
final_range = (min(alt_min, alt_max), max(alt_min, alt_max))

# =====================================================================
# 4. Main Rendering (主界面渲染)
# =====================================================================
st.title(t["main_title"])
st.markdown(t["desc"])

col_lon = t['metric_names']['经度(Longitude)']
col_lat = t['metric_names']['纬度(Latitude)']
col_alt = t['metric_names']['高度(Altitude_m)']

# --- Vue 3D ---
st.subheader(f"{t['title_3d']} {selected_metric}")
fig_3d = px.scatter_3d(
    df_sample, 
    x=col_lon, y=col_lat, z=col_alt,
    color=selected_metric,
    color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.85
)
fig_3d.update_traces(marker=dict(size=4, line=dict(width=0)))
fig_3d.update_layout(
    scene=dict(xaxis_title=col_lon, yaxis_title=col_lat, zaxis_title=col_alt, bgcolor='white'),
    paper_bgcolor='white',
    height=700
)
st.plotly_chart(fig_3d, use_container_width=True)

# --- Section 2D ---
df_slice = df[(df[col_alt] >= final_range[0]) & (df[col_alt] <= final_range[1])]
st.markdown("---")
st.subheader(t["title_2d"].format(min=final_range[0], max=final_range[1]))

if not df_slice.empty:
    fig_2d = px.scatter(
        df_slice, 
        x=col_lon, y=col_lat,
        color=selected_metric,
        color_continuous_scale=px.colors.diverging.RdYlBu_r,
        title=t["title_2d_fig"]
    )
    fig_2d.update_traces(marker=dict(size=8, opacity=0.9, line=dict(width=1, color='DarkSlateGrey')))
    fig_2d.update_layout(xaxis_title=col_lon, yaxis_title=col_lat, plot_bgcolor='white', height=500)
    st.plotly_chart(fig_2d, use_container_width=True)
else:
    st.warning(t["warn_no_data"])

# --- Raw Data Log & Download ---
with st.expander(t["expander_raw"]):
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label=t["btn_download"],
        data=csv_bytes,
        file_name="D_AEP_DAL_Full_Log.csv",
        mime="text/csv"
    )
