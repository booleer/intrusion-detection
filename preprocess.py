import pandas as pd
import numpy as np
from src.util import transform_datasets
from src.preprocessing import full_data, split_data, full_components
from src.model import intrusion_detector


def preprocess_datasets(X_safe, X_train, y_train, X_test):
    best = intrusion_detector(X_safe, gmm_components=36, pca_components=28, neighbors=10)
    best.fit(X_train, y_train)

    preprocessed_safe = best.predict_attack_probability(X_safe)
    preprocessed_train = best.predict_attack_probability(X_train)
    preprocessed_test = best.predict_attack_probability(X_test)
    return preprocessed_safe, preprocessed_train, preprocessed_test


def main():
    np.random.seed(0)
    safe_dataset, train_dataset, test_dataset = transform_datasets(full_data)
    components_safe, components_train, components_test = transform_datasets(full_components)

    X_safe, y_safe = split_data(safe_dataset)
    X_train, y_train = split_data(train_dataset)
    X_test, y_test = split_data(test_dataset)

    preprocessed_safe, preprocessed_train, preprocessed_test = preprocess_datasets(X_safe, X_train, y_train, X_test)


if __name__ == '__main__':
    main()