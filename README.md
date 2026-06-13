# AI Code Review Intelligence System

An AI-powered system that predicts bug-introducing pull requests and recommends
the best reviewer using CodeBERT, XGBoost, and graph-based ML on real GitHub data.

## What it does
- Predicts which PRs are likely to introduce bugs (CodeBERT + XGBoost)
- Recommends optimal reviewers using developer collaboration graph
- Explains predictions with SHAP feature importance
- Live Streamlit dashboard with real-time PR analysis

## Tech Stack
Python · CodeBERT · XGBoost · Scikit-learn · NetworkX · SHAP · 
FastAPI · Streamlit · GitHub API · Pandas · NLP

## Dataset
1500+ real PRs collected from microsoft/vscode, facebook/react, 
kubernetes/kubernetes via GitHub API

