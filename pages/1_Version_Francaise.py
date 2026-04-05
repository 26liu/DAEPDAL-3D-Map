import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 网站全局配置
st.set_page_config(page_title="倾旋探微 - 大气监测可视化平台", layout="wide")

# 2. 页面主标题
st.title("🚁 倾旋探微 - 3D 局部空气诊断平台")
st.markdown(
    "本系统展示了倾旋翼无人机（VTOL）在飞行过程中采集的多维气象与空间污染数据。")


# 3. 读取数据
@st.cache_data
def load_data():
    # 使用相对路径，确保在 GitHub 和 Streamlit Cloud 上能正常读取
    df = pd.read_csv("Simulated_UAV_Meteorological_Data.csv")

    # 将原始列名重命名为规范的中文显示标签，确保图表悬浮提示和底部表格全中文显示
    rename_dict = {
        '标准时间': '采样时间',
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
    df.rename(columns=rename_dict, inplace=True)
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 未找到数据文件，请检查 CSV 文件路径是否正确！")
    st.stop()

# 适当抽样保证网页流畅
df_sample = df.iloc[::5, :]

# 4. 创建侧边栏控制面板
# 在侧边栏最上方插入团队 Logo
try:
    # use_container_width=True 会让图片自动适应侧边栏的宽度
    st.sidebar.image("logo.jpg", use_container_width=True)
except FileNotFoundError:
    # 如果找不到图片，就静默跳过，防止网页崩溃
    pass

st.sidebar.header("⚙️ 飞行参数与数据设置")
st.sidebar.markdown("请选择要在 3D 轨迹上渲染的气象/污染指标：")

# 使用重命名后的中文列名
available_metrics = [
    '大气温度 (°C)',
    '大气湿度 (%)',
    '大气压 (hPa)',
    'PM2.5 (µg/m³)',
    'PM10 (µg/m³)',
    'NO2 (µg/m³)',
    'SO2 (µg/m³)'
]

selected_metric = st.sidebar.selectbox("选择数据类型", available_metrics)

# 5. 动态渲染 3D 图表
st.subheader(f"当前视图：{selected_metric} 空间热力分布图")

fig = px.scatter_3d(
    df_sample,
    x='经度',
    y='纬度',
    z='高度 (m)',
    color=selected_metric,
    color_continuous_scale=px.colors.diverging.RdYlBu_r,
    opacity=0.85,
    labels={selected_metric: selected_metric} # 确保悬浮提示文字显示正确
)

# 消除点边框，让色彩融合更自然
fig.update_traces(marker=dict(size=4, line=dict(width=0)))

# 配置科研极简风的主题背景
fig.update_layout(
    scene=dict(
        xaxis_title='经度',
        yaxis_title='纬度',
        zaxis_title='高度 (m)',
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

# 6. 底部的原始数据表格
with st.expander("📊 查看原始数据日志 (Data Log)"):
    st.dataframe(df[['采样时间', '经度', '纬度', '高度 (m)', selected_metric]].head(50))
