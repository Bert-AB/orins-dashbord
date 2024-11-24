import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, time

# 设置页面配置，启用宽屏模式
st.set_page_config(layout="wide")

# 加载数据
try:
    data = pd.read_csv('./mt4镑日历史数据.csv', encoding='gbk')
except FileNotFoundError:
    st.error("数据文件未找到，请检查文件路径是否正确。")
    st.stop()
except Exception as e:
    st.error(f"加载数据时发生错误: {e}")
    st.stop()

# 将日期列转换为datetime类型
data['日期'] = pd.to_datetime(data['日期'], format='%Y-%m-%d')

# 获取所有可用日期
available_dates = data['日期'].unique()

# 在左侧边栏中插入日期选择器
selected_date = st.sidebar.date_input("选择日期",
                  min_value=min(available_dates).date(),
                  max_value=max(available_dates).date(),
                  value=min(available_dates).date())

# 在左侧边栏中插入时间输入框
start_time_str = st.sidebar.text_input("输入开始时间 (HH:MM)", value="00:00")
end_time_str = st.sidebar.text_input("输入结束时间 (HH:MM)", value="23:55")

# 尝试将输入的时间字符串转换为 datetime.time 对象
try:
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()
except ValueError:
    st.error("请输入有效的时间格式 (HH:MM)。")
    st.stop()

# 获取指定日期的数据
day_data = data[data['日期'] == pd.Timestamp(selected_date)]

if day_data.empty:
    st.warning(f"没有找到 {selected_date} 的数据。请尝试选择其他日期。")
else:
    # 将时间列转换为datetime类型
    day_data['time'] = pd.to_datetime(day_data['时间'], format='%H:%M').dt.time

    # 根据选择的时间范围过滤数据
    filtered_data = day_data[(day_data['time'] >= start_time) & (day_data['time'] <= end_time)]

    if filtered_data.empty:
        st.warning(f"在所选时间范围内没有数据。")
    else:
        # 准备用于绘图的数据
        box_data = filtered_data[['开盘', '最高', '最低', '收盘', 'time']].copy()

        # 创建箱型图
        fig = go.Figure()

        for time, data in box_data.groupby('time'):
            # 根据开盘价和收盘价的差异选择颜色
            if data['收盘'].iloc[0] > data['开盘'].iloc[0]:
                color = 'green'
            else:
                color = 'red'

            fig.add_trace(go.Box(y=data[['开盘', '最高', '最低', '收盘']].values.flatten(),
                                 name=time.strftime('%H:%M'),
                                 marker_color=color))

        # 设置图表标题和标签
        fig.update_layout(
            title=f"{selected_date} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} 镑日价格分布",
            xaxis_title="时间",
            yaxis_title="价格",
            font=dict(family="Arial, monospace", size=12, color="#7f7f7f"),
            xaxis=dict(tickangle=50),  # 自动调整x轴刻度标签，使其更易读
            width=1800,  # 设置画布宽度
            height=1000,  # 设置画布高度
            xaxis_rangeslider=dict(visible=True)  # 添加时间滑动条
        )

        # 应用自定义样式
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"] > .main {
                padding: 0;  /* 移除页面边缘的空白 */
            }
            [data-testid="stVerticalBlock"] {
                gap: 0;  /* 移除元素之间的间距 */
            }
            [data-testid="stPlotlyChart"] {
                display: flex;
                justify-content: center;  /* 水平居中 */
                align-items: center;  /* 垂直居中 */
                width: 100%;  /* 占据整个宽度 */
                height: 100%;  /* 占据整个高度 */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 在Streamlit中显示图表
        st.plotly_chart(fig, use_container_width=True)