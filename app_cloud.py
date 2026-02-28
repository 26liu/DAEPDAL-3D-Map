import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuration globale de la page (网站全局配置)
st.set_page_config(page_title="Plateforme D.Æᵖ.D.A.L.", layout="wide")

# 2. Titre principal de la page (页面主标题)
# 融入了你们项目的正式名称
st.title("D.Æᵖ.D.A.L. - Plateforme de Diagnostic de l'Air Local 3D")
st.markdown(
    "Ce système présente les données météorologiques et de pollution spatiale multidimensionnelles collectées par le drone à aile pivotante (VTOL) pendant le vol.")


# 3. Chargement des données (读取数据)
@st.cache_data
def load_data():
    # 修改后（假设文件和代码在同一个文件夹）：
    df = pd.read_csv("Simulated_UAV_Meteorological_Data.csv")

    # 将中文列名重命名为法语，确保图表悬浮提示和底部表格全法文化
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
    st.error("⚠️ Fichier de données introuvable. Veuillez vérifier le chemin du fichier CSV !")
    st.stop()

# Échantillonnage pour assurer la fluidité (适当抽样保证网页流畅)
df_sample = df.iloc[::5, :]

# ... 前面的代码保持不变 ...

# 4. Panneau de contrôle latéral (创建侧边栏控制面板)
# 🌟 新增：在侧边栏最上方插入团队 Logo
try:
    # use_container_width=True 会让图片自动适应侧边栏的宽度
    # 修改后：
    st.sidebar.image("logo.jpg", use_container_width=True)
except FileNotFoundError:
    # 如果找不到图片，就静默跳过，防止网页崩溃
    pass

st.sidebar.header("⚙️ Paramètres de Vol et Données")
st.sidebar.markdown("Veuillez sélectionner l'indicateur météorologique à rendre sur la trajectoire 3D :")

# ... 后面的代码保持不变 ...

# 使用重命名后的法语列名
available_metrics = [
    'Température (°C)',
    'Humidité (%)',
    'Pression Atmos. (hPa)',
    'PM2.5 (µg/m³)',
    'PM10 (µg/m³)',
    'NO2 (µg/m³)',
    'SO2 (µg/m³)'
]

selected_metric = st.sidebar.selectbox("Sélectionner le type de données", available_metrics)

# 5. Rendu dynamique du graphique 3D (动态渲染 3D 图表)
st.subheader(f"Vue actuelle : Cartographie thermique 3D de {selected_metric}")

fig = px.scatter_3d(
    df_sample,
    x='Longitude',
    y='Latitude',
    z='Altitude (m)',
    color=selected_metric,
    color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.85
)

# Suppression des bordures des points pour une meilleure fusion des couleurs
fig.update_traces(marker=dict(size=4, line=dict(width=0)))

# Configuration du thème blanc et de la grille
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

# 6. Tableau des données brutes en bas (底部的原始数据表格)
with st.expander("📊 Afficher le journal des données brutes (Data Log)"):
    st.dataframe(df[['Horodatage', 'Longitude', 'Latitude', 'Altitude (m)', selected_metric]].head(50))