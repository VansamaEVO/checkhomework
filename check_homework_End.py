# =========================================================
# 学生作业智能检查系统（人工阅卷纯净版）
# =========================================================

import re
import zipfile
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt

# =========================================================
# 1. 页面配置
# =========================================================
st.set_page_config(
    page_title="学生作业检查系统",
    page_icon="📘",
    layout="wide"
)

# =========================================================
# 2. 全局样式美化
# =========================================================
st.markdown(
    """
    <style>
    /* 全局背景微调 */
    .stApp { background-color: #f8f9fa; }

    /* 顶部 Banner 渐变色优化 */
    .banner {
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
        padding: 2rem; 
        border-radius: 16px; 
        color: #2c3e50; 
        text-align: center;
        margin-bottom: 2rem; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .banner h1 { color: #2c3e50; margin-bottom: 0.5rem; font-weight: 800; font-size: 2.5rem; }
    .banner p { font-size: 1.1rem; opacity: 0.8; font-weight: 600; }

    /* 步骤条样式 */
    .step-box {
        background: #ffffff; 
        padding: 12px; 
        border-radius: 8px;
        margin-bottom: 10px; 
        border-left: 5px solid #66a6ff; 
        font-size: 0.9rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* 评分控制台卡片样式 */
    .grade-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* 调整数字输入框样式 */
    [data-testid="stNumberInput"] { margin-bottom: 0.5rem; }

    /* 优化 Tab 标题 */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. 顶部 Banner
# =========================================================
st.markdown(
    """
    <div class="banner">
        <h1>📘 学生作业检查系统</h1>
        <p>高效 · 可视化 · 人工阅卷平台</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 4. 侧边栏逻辑
# =========================================================
with st.sidebar:
    st.header("⚙️ 视图设置")

    # 删除了 API Key 输入框

    expand_all = st.toggle(
        "一键展开所有作业",
        value=False,
        help="开启后，右侧所有学生的作业详情页会自动展开，无需手动逐个点击，方便快速浏览。"
    )
    if expand_all:
        st.caption("ℹ️ 当前状态：作业详情已默认全部展开")
    else:
        st.caption("ℹ️ 当前状态：作业详情默认折叠")

    st.markdown("---")
    st.subheader("📝 操作指南")
    st.markdown(
        """
        <div class="step-box"><b>Step 1</b> 上传 Excel 花名册</div>
        <div class="step-box"><b>Step 2</b> 上传作业 ZIP 包</div>
        <div class="step-box"><b>Step 3</b> 在 Tab3 查看代码并打分</div>
        <div class="step-box"><b>Step 4</b> 底部导出最终成绩单</div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 5. 核心逻辑函数
# =========================================================
def extract_student_id_from_filename(filename):
    m = re.search(r"\d{9}", filename)
    return m.group() if m else None


def get_student_info_from_roster(roster_file):
    try:
        df_raw = pd.read_excel(roster_file, header=None)
        header_row = None
        for i in range(len(df_raw)):
            row = df_raw.iloc[i].astype(str).tolist()
            if any("学号" in v for v in row) and any("姓名" in v for v in row):
                header_row = i
                break
        if header_row is None: return set(), {}

        df = pd.read_excel(roster_file, header=header_row)
        df = df.dropna(axis=1, how="all")

        sid_col = next(c for c in df.columns if "学号" in str(c))
        name_col = next(c for c in df.columns if "姓名" in str(c))

        student_ids = set()
        id_name_map = {}
        for _, row in df.iterrows():
            m = re.search(r"\d{9}", str(row[sid_col]))
            if m:
                sid = m.group()
                student_ids.add(sid)
                id_name_map[sid] = str(row[name_col]).strip()
        return student_ids, id_name_map
    except:
        return set(), {}


# 删除了 deepseek_ai_check 函数

# =========================================================
# 6. 主界面逻辑
# =========================================================
st.subheader("📂 文件上传区")
c1, c2 = st.columns(2)
with c1: roster_file = st.file_uploader("上传花名册 (Excel)", type="xlsx")
with c2: homework_zip = st.file_uploader("上传作业包 (ZIP)", type="zip")

if not roster_file or not homework_zip:
    st.info("👋 请先上传必要文件以开始工作")
    st.stop()

with tempfile.TemporaryDirectory() as tmpdir:
    # --- 数据处理 ---
    roster_path = Path(tmpdir) / "roster.xlsx"
    roster_path.write_bytes(roster_file.getbuffer())
    student_ids, id_name_map = get_student_info_from_roster(roster_path)

    with zipfile.ZipFile(homework_zip) as z:
        z.extractall(tmpdir)

    submitted_ids = set()
    homework_files = []
    # 使用 rglob 递归查找，防止文件在子文件夹中
    for py in Path(tmpdir).rglob("*.py"):
        sid = extract_student_id_from_filename(py.name)
        if sid:
            submitted_ids.add(sid)
            homework_files.append(py)

    missing_ids = student_ids - submitted_ids

    # ==============================
    # TAB 页展示
    # ==============================
    tab1, tab2, tab3 = st.tabs(["📊 提交统计", "📋 学生明细", "📝 作业评分 (核心)"])

    # --- TAB 1: 统计图表 ---
    with tab1:
        st.markdown("#### 📈 概览数据")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("应交", len(student_ids))
        m2.metric("已交", len(submitted_ids), delta="完成")
        m3.metric("未交", len(missing_ids), delta="-缺交", delta_color="inverse")
        rate = len(submitted_ids) / len(student_ids) if student_ids else 0
        m4.metric("提交率", f"{rate:.1%}")
        st.progress(rate)

        st.divider()

        c_chart, c_legend = st.columns([3, 1])
        with c_chart:
            chart_data = pd.DataFrame({
                '状态': ['已交', '未交'],
                '人数': [len(submitted_ids), len(missing_ids)]
            })

            base = alt.Chart(chart_data).encode(theta=alt.Theta("人数", stack=True))

            # 环形图主体
            pie = base.mark_arc(innerRadius=80, outerRadius=120).encode(
                color=alt.Color("状态", scale=alt.Scale(domain=['已交', '未交'], range=['#2ecc71', '#e74c3c'])),
                tooltip=["状态", "人数"]
            )

            # 数字标签
            text = base.mark_text(radius=140, size=24, fontStyle="bold").encode(
                text=alt.Text("人数"),
                color=alt.value("black")
            )

            st.altair_chart(pie + text, use_container_width=True)

        with c_legend:
            st.markdown("#### 图例")
            st.markdown(f"🟢 **已交**: {len(submitted_ids)} 人")
            st.markdown(f"🔴 **未交**: {len(missing_ids)} 人")

    # --- TAB 2: 学生明细 ---
    with tab2:
        rows = []
        for i, sid in enumerate(sorted(student_ids), 1):
            is_sub = sid in submitted_ids
            status_text = "✅ 已交" if is_sub else "❌ 未交"

            rows.append({
                "序号": i,
                "学号": sid,
                "姓名": id_name_map.get(sid, "未知"),
                "提交状态": status_text
            })

        df_show = pd.DataFrame(rows)


        def color_row(row):
            if "已交" in row["提交状态"]:
                bg_color = 'background-color: #d4edda; color: #155724'
            else:
                bg_color = 'background-color: #f8d7da; color: #721c24'
            return [bg_color if col == '提交状态' else '' for col in row.index]


        styled_df = df_show.style.apply(color_row, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )

    # --- TAB 3: 作业评分 (核心) ---
    with tab3:
        if not homework_files:
            st.warning("⚠️ 未识别到任何作业文件 (请检查 ZIP 中是否包含 .py 文件且以学号命名)")
        else:
            grade_data = []  # 用于收集导出数据

            for py in homework_files:
                sid = extract_student_id_from_filename(py.name)
                name = id_name_map.get(sid, "未知")
                score_key = f"score_{sid}"

                # 初始化分数
                if score_key not in st.session_state:
                    st.session_state[score_key] = 0.0

                # 展开框
                with st.expander(f"📝 {sid} - {name}", expanded=expand_all):

                    # 调整比例：左侧代码 (3) : 右侧评分 (1)
                    c_code, c_grade = st.columns([3, 1])

                    code_content = py.read_text(encoding="utf-8", errors="ignore")

                    # --- 左侧：代码区 ---
                    with c_code:
                        st.markdown("**💻 学生代码** (可滚动查看)")
                        # height=500 限制高度，内容多时自动出现滚动条
                        with st.container(height=500):
                            st.code(code_content, language="python")

                    # --- 右侧：人工评分区 ---
                    with c_grade:
                        # 使用容器卡片化，增加美观度
                        with st.container(border=True):
                            st.markdown("#### 💯 评分控制台")
                            st.caption("请阅读左侧代码后打分")

                            st.markdown("---")

                            new_score = st.number_input(
                                f"输入分数",
                                min_value=0.0, max_value=100.0, step=1.0,
                                key=score_key,
                                label_visibility="collapsed"  # 隐藏label，用上方标题代替
                            )

                            st.markdown(
                                f"<h2 style='text-align: center; color: #66a6ff;'>{st.session_state[score_key]:.0f} <span style='font-size: 1rem; color: #888;'>分</span></h2>",
                                unsafe_allow_html=True)

                # 收集数据
                grade_data.append({
                    "学号": sid,
                    "姓名": name,
                    "作业文件": py.name,
                    "最终得分": st.session_state[score_key]
                })

            # --- 导出区 ---
            st.divider()
            if grade_data:
                st.markdown("### 📥 导出成绩单")
                df_export = pd.DataFrame(grade_data)
                csv = df_export.to_csv(index=False).encode('utf-8-sig')

                st.download_button(
                    label="💾 下载 CSV 成绩单",
                    data=csv,
                    file_name="作业成绩单.csv",
                    mime="text/csv"
                )