import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Page config
st.set_page_config(
    page_title="AI Quality Inspector Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Load data
@st.cache_data(ttl=5)
def load_data():
    engine = create_engine("sqlite:///C:/Users/derin/OneDrive/Desktop/visual/database/inspections.db")
    df = pd.read_sql("SELECT * FROM inspections", engine)
    return df

# Header
st.title("🏭 AI Visual Quality Inspection Dashboard")
st.markdown("**Powered by YOLOv8 + Edufyi Tech Solutions**")
st.markdown("---")

# Load data
df = load_data()

if df.empty:
    st.warning("No inspections yet! Run report_generator.py first.")
else:
    # TOP METRICS
    col1, col2, col3, col4 = st.columns(4)
    total     = len(df)
    passed    = len(df[df["result"] == "PASS"])
    failed    = len(df[df["result"] == "FAIL"])
    pass_rate = (passed / total * 100) if total > 0 else 0

    col1.metric("📦 Total Inspections", total)
    col2.metric("✅ Passed", passed)
    col3.metric("❌ Failed", failed)
    col4.metric("📊 Pass Rate", f"{pass_rate:.1f}%")

    st.markdown("---")

    # CHARTS
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("🍩 Pass vs Fail")
        pie_data = df["result"].value_counts().reset_index()
        pie_data.columns = ["Result", "Count"]
        fig1 = px.pie(
            pie_data, values="Count", names="Result",
            color_discrete_map={"PASS": "#00cc96", "FAIL": "#ef553b"}
        )
        st.plotly_chart(fig1)

    with col6:
        st.subheader("📊 Defects by Type")
        defect_data = df[df["defect_type"] != "None"]["defect_type"].value_counts().reset_index()
        defect_data.columns = ["Defect Type", "Count"]
        fig2 = px.bar(
            defect_data, x="Defect Type", y="Count",
            color="Defect Type"
        )
        st.plotly_chart(fig2)

    st.markdown("---")

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("⚠️ Severity Breakdown")
        sev_data = df["severity"].value_counts().reset_index()
        sev_data.columns = ["Severity", "Count"]
        fig3 = px.bar(sev_data, x="Severity", y="Count", color="Severity")
        st.plotly_chart(fig3)

    with col8:
        st.subheader("📈 Inspections Over Time")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        time_data = df.groupby(df["timestamp"].dt.date).size().reset_index()
        time_data.columns = ["Date", "Count"]
        fig4 = px.line(time_data, x="Date", y="Count", markers=True)
        st.plotly_chart(fig4)

    st.markdown("---")

    # TABLE
    st.subheader("📋 Recent Inspections")
    recent = df.sort_values("timestamp", ascending=False).head(20)
    st.dataframe(
        recent[["timestamp", "image_name", "defect_type",
                "confidence", "severity", "region", "result"]]
    )