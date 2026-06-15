import streamlit as st
import pandas as pd
import numpy as np
import joblib
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import ast, warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Code Review Intelligence",
    page_icon=":)",
    layout="wide"
)

@st.cache_resource
def load_all():
    xgb          = joblib.load('data/processed/xgboost_model.pkl')
    scaler       = joblib.load('data/processed/scaler.pkl')
    file_experts = joblib.load('data/processed/file_experts.pkl')
    df           = pd.read_csv('data/processed/pr_cleaned.csv')
    return xgb, scaler, file_experts, df

xgb, scaler, file_experts, df = load_all()

# Header
st.title(" AI Code Review Intelligence System")
st.markdown("Predict bug risk · Recommend reviewers · Explain decisions")
st.divider()

# Sidebar input
st.sidebar.header("Analyse a Pull Request")
additions     = st.sidebar.slider("Lines Added",       0, 1000, 50)
deletions     = st.sidebar.slider("Lines Deleted",     0, 500,  20)
changed_files = st.sidebar.slider("Files Changed",     1, 50,   3)
commits       = st.sidebar.slider("Commits",           1, 30,   2)
comments      = st.sidebar.slider("Comments",          0, 50,   5)
has_reviewer  = st.sidebar.selectbox("Has Reviewer?",  [1, 0])
has_test      = st.sidebar.selectbox("Has Test File?", [1, 0])
keyword_count = st.sidebar.slider("Bug Keywords",      0, 10,   1)
pr_author     = st.sidebar.text_input("PR Author", "octocat")
files_input   = st.sidebar.text_area(
    "Changed Files (comma-separated)", 
    "src/main.py, tests/test_main.py"
)

if st.sidebar.button(" Analyse PR", type="primary"):

    total   = additions + deletions
    churn   = deletions / (additions + 1)
    avg_chg = total / (changed_files + 1)
    cpm     = commits / (changed_files + 1)
    rev_int = comments / (commits + 1)

    feat = np.array([[
        total, churn, avg_chg,
        additions, deletions, changed_files,
        cpm, rev_int, commits,
        has_reviewer, 1-has_reviewer, 0, 0,
        24.0, 0, 1, 0,
        keyword_count, total//10, has_test,
        0, 0, 0, 20,
        comments, comments
    ]])

    feat_scaled = scaler.transform(feat)
    bug_prob    = xgb.predict_proba(feat_scaled)[0][1]

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bug Risk",      f"{bug_prob:.0%}",
              " High" if bug_prob > 0.6 else "Low")
    c2.metric("Lines Changed", f"{total}")
    c3.metric("Files Changed", f"{changed_files}")
    c4.metric("Commits",       f"{commits}")

    # Gauge
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = bug_prob * 100,
        title = {'text': "Bug Risk Score (%)"},
        gauge = {
            'axis' : {'range': [0, 100]},
            'bar'  : {'color': "darkred" if bug_prob > 0.6 else "steelblue"},
            'steps': [
                {'range': [0,  40], 'color': '#d4edda'},
                {'range': [40, 70], 'color': '#fff3cd'},
                {'range': [70,100], 'color': '#f8d7da'}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Reviewer recommendations
    st.subheader(" Recommended Reviewers")
    files_list = [f.strip() for f in files_input.split(',')]
    scores     = defaultdict(float)

    for f in files_list:
        for expert, count in file_experts.get(f, {}).items():
            if expert != pr_author:
                scores[expert] += count

    recs = sorted(scores.items(), key=lambda x: -x[1])[:3]

    if recs:
        for i, (reviewer, score) in enumerate(recs, 1):
            st.markdown(f"**{i}. @{reviewer}** — expertise score: {score:.1f}")
    else:
        st.info("No reviewer history found for these files. Assign manually.")

# Tabs
tab1, tab2, tab3 = st.tabs([" Dataset", " Models", " Network"])

with tab1:
    st.subheader("Dataset Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total PRs",      len(df))
    m2.metric("Bug-fix Rate",   f"{df['is_bug_fix'].mean():.1%}")
    m3.metric("Repos",          df['repo'].nunique())
    m4.metric("Unique Authors", df['author'].nunique())

    fig2 = px.histogram(
        df, x='total_changes', color='is_bug_fix',
        nbins=50, title='PR Size by Bug Label',
        labels={'is_bug_fix':'Bug Fix','total_changes':'Lines Changed'}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Model Performance")
    metrics = pd.DataFrame({
        'Model'   : ['Logistic Reg','Random Forest',
                     'XGBoost','CodeBERT'],
        'Accuracy': [0.79, 0.84, 0.87, 0.72],
        'F1 Score': [0.76, 0.82, 0.85, 0.84],
        'ROC-AUC' : [0.81, 0.87, 0.90, 0.89]
    })
    st.dataframe(metrics, use_container_width=True)
    fig3 = px.bar(
        metrics.melt(id_vars='Model'),
        x='Model', y='value', color='variable',
        barmode='group', title='Model Comparison'
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Collaboration Network")
    try:
        st.image('data/collaboration_network.png',
                 caption='Developer collaboration graph')
    except:
        st.info("Run Day 6 notebook first to generate network chart.")