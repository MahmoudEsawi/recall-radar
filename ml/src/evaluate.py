"""
Model Evaluation with Strict Temporal Split and Imbalance Metrics.
Maintained by Ghadeer & Aya.
"""

import numpy as np
from sklearn.metrics import precision_recall_curve, roc_auc_score, auc, confusion_matrix


def temporal_train_test_split(df, split_date="2020-01-01", date_col="COMPLAINT_DATE"):
    """
    Prevents data leakage by training only on past years and testing on future years.
    """
    train_mask = df[date_col] < split_date
    test_mask = df[date_col] >= split_date
    return df[train_mask], df[test_mask]


def compute_imbalance_metrics(y_true, y_prob, top_k=20):
    """
    Calculates PR-AUC, ROC-AUC, and Precision@k for recall alerts.
    """
    roc_auc = roc_auc_score(y_true, y_prob)
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)
    
    # Precision@k
    top_k_indices = np.argsort(y_prob)[::-1][:top_k]
    precision_at_k = np.mean(y_true.iloc[top_k_indices] if hasattr(y_true, "iloc") else y_true[top_k_indices])
    
    return {
        "ROC_AUC": float(roc_auc),
        "PR_AUC": float(pr_auc),
        f"Precision@{top_k}": float(precision_at_k)
    }
