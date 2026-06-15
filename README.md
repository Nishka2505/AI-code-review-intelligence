#  AI Code Review Intelligence System


#LIVE DEMO -https://ai-code-review-intelligence-hqkxc5n4gjutjgapptjbvqd.streamlit.app/

An AI system that predicts bug-introducing PRs and recommends 
reviewers using CodeBERT, XGBoost, and graph-based ML on real GitHub data.

## Results
| Model | Accuracy | F1 Score | ROC-AUC |
|-------|----------|----------|---------|
| Logistic Regression | 79% | 0.76 | 0.81 |
| Random Forest | 84% | 0.82 | 0.87 |
| XGBoost | 87% | 0.85 | 0.90 |
| CodeBERT (fine-tuned) | 72% | 0.84 | 0.89 |

- Dataset: 900+ PRs from microsoft/vscode, facebook/react, kubernetes/kubernetes
- Reviewer recommendation top-3 hit rate: ~60%+
- Features engineered: 26 structural + text features

## Stack
Python · CodeBERT · XGBoost · NetworkX · Streamlit · GitHub API · SHAP · FastAPI

## Run locally
pip install -r requirements.txt
streamlit run app/dashboard.py

## Future Work
GitHub Action integration — auto-analyse PRs on any repo via webhook
Fine-tune CodeBERT on domain-specific codebases
Add multi-language support beyond Python/JavaScript
Real-time PR monitoring via GitHub webhooks
