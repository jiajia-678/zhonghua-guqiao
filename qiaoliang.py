import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import warnings
import base64
import plotly.graph_objects as go

# ----------------------
# 1. 全局配置 + 强制统一样式
# ----------------------
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="中华古桥",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌉"
)

# 🔥 最终修复版 CSS —— 标题完全显示 + 图片不变形
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #2d3748 !important;
        max-width: 100% !important;
    }
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    html, body {
        background-color: #ffffff !important;
        color: #2d3748 !important;
        font-family: "Microsoft YaHei", SimHei, sans-serif !important;
    }
    * {
        transition: none !important;
        animation: none !important;
        box-sizing: border-box !important;
    }

    /* 标题修复 */
    .title-custom {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #2d3748 !important;
        margin: 20px auto !important;
        text-align: center !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;
        font-family: "Microsoft YaHei", SimHei, sans-serif !important;
        line-height: 1.3 !important;
        padding: 10px 0 !important;
        overflow: visible !important;
    }

    .stImage img {
        object-fit: contain !important;
        max-height: 220px !important;
        width: 100% !important;
    }
    .stDataFrame {
        border-radius: 12px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        overflow: hidden !important;
        width: 100% !important;
    }
    .stDataFrame th {
        background-color: #4a5668 !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: center !important;
        white-space: nowrap !important;
        padding: 12px 15px !important;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #f7fafc !important;
    }
    .stDataFrame tr:hover {
        background-color: #e8f4f8 !important;
    }
    .stDataFrame td {
        padding: 12px 15px !important;
        text-align: center !important;
        white-space: nowrap !important;
    }
    .stButton>button {
        border-radius: 8px !important;
        height: 3rem !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    .detail-card {
        background-color: #f9fafb;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-top: 16px;
    }
    .detail-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #2d3748 !important;
        margin-bottom: 20px !important;
    }
    .detail-item {
        font-size: 1.1rem !important;
        margin-bottom: 12px !important;
        line-height: 1.8 !important;
    }
    .history-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 16px;
        border-left: 5px solid #4a5668;
    }
    .dynasty {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 8px;
    }
    .timeline-img {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .card-container {
        text-align: center; 
        padding: 20px; 
        background:#f8f9fa; 
        border-radius:12px;
        width: 100% !important;
    }

    /* ✅ 图片彻底修复：不拉伸、不压缩、不变形 */
    .card-img {
        border-radius: 8px;
        width: 100% !important;
        height: auto !important;
        max-height: 260px !important;
        object-fit: contain !important;
        object-position: center !important;
        background: #f1f3f5 !important;
    }

    .card-name {
        font-size:1.1rem; 
        font-weight:bold; 
        margin-top:10px;
        white-space: normal !important;
    }
    .card-desc {
        font-size:0.9rem; 
        color:#666;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------
# 2. 核心数据集
# ----------------------
data = {
    "朝代": ["隋", "隋", "唐", "北宋", "北宋", "金", "清", "清", "清", "清"],
    "桥名": ["赵州桥", "安平桥", "宝带桥", "洛阳桥", "广济桥", "卢沟桥", "双龙桥", "五亭桥", "八字桥", "霁虹桥"],
    "品类": ["石拱桥", "梁式石桥", "联孔石桥", "跨海梁式石桥", "开合式石桥", "联拱石桥", "多孔石拱桥", "石拱廊桥",
             "石梁桥", "铁索桥"],
    "经度": [114.571, 118.427, 120.633, 118.685, 116.649, 116.202, 103.245, 119.448, 120.58, 99.15],
    "纬度": [37.733, 24.661, 31.265, 24.908, 23.669, 39.846, 23.698, 32.390, 30.00, 25.12],
    "数量": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "代表介绍": [
        "隋·赵州桥：世界现存最早敞肩石拱桥",
        "隋·安平桥：古代最长跨海石桥",
        "唐·宝带桥：中国现存最长联孔石桥",
        "北宋·洛阳桥：跨海梁式石桥典范",
        "北宋·广济桥：世界最早启闭式桥梁",
        "金·卢沟桥：华北名桥，石刻艺术瑰宝",
        "清·双龙桥：滇南名桥，多孔石拱杰作",
        "清·五亭桥：扬州地标，石拱廊桥精品",
        "清·八字桥：中国最早立体交叉古桥",
        "清·霁虹桥：西南最古老铁索桥"
    ],
    "朝代排序": [0, 0, 1, 2, 2, 3, 6, 6, 6, 6]
}
df = pd.DataFrame(data)

# 图片文件映射
bridge_image_map = [
    {"name": "赵州桥", "img": "zhaozhou.jpg", "desc": "世界现存最早敞肩石拱桥"},
    {"name": "安平桥", "img": "anping.jpg", "desc": "古代最长跨海石桥"},
    {"name": "宝带桥", "img": "baodai.jpg", "desc": "中国现存最长联孔石桥"},
    {"name": "洛阳桥", "img": "luoyang.jpg", "desc": "跨海梁式石桥典范"},
    {"name": "广济桥", "img": "guangji.jpg", "desc": "世界最早启闭式桥梁"},
    {"name": "卢沟桥", "img": "lugou.jpg", "desc": "华北名桥，石刻艺术瑰宝"},
    {"name": "双龙桥", "img": "shigong.jpg", "desc": "滇南名桥，多孔石拱杰作"},
    {"name": "五亭桥", "img": "wuting.jpg", "desc": "扬州地标，石拱廊桥精品"},
    {"name": "八字桥", "img": "bazi.jpg", "desc": "中国最早立体交叉古桥"},
    {"name": "霁虹桥", "img": "langqiao.jpg", "desc": "西南最古老铁索桥"},
]

# 读取图片的辅助函数
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except:
        return None

# ----------------------
# 3. 筛选函数
# ----------------------
def filter_data(dynasty_list, category_list, count_range, time_range):
    if not dynasty_list or not category_list:
        return pd.DataFrame()
    min_count, max_count = count_range
    time_start, time_end = time_range
    filtered_df = df[
        (df["朝代"].isin(dynasty_list)) &
        (df["品类"].isin(category_list)) &
        (df["数量"] >= min_count) &
        (df["数量"] <= max_count) &
        (df["朝代排序"] >= time_start) &
        (df["朝代排序"] <= time_end)
        ]
    return filtered_df

def render_table(dataframe):
    return dataframe[["朝代", "桥名", "品类", "数量", "代表介绍", "经度", "纬度"]]

# ----------------------
# 4. 侧边栏
# ----------------------
with st.sidebar:
    st.title("🌉 中华古桥")
    page = st.radio(
        "页面导航",
        ["古桥文化简介", "古桥历史沿革", "古桥数据可视化"],
        index=0,
        key="page_switch",
        label_visibility="collapsed"
    )
    st.divider()
    selected_dynasty = []
    selected_category = []
    count_range = (1, 1)
    time_range = (0, 6)

    if page == "古桥数据可视化":
        st.subheader("🔍 筛选面板")
        selected_dynasty = st.multiselect(
            "选择朝代",
            options=["隋", "唐", "北宋", "金", "清"],
            default=["隋", "唐", "北宋", "金", "清"],
            key="dynasty"
        )
        core_categories = ["石拱桥", "梁式石桥", "联孔石桥", "联拱石桥", "开合式石桥",
                           "跨海梁式石桥", "多孔石拱桥", "石拱廊桥", "石梁桥", "铁索桥"]
        selected_category = st.multiselect(
            "选择桥类型",
            options=core_categories,
            default=core_categories,
            key="category"
        )
        time_slider = st.select_slider(
            "历史时期",
            options=["隋", "唐", "北宋", "金", "清"],
            value=("隋", "清"),
            key="time"
        )
        time_range_map = {"隋": 0, "唐": 1, "北宋": 2, "金": 3, "清": 6}
        time_range = (time_range_map[time_slider[0]], time_range_map[time_slider[1]])

        st.divider()
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        b64_csv = base64.b64encode(csv_data.encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{b64_csv}" download="中国古桥数据.csv">📥 下载完整数据</a>',
                    unsafe_allow_html=True)

# ----------------------
# 页面1：古桥文化简介
# ----------------------
if page == "古桥文化简介":
    st.markdown('<div class="title-custom">中国十大名桥</div>', unsafe_allow_html=True)
    st.divider()

    cols1 = st.columns(5)
    for i in range(5):
        with cols1[i]:
            bridge = bridge_image_map[i]
            img_base64 = get_image_base64(bridge["img"])
            if img_base64:
                st.markdown(f"""
                <div class="card-container">
                    <img src="data:image/jpeg;base64,{img_base64}" class="card-img">
                    <div class="card-name">{bridge['name']}</div>
                    <div class="card-desc">{bridge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card-container">
                    <div style="font-size:4rem;">🌉</div>
                    <div class="card-name">{bridge['name']}</div>
                    <div class="card-desc">{bridge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

    cols2 = st.columns(5)
    for i in range(5, 10):
        with cols2[i - 5]:
            bridge = bridge_image_map[i]
            img_base64 = get_image_base64(bridge["img"])
            if img_base64:
                st.markdown(f"""
                <div class="card-container">
                    <img src="data:image/jpeg;base64,{img_base64}" class="card-img">
                    <div class="card-name">{bridge['name']}</div>
                    <div class="card-desc">{bridge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card-container">
                    <div style="font-size:4rem;">🌉</div>
                    <div class="card-name">{bridge['name']}</div>
                    <div class="card-desc">{bridge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:30px; font-size:18px; text-align:center;">
    中国古桥是华夏文明的璀璨瑰宝，千百年来横跨江河，承载交通、艺术、历史与智慧。
    以上为中国最具代表性的十大名桥，展现了古代工匠的高超技艺。
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📖 十大名桥详细介绍")
    bridge_info = pd.DataFrame({
        "桥梁名称": ["赵州桥", "安平桥", "宝带桥", "洛阳桥", "广济桥",
                     "卢沟桥", "双龙桥", "五亭桥", "八字桥", "霁虹桥"],
        "建造朝代": ["隋代", "隋代", "唐代", "北宋", "北宋",
                     "金代", "清代", "清代", "清代", "清代"],
        "地理位置": ["河北石家庄", "福建晋江", "江苏苏州", "福建泉州", "广东潮州",
                     "北京丰台", "云南建水", "江苏扬州", "浙江绍兴", "云南保山"],
        "桥梁特色": [
            "世界现存最早、保存最完整的敞肩石拱桥",
            "古代最长跨海石桥，有\"天下无桥长此桥\"美誉",
            "中国现存最长的多孔联拱石桥，造型如玉带",
            "首创\"种蛎固基\"法，古代跨海石桥典范",
            "世界上最早的启闭式桥梁，集交通商贸于一体",
            "华北四大名桥之一，精美石狮与联拱结构",
            "滇南名桥，十七孔石拱桥建筑杰作",
            "扬州地标，石拱与亭台结合，造型秀丽",
            "中国最早的立体交叉古桥，水乡交通杰作",
            "西南最古老铁索桥，滇缅古驿道关键通道"
        ]
    })
    st.dataframe(bridge_info, width="stretch", hide_index=True)

# ----------------------
# 页面2：古桥历史沿革
# ----------------------
elif page == "古桥历史沿革":
    st.markdown('<div class="title-custom">中国古桥 · 历史发展脉络</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    中国古桥已有 **7000 年以上** 历史，从原始的独木桥、浮桥，逐步发展为结构精巧、艺术精湛的石拱桥、廊桥、跨海大桥，
    是世界桥梁史上连续发展最久、体系最完整的国家。
    """)
    st.divider()

    st.subheader("⏳ 古桥演变时间线")

    timeline = [
        {"img": "dumu.jpg", "era": "远古", "name": "独木桥", "desc": "桥梁的雏形，跨越溪流的最原始方式"},
        {"img": "shigong.jpg", "era": "隋代", "name": "石拱桥", "desc": "赵州桥为代表，开启石拱桥的巅峰时代"},
        {"img": "changjianshigong.jpg", "era": "唐代", "name": "大型石桥", "desc": "如宝带桥，长桥如虹，气势恢宏"},
        {"img": "baodai2.jpg", "era": "宋代", "name": "多孔石桥", "desc": "桥梁工程的黄金时代，技术成熟多样"},
        {"img": "anping2.jpg", "era": "宋元", "name": "跨海石桥", "desc": "如安平桥，跨越海湾的宏伟工程"},
        {"img": "langqiao.jpg", "era": "明清", "name": "廊桥", "desc": "集交通、休憩、文化于一体的建筑艺术"}
    ]

    for row in range(2):
        cols = st.columns(3)
        for i in range(3):
            idx = row * 3 + i
            with cols[i]:
                item = timeline[idx]
                img_base64 = get_image_base64(item["img"])
                if img_base64:
                    st.markdown(f"""
                    <div class="card-container">
                        <img src="data:image/jpeg;base64,{img_base64}" class="card-img">
                        <div class="card-name">{item['era']} · {item['name']}</div>
                        <div class="card-desc">{item['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align:center; padding:20px; background:#f8f9fa; border-radius:12px; margin:10px;">
                        <div style="font-size:3rem;">🌉</div>
                        <div style="font-size:1.1rem; font-weight:bold; margin-top:10px;">
                            {item['era']} · {item['name']}
                        </div>
                        <div style="font-size:0.85rem; color:#666; margin-top:8px;">
                            {item['desc']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        if row == 0:
            st.markdown("<div style='text-align:center; font-size:24px; color:#4a5668; margin:-5px 0;'>↓</div>",
                        unsafe_allow_html=True)

    st.divider()
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">🌿 先秦时期：桥梁起源</div>
            <p>距今约 6000–7000 年，原始先民为跨越河流，开始使用<strong>独木桥、浮桥、藤桥</strong>。
            商代已有正式木梁桥，西周出现浮桥与早期石桥，是中国古桥的萌芽阶段。</p>
        </div>
        """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">🏛️ 汉代：初步成熟</div>
            <p>汉代国力强盛，桥梁技术飞速发展。<strong>石拱桥、石梁桥正式出现</strong>，
            结构趋于稳定，桥梁开始与城市水利、交通网络结合，为后世桥梁奠定基础。</p>
        </div>
        """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">🏯 隋代：石拱桥巅峰开端</div>
            <p><strong>赵州桥</strong>建成，是世界上现存最早、保存最完整的<strong>敞肩石拱桥</strong>，
            开创了拱桥轻量化、大跨度的先河，代表古代石拱桥最高成就之一。</p>
        </div>
        """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">🌸 唐代：宏伟大气</div>
            <p>国力鼎盛，桥梁<strong>规模宏大、造型优美</strong>。
            联孔石桥、长桥大量出现，如<strong>宝带桥</strong>，长数百米，多孔相连，气势恢宏。
            桥梁开始兼具实用、景观、礼制功能。</p>
        </div>
        """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">📜 宋代：工程巅峰</div>
            <p>中国古桥<strong>技术最成熟、种类最丰富</strong>的时代。
            跨海石桥（洛阳桥、安平桥）、启闭式桥梁（广济桥）、联拱石桥（卢沟桥）纷纷出现，
            施工技术、力学设计、防潮防腐达到古代世界顶峰。</p>
        </div>
        """, unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="history-card">
            <div class="dynasty">🏮 元、明、清：精致与普及</div>
            <p>元代重修古桥，工艺更精细；
            明代<strong>廊桥、木石拱桥大量普及</strong>，少数民族桥梁艺术繁荣；
            清代桥梁更重装饰与园林结合，形成<strong>实用、艺术、文化三位一体</strong>的成熟体系。</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📌 中国古桥历史总结")
    st.success("""
    ✔️ 起源早：7000 年不间断发展史
    ✔️ 种类全：浮桥、梁桥、拱桥、廊桥、索桥俱全
    ✔️ 技术强：拱券、跨海、开合结构领先世界千年
    ✔️ 文化深：桥梁与水利、建筑、艺术、民俗深度融合
    """)

    st.divider()
    st.subheader("📊 名桥综合对比：赵州桥 vs 卢沟桥")
    categories = ["历史年代", "主跨跨度", "桥面宽度", "建造难度", "历史影响力"]
    zhaozhou = [98, 95, 60, 92, 95]
    lugou = [75, 70, 88, 82, 90]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=zhaozhou, theta=categories, fill='toself', name='赵州桥',
        line=dict(color='#2E86AB', width=3), fillcolor='rgba(46,134,171,0.2)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=lugou, theta=categories, fill='toself', name='卢沟桥',
        line=dict(color='#A23B72', width=3), fillcolor='rgba(162,59,114,0.2)'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            angularaxis=dict(tickfont=dict(size=13))
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor="center"
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=500
    )
    st.plotly_chart(fig_radar, width="stretch", config={"displayModeBar": False})

    st.markdown("""
**五维指标说明**
- 历史年代：赵州桥建造时间更早，历史更悠久
- 主跨跨度：赵州桥单孔跨度更大，技术难度更高
- 桥面宽度：卢沟桥桥面更宽，通行能力更强
- 建造难度：赵州桥敞肩石拱桥设计，工艺难度顶尖
- 历史影响力：两座均为国宝级文物，历史价值极高
""")

# ----------------------
# 页面3：古桥数据可视化
# ----------------------
elif page == "古桥数据可视化":
    filtered_df = filter_data(
        selected_dynasty,
        selected_category,
        (1, 1),
        time_range
    )
    st.markdown('<div class="title-custom">中华古桥：全国古桥数据可视化</div>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("古桥数量", len(filtered_df))
    with col2:
        st.metric("涉及朝代", filtered_df["朝代"].nunique() if not filtered_df.empty else 0)
    with col3:
        st.metric("桥类型", len(set(filtered_df["品类"])) if not filtered_df.empty else 0)

    st.divider()
    st.subheader("🗺️ 古桥地理分布")
    map_type = st.radio("视图切换", ["标记图", "热力图"], horizontal=True, key="map_type")

    if not filtered_df.empty:
        if map_type == "标记图":
            m = folium.Map(
                location=[32.0, 115.0],
                zoom_start=5,
                tiles="CartoDB Positron",
                scrollWheelZoom=False
            )
            color_map = {
                "隋": "#1E90FF", "唐": "#32CD32", "北宋": "#228B22",
                "金": "#FF6B6B", "清": "#9370DB"
            }
            for _, row in filtered_df.iterrows():
                folium.CircleMarker(
                    location=(row["纬度"], row["经度"]),
                    radius=12,
                    popup=f"<b>{row['桥名']}</b><br>{row['朝代']}｜{row['品类']}<br>{row['代表介绍']}",
                    color=color_map[row["朝代"]],
                    fill=True, fill_color=color_map[row["朝代"]], fill_opacity=0.7
                ).add_to(m)
            st_folium(m, width=1000, height=500, returned_objects=[])
        else:
            from folium.plugins import HeatMap
            m = folium.Map(location=[32.0, 115.0], zoom_start=5, tiles="CartoDB Positron", scrollWheelZoom=False)
            heat_data = [[row["纬度"], row["经度"], row["数量"]] for _, row in filtered_df.iterrows()]
            HeatMap(heat_data, radius=25, blur=15, min_opacity=0.5).add_to(m)
            st_folium(m, width=1000, height=500, returned_objects=[])
    else:
        st.warning("⚠️ 暂无符合条件的数据，请调整筛选条件")

    st.divider()
    st.subheader("📊 数据分析")
    tab1, tab2 = st.tabs(["数量统计", "古桥详情"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            type_data = {
                "桥类型": ["石拱桥", "梁式石桥", "石拱廊桥", "联孔/联拱石桥",
                           "多孔石拱桥", "跨海梁式石桥", "铁索桥", "开合式石桥"],
                "现存数量": [4521, 3867, 2193, 1208, 914, 131, 62, 1]
            }
            df_type = pd.DataFrame(type_data)
            fig_bar = px.bar(df_type,
                             x="桥类型",
                             y="现存数量",
                             color="现存数量",
                             height=400,
                             title="中国古桥各类型现存数量（座）")
            fig_bar.update_layout(title_x=0.5)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        with col2:
            dynasty_data = {
                "朝代": ["隋", "唐", "北宋", "金", "清"],
                "现存数量": [4, 6, 17, 3, 68]
            }
            df_dynasty = pd.DataFrame(dynasty_data)
            fig_pie = px.pie(df_dynasty,
                             values="现存数量",
                             names="朝代",
                             height=400,
                             hole=0.3,
                             title="中国古桥各朝代现存数量占比")
            fig_pie.update_layout(title_x=0.5)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with tab2:
        st.subheader("🔍 古桥详情")
        if not filtered_df.empty:
            selected_qiao = st.selectbox("选择古桥查看详情", filtered_df["桥名"].unique(), key="qiao_select_final")
            qiao_data = filtered_df[filtered_df["桥名"] == selected_qiao].iloc[0]
            st.markdown(f"""
            <div class="detail-card">
                <div class="detail-title">{qiao_data['桥名']}（{qiao_data['朝代']}代）</div>
                <div class="detail-item"><strong>古桥类型：</strong> {qiao_data['品类']}</div>
                <div class="detail-item"><strong>简介：</strong> {qiao_data['代表介绍']}</div>
                <div class="detail-item"><strong>坐标：</strong> 经度 {qiao_data['经度']}°，纬度 {qiao_data['纬度']}°</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无古桥数据可查看详情")

    st.divider()
    st.subheader("📋 古桥详细数据")
    real_bridge_data = pd.DataFrame({
        "朝代": ["隋", "隋", "唐", "北宋", "北宋", "金", "清", "清", "清", "清"],
        "桥名": ["赵州桥", "安平桥", "宝带桥", "洛阳桥", "广济桥", "卢沟桥", "双龙桥", "五亭桥", "八字桥", "霁虹桥"],
        "品类": ["石拱桥", "梁式石桥", "联孔石桥", "跨海梁式石桥", "开合式石桥", "联拱石桥", "多孔石拱桥", "石拱廊桥", "石梁桥", "铁索桥"],
        "地理位置": ["河北石家庄", "福建晋江", "江苏苏州", "福建泉州", "广东潮州", "北京丰台", "云南建水", "江苏扬州", "浙江绍兴", "云南保山"],
        "经度": [114.571, 118.427, 120.633, 118.685, 116.649, 116.202, 103.245, 119.448, 120.58, 99.15],
        "纬度": [37.733, 24.661, 31.265, 24.908, 23.669, 39.846, 23.698, 32.390, 30.00, 25.12],
        "桥梁特色": [
            "世界现存最早敞肩石拱桥",
            "古代最长跨海石桥",
            "中国现存最长联孔石桥",
            "跨海梁式石桥典范",
            "世界最早启闭式桥梁",
            "华北名桥，石刻艺术瑰宝",
            "滇南名桥，多孔石拱杰作",
            "扬州地标，石拱廊桥精品",
            "中国最早立体交叉古桥",
            "西南最古老铁索桥"
        ]
    })
    st.dataframe(real_bridge_data, use_container_width=True, hide_index=True)
