# 🧠 ML & Data Science Pipeline

This directory is maintained by **Ghadeer, Aya & Mahdy**.

## Team Ownership & Pipeline Stages

1. **`src/etl.py` (Data Ingestion & Ground Truth Labeling) — Lead: Mahdy**
   - Ingests raw NHTSA complaints and recalls.
   - Cleans and standardizes `Make`, `Model`, `Year`, and `Component`.
   - Links complaints to recalls to create the ground truth target:
     `recall_within_12m` = `1` if an official recall was published within 12 months after complaint date, else `0`.
   - Outputs: `data/processed/clean_complaints.parquet` and `data/processed/labels.parquet`.

2. **`src/nlp_clustering.py` (Text & Defect Clustering) — Lead: Ghadeer**
   - Applies TF-IDF vectorization on complaint narratives (`CDESCR`).
   - Reduces dimensionality via TruncatedSVD/PCA.
   - Clusters complaints using K-Means into distinct failure modes.
   - Evaluates safety-critical keywords (fire, stall, crash, injury) via Naive Bayes / SVM.

3. **`src/time_series.py` (Trend & Anomaly Features) — Lead: Aya**
   - Calculates monthly complaint growth slopes (`Linear Regression` with p-value).
   - Computes expected complaints baseline using `Poisson Regression` to detect abnormal surges.
   - Builds monthly cluster velocity and acceleration features.

4. **`src/train_models.py` (Supervised Classification) — Lead: Mahdy & Aya**
   - Combines features into a unified dataset.
   - Trains baseline: `Logistic Regression` (interpretable coefficients).
   - Trains comparison models: `Random Forest`, `Gradient Boosting`, `KNN`.
   - Exports the best model to `ml/artifacts/model.joblib`.

5. **`src/evaluate.py` (Validation & Benchmarking) — Lead: Ghadeer & Mahdy**
   - Enforces **Strict Temporal Split** (Train on past years, test on future years — NO random split!).
   - Computes: `PR-AUC`, `ROC-AUC`, `Precision@k`, and `Lead Time` (months prior to recall).
