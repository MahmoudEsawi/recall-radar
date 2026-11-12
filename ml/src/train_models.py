"""
Supervised Model Training & Comparison.
Maintained by Aya & Ghadeer.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
import joblib
from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"


def train_and_compare(X_train, y_train, X_test, y_test):
    """
    Trains baseline Logistic Regression and benchmark models.
    """
    models = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Decision_Tree": DecisionTreeClassifier(max_depth=5),
        "Random_Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
        "Gradient_Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5)
    }

    results = {}
    best_model = None
    best_score = -1.0

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        results[name] = score
        print(f"  {name} Accuracy: {score:.4f}")
        if score > best_score:
            best_score = score
            best_model = model

    # Save best model to artifacts for Backend ingestion
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, ARTIFACTS_DIR / "model.joblib")
    print(f"\nSaved champion model to {ARTIFACTS_DIR / 'model.joblib'}")
    return results
