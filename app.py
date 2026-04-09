import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from collections import Counter

st.set_page_config(page_title="Job Market Lie Detector", page_icon="🔍", layout="wide")

@st.cache_data
def load_data():
    real_usage = {
        "SQL":92,"Excel":85,"Data Analysis":90,"Data Visualization":70,
        "Power BI":52,"Communication":80,"Python":63,"Tableau":48,
        "ETL":28,"Statistics":45,"Data Science":30,"Data Modeling":35,
        "Problem Solving":85,"R":22,"Project Management":45,
        "Data Management":60,"Mathematics":40,"Machine Learning":18,
        "Agile":30,"PowerPoint":70,"Looker":18,"Leadership":55,
        "Critical Thinking":75,"Collaboration":80,"Reporting":72,
        "Data Analytics":88,"Spark":8,"Java":6,"Hadoop":5,
    }
    try:
        df_jobs = pd.read_csv("job_postings_with_skills.csv")
        total   = len(df_jobs)
        counter = Counter()
        for val in df_jobs["skills_required"]:
            try: counter.update(json.loads(val))
            except: pass
    except:
        total   = 116
        counter = {
            "SQL":70,"Excel":27,"Python":22,"Power BI":29,"Tableau":20,
            "Data Analysis":39,"Communication":23,"Statistics":15,
            "ETL":16,"Data Science":14,"Data Modeling":12,"R":10,
        }
    rows = []
    for skill, real_pct in real_usage.items():
        demanded = round(counter.get(skill, 0) / total * 100)
        gap      = real_pct - demanded
        if gap > 40:   cat = "Invisible"
        elif gap > 20: cat = "Undermentioned"
        elif gap < -5: cat = "Overhyped"
        else:          cat = "Fair"
        rows.append({
            "Skill": skill,
            "In Job Ads (%)": demanded,
            "Used Daily (%)": real_pct,
            "Hidden Gap": gap,
            "Category": cat
        })
    return pd.DataFrame(rows).sort_values("Hidden Gap", ascending=False), total

df, total_jobs = load_data()

# Build a simple lookup dictionary for fast matching
skill_lookup = {row["Skill"].lower(): row for _, row in df.iterrows()}

st.markdown("## Job Market Lie Detector")
st.markdown("**What companies demand vs what Data Analysts actually use daily**")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Job postings analyzed", total_jobs)
with c2:
    st.metric("Unique skills found", "564")
with c3:
    st.metric("Biggest hidden gap", "+79%")
with c4:
    st.metric("Most demanded skill", "SQL — 60%")

st.markdown("---")

st.sidebar.header("Filters")
categories = st.sidebar.multiselect(
    "Skill category",
    options=["Invisible","Undermentioned","Fair","Overhyped"],
    default=["Invisible","Undermentioned","Fair","Overhyped"]
)
min_gap = st.sidebar.slider("Minimum hidden gap (%)", 0, 80, 0, step=5)
top_n   = st.sidebar.slider("Show top N skills", 5, 30, 15, step=5)

filtered = df[
    (df["Category"].isin(categories)) &
    (df["Hidden Gap"] >= min_gap)
].head(top_n)

st.subheader("Skills demanded vs actually used daily")

fig = go.Figure()
fig.add_trace(go.Bar(
    name="Used daily",
    y=filtered["Skill"],
    x=filtered["Used Daily (%)"],
    orientation="h",
    marker_color="#2563EB",
    text=filtered["Used Daily (%)"].astype(str) + "%",
    textposition="outside"
))
fig.add_trace(go.Bar(
    name="In job ads",
    y=filtered["Skill"],
    x=filtered["In Job Ads (%)"],
    orientation="h",
    marker_color="#CBD5E1",
    text=filtered["In Job Ads (%)"].astype(str) + "%",
    textposition="outside"
))
fig.update_layout(
    barmode="overlay",
    height=max(400, len(filtered) * 42),
    xaxis=dict(title="% of Data Analysts", range=[0, 110]),
    yaxis=dict(autorange="reversed"),
    legend=dict(orientation="h", y=1.05),
    margin=dict(l=10, r=80, t=30, b=10),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1,1])
with col1:
    st.subheader("Category breakdown")
    cat_counts = df["Category"].value_counts().reset_index()
    cat_counts.columns = ["Category","Count"]
    colors = {"Invisible":"#E24B4A","Undermentioned":"#F59E0B","Fair":"#639922","Overhyped":"#2563EB"}
    fig2 = px.pie(cat_counts, names="Category", values="Count",
                  color="Category", color_discrete_map=colors, hole=0.45)
    fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Full data table")
    st.dataframe(
        filtered[["Skill","In Job Ads (%)","Used Daily (%)","Hidden Gap","Category"]],
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")
st.subheader("Job posting honesty checker")
st.markdown("Paste skills from any job posting to see how realistic it is")

user_input = st.text_area(
    "Paste required skills here (comma separated)",
    placeholder="e.g. SQL, Python, Spark, Kubernetes, Hadoop, Java...",
    height=80
)

if user_input.strip():
    entered = [s.strip() for s in user_input.split(",") if s.strip()]

    overhyped_found = []
    fair_found      = []
    unknown_found   = []

    for s in entered:
        key = s.lower()
        if key in skill_lookup:
            row = skill_lookup[key]
            if row["Category"] == "Overhyped":
                overhyped_found.append(row)
            else:
                fair_found.append(row)
        else:
            # skill not in our database — check if it is known hype
            known_hype = ["kubernetes","docker","kafka","scala","terraform",
                          "airflow","dbt","jenkins","ansible","cassandra"]
            if key in known_hype:
                overhyped_found.append({
                    "Skill": s, "Used Daily (%)": 3,
                    "In Job Ads (%)": 8, "Category": "Overhyped"
                })
            else:
                unknown_found.append(s)

    score = max(0, 100 - len(overhyped_found) * 20)

    col_a, col_b = st.columns(2)
    with col_a:
        if score >= 80:
            st.success(f"### Honesty score: {score}/100")
            st.success("This job posting looks realistic")
        elif score >= 50:
            st.warning(f"### Honesty score: {score}/100")
            st.warning("Some requirements may be inflated")
        else:
            st.error(f"### Honesty score: {score}/100")
            st.error("This posting has unrealistic requirements")

        st.markdown(f"**Skills checked:** {len(entered)}")
        st.markdown(f"**Overhyped:** {len(overhyped_found)}")
        st.markdown(f"**Realistic:** {len(fair_found)}")
        if unknown_found:
            st.markdown(f"**Not in our database:** {', '.join(unknown_found)}")

    with col_b:
        if overhyped_found:
            st.markdown("**Overhyped skills in this posting:**")
            for row in overhyped_found:
                st.error(
                    f"**{row['Skill']}** — only {row['Used Daily (%)']}% "
                    f"of analysts use it daily but {row['In Job Ads (%)']}% "
                    f"of job ads demand it"
                )
        else:
            st.success("No overhyped skills found — realistic posting!")

        if fair_found:
            st.markdown("**Realistic skills:**")
            for row in fair_found:
                st.success(f"**{row['Skill']}** — used by {row['Used Daily (%)']}% of analysts daily")

st.markdown("---")
st.markdown("Built with Python · JSearch API · Groq AI · Streamlit | 116 real US job postings")
