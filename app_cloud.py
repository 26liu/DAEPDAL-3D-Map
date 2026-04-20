import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================================
# 1. Configuration Globale & i18n (全局配置与国际化)
# =====================================================================
st.set_page_config(page_title="Plateforme D.Æᵖ.D.A.L.", layout="wide")

# 语言资源字典 (Language Resource Dictionary)
# 集中管理所有静态文本，确保 UI 的完全解耦
TEXTS = {
    "Français": {
        "main_title": "D.Æᵖ.D.A.L. - Plateforme de Diagnostic de l'Air Local 3D",
        "desc": "Ce système visualise les données collectées par le drone D.Æᵖ.D.A.L. (Quadricoptère à empennage en V, optimisé pour l'utilisation de l'espace et la portabilité).",
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
        "btn_download": "📥 Télécharger le jeu de données complet",  # 法语下载提示
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
        "desc": "Visualizing data from the D.Æᵖ.D.A.L. drone (V-tail quad-rotor configuration, optimized for space utilization and portability).",
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
        "btn_download": "📥 Download Complete Dataset",  # 英语下载提示
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
    }
}


@st.cache_data
def load_raw_data():
    """
    数据加载模块。
    边界条件处理：云端环境 (如 Linux 容器) 无法识别 Windows 绝对路径。
    因此强制使用相对路径 (Relative Path)，要求 CSV 文件必须与 app.py 位于 GitHub 仓库的同一层级。
    """
    file_name = "UAV_Meteorological_Data_20260503.csv"
    return pd.read_csv(file_name, encoding='utf-8-sig')


# =====================================================================
# 3. Sidebar (侧边栏与状态机逻辑)
# =====================================================================
# 云端图片加载机制：同样切换为相对路径
logo_name = "logo.jpg"
if os.path.exists(logo_name):
    st.sidebar.image(logo_name, use_container_width=True)

# 语言监听器
selected_lang = st.sidebar.radio("🌐 Langue / Language", ["Français", "English"], index=0)
t = TEXTS[selected_lang]

try:
    raw_df = load_raw_data()
    # 动态列名映射：基于所选语言重写 DataFrame 列头
    df = raw_df.rename(columns=t["metric_names"])
except Exception:
    st.error(t["err_file"])
    st.stop()

# 3D 渲染降采样（提高前端 WebGL 帧率）
df_sample = df.iloc[::5, :]

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_flight"])
available_metrics = list(t["metric_names"].values())[4:]
selected_metric = st.sidebar.selectbox("Metric", available_metrics, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_slice"])
# 动态提取高度极值，防止硬编码导致的数据越界
abs_min_alt = float(df[t['metric_names']['高度(Altitude_m)']].min())
abs_max_alt = float(df[t['metric_names']['高度(Altitude_m)']].max())

range_slider = st.sidebar.slider(t["slider_quick"], abs_min_alt, abs_max_alt, (abs_min_alt + 50.0, abs_min_alt + 60.0),
                                 step=0.1)
col1, col2 = st.sidebar.columns(2)
with col1:
    alt_min = st.number_input(t["input_min"], abs_min_alt, abs_max_alt, range_slider[0], step=0.1, format="%.1f")
with col2:
    alt_max = st.number_input(t["input_max"], abs_min_alt, abs_max_alt + 50.0, range_slider[1], step=0.1, format="%.1f")

# 逻辑自校正：自动修复 Min > Max 的误输入
final_range = (min(alt_min, alt_max), max(alt_min, alt_max))

# =====================================================================
# 4. Rendering (主页面 3D 与 2D 渲染)
# =====================================================================
st.title(t["main_title"])
st.markdown(t["desc"])

col_lon = t['metric_names']['经度(Longitude)']
col_lat = t['metric_names']['纬度(Latitude)']
col_alt = t['metric_names']['高度(Altitude_m)']

# 实例化 3D 散点云
fig_3d = px.scatter_3d(
    df_sample, x=col_lon, y=col_lat, z=col_alt,
    color=selected_metric,
    color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.85
)
fig_3d.update_layout(
    scene=dict(xaxis_title=col_lon, yaxis_title=col_lat, zaxis_title=col_alt, bgcolor='white'),
    paper_bgcolor='white',
    height=700
)
st.plotly_chart(fig_3d, use_container_width=True)

# 2D 数据切片：利用布尔掩码 (Boolean Mask) 过滤指定高度层
df_slice = df[(df[col_alt] >= final_range[0]) & (df[col_alt] <= final_range[1])]
st.markdown("---")
st.subheader(t["title_2d"].format(min=final_range[0], max=final_range[1]))

if not df_slice.empty:
    fig_2d = px.scatter(
        df_slice, x=col_lon, y=col_lat,
        color=selected_metric,
        color_continuous_scale=px.colors.diverging.RdYlBu_r
    )
    st.plotly_chart(fig_2d, use_container_width=True)
else:
    st.warning(t["warn_no_data"])

# =====================================================================
# 6. Raw Data Export (数据溯源与导出)
# =====================================================================
with st.expander(t["expander_raw"]):
    # 使用虚拟滚动 (Virtual Scrolling) 技术渲染全量数据，取代原先的 .head() 截断
    st.dataframe(df, use_container_width=True)

    # 将 Pandas DataFrame 转换为带有 UTF-8 BOM 签名的字节流，防止 Excel 打开时出现乱码
    csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    # 部署云端下载组件
    st.download_button(
        label=t["btn_download"],
        data=csv_data,
        file_name="D_AEP_DAL_Flight_Log_Complete.csv",
        mime="text/csv"
    )
