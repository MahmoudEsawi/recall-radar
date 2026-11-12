"""
NLP & Text Clustering Pipeline (TF-IDF + PCA + K-Means + Safety Filter).
Maintained by Ghadeer.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
import joblib


class DefectClusterer:
    def __init__(self, n_clusters: int = 8, n_components: int = 20):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=5000, 
            stop_words='english', 
            ngram_range=(1, 2)
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')

    def fit_transform(self, texts: pd.Series):
        """Vectorizes texts, applies SVD, and fits K-Means clusters."""
        cleaned_texts = texts.fillna("").astype(str)
        tfidf_matrix = self.vectorizer.fit_transform(cleaned_texts)
        reduced_matrix = self.svd.fit_transform(tfidf_matrix)
        cluster_labels = self.kmeans.fit_predict(reduced_matrix)
        return cluster_labels, reduced_matrix


def train_safety_filter(texts: pd.Series, safety_labels: pd.Series):
    """Trains a Naive Bayes classifier to identify urgent safety hazards."""
    vec = TfidfVectorizer(max_features=2000, stop_words='english')
    X = vec.fit_transform(texts.fillna(""))
    clf = MultinomialNB()
    clf.fit(X, safety_labels)
    return vec, clf
