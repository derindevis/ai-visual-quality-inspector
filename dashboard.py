import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from database import verify_password, save_login_history, get_user
from database import create_user, verify_password, save_login_history, get_user

# Auto create default users if they don't exist
create_user(
    username = "admin",
    name     = "Derin Devis",
    email    = "derindevis79@gmail.com",
    password = "admin123",
    role     = "admin"
)
create_user(
    username = "viewer",
    name     = "Viewer User",
    email    = "viewer@gmail.com",
    password = "viewer123",
    role     = "viewer"
)

# Page config
st.set_page_config(
    page_title="AI Quality Inspector Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ── LOGIN PAGE ──
if not st.session_state.logged_in:
    st.title("🔍 AI Quality Inspector")
    st.markdown("### Please Login to Continue")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username  = st.text_input("👤 Username")
        password  = st.text_input("🔒 Password", type="password")
        login_btn = st.button("Login", use_container_width=True)

        if login_btn:
            if verify_password(username, password):
                st.session_state.logged_in = True
                st.session_state.username  = username
                user = get_user(username)
                st.session_state.role = user.role
                save_login_history(username, "SUCCESS")
                st.rerun()
            else:
                save_login_history(username, "FAILED")
                st.error("❌ Invalid username or password!")

# ── DASHBOARD ──
else:
    @st.cache_data(ttl=5)
    def load_data():
        engine = create_engine(
            "sqlite:///C:/Users/derin/OneDrive/Desktop/visual/database/inspections.db"
        )
        df = pd.read_sql("SELECT * FROM inspections", engine)
        return df

    # Header with user info
    col_title, col_user, col_logout = st.columns([6, 2, 1])
    with col_title:
        st.title("🏭 AI Visual Quality Inspection Dashboard")
        st.markdown("**Powered by YOLOv8 + Edufyi Tech Solutions**")
    with col_user:
        user = get_user(st.session_state.username)
        st.markdown(f"👤 **{user.name}**")
        st.markdown(f"🎭 Role: **{user.role.upper()}**")
    with col_logout:
        if st.button("Logout 🚪"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.role      = ""
            st.rerun()

    st.markdown("---")

    if st.session_state.role == "admin":
        with st.expander("👑 Admin Panel"):
        
            tab1, tab2, tab3 = st.tabs(["📝 Login History", "👤 Manage Users", "🗑️ Clear Data"])
        
        # Tab 1 - Login History
            with tab1:
                engine = create_engine(
                    "sqlite:///C:/Users/derin/OneDrive/Desktop/visual/database/inspections.db"
                )
                login_df = pd.read_sql(
                    "SELECT * FROM login_history ORDER BY login_time DESC LIMIT 20", 
                    engine
                )
                st.dataframe(login_df)

        # Tab 2 - Manage Users
            with tab2:
                engine = create_engine(
                    "sqlite:///C:/Users/derin/OneDrive/Desktop/visual/database/inspections.db"
                )
                users_df = pd.read_sql("SELECT id, username, name, email, role, created_at, is_active FROM users", engine)
                st.dataframe(users_df)

        # Tab 3 - Clear Data
            with tab3:
             st.warning("⚠️ These actions are permanent and cannot be undone!")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("**Clear Login History**")
                if st.button("🗑️ Clear Login History"):
                    from sqlalchemy import text
                    engine = create_engine(
                        "sqlite:///database/inspections.db"
                    )
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM login_history"))
                        conn.commit()
                    st.success("✅ Login history cleared!")
                    st.rerun()

            with col_b:
                st.markdown("**Clear Inspections**")
                if st.button("🗑️ Clear All Inspections"):
                    from sqlalchemy import text
                    engine = create_engine(
                        "sqlite:///database/inspections.db"
                    )
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM inspections"))
                        conn.commit()
                    st.success("✅ All inspections cleared!")
                    st.rerun()

            with col_c:
                st.markdown("**Clear Everything**")
                if st.button("🗑️ Clear ALL Data"):
                    from sqlalchemy import text
                    engine = create_engine(
                        "sqlite:///database/inspections.db"
                    )
                    with engine.connect() as conn:
                        conn.execute(text("DELETE FROM inspections"))
                        conn.execute(text("DELETE FROM login_history"))
                        conn.commit()
                    st.success("✅ All data cleared!")
                    st.rerun()

    st.markdown("---")

    df = load_data()

    if df.empty:
        st.warning("No inspections yet!")
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
            fig2 = px.bar(defect_data, x="Defect Type", y="Count", color="Defect Type")
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

        st.subheader("📋 Recent Inspections")
        recent = df.sort_values("timestamp", ascending=False).head(20)
        st.dataframe(
            recent[["timestamp", "image_name", "defect_type",
                    "confidence", "severity", "region", "result"]]
        )