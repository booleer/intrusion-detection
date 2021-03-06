import pandas as pd
import numpy as np
from src.util import transform_datasets
from src.preprocessing import full_data, split_data
from sklearn.model_selection import StratifiedKFold
from src.model import cov_detector, dual_cov_detector
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import FactorAnalysis, PCA
import argparse
import sys


def train_valid_split(X, y, shuffle=True):
    skf = StratifiedKFold(n_splits=2, shuffle=shuffle)
    train, valid = skf.split(X, y)
    train_index = train[0]
    valid_index = valid[0]
    return X[train_index], y[train_index], X[valid_index], y[valid_index]


def experiment(exp, seed, dual=False):
    np.random.seed(seed)

    safe_dataset, train_dataset, test_dataset = transform_datasets(full_data)

    X_safe, y_safe = split_data(safe_dataset)
    X_train, y_train = split_data(train_dataset)
    X_test, y_test = split_data(test_dataset)

    X_train, y_train, X_valid, y_valid = train_valid_split(X_train, y_train)

    if dual is True:
        exp.fit_cov(X_safe, X_train)
    else:
        exp.fit_cov(X_safe)
    exp.fit(X_train, y_train)
    
    print("Safe fp: {}".format(exp.false_positives(X_safe, y_safe)))
    print("Valid MCC: {:.3f}".format(exp.score(X_valid, y_valid)))
    print("Valid fp: {}".format(exp.false_positives(X_valid, y_valid)))


def single_estimator_experiment(args):
    if args.estimator[0] == "GMM":
        estimator = GaussianMixture(n_components=args.components[0], covariance_type='full')
    elif args.estimator[0] == "FA":
        estimator = FactorAnalysis(n_components=args.components[0])
    elif args.estimator[0] == "PCA":
        estimator = PCA(n_components=args.components[0], whiten=True)
    else:
        print("Invalid estimator:", args.estimator)
        print("Supported estimators: 'GMM', 'FA', 'PCA'")
        error_exit()
    estimator_experiment = cov_detector(estimator, neighbors=args.neighbors, weights='uniform')
    experiment(estimator_experiment, seed=args.seed)


def dual_estimator_experiment(args):
    if args.estimator[0] == "GMM":
        first_est = GaussianMixture(n_components=args.components[0], covariance_type='full')
    elif args.estimator[0] == "FA":
        first_est = FactorAnalysis(n_components=args.components[0])
    elif args.estimator[0] == "PCA":
        first_est = PCA(n_components=args.components[0], whiten=True)
    else:
        print("Invalid estimator:", args.estimator[0])
        print("Supported estimators: 'GMM', 'FA', or 'PCA'")
        error_exit()

    if len(args.components) < 2:
        print("Error: missing second estimator components.")
        error_exit()

    if args.estimator[1] == "GMM":
        second_est = GaussianMixture(n_components=args.components[1], covariance_type='full')
    elif args.estimator[1] == "FA":
        second_est = FactorAnalysis(n_components=args.components[1])
    elif args.estimator[1] == "PCA":
        second_est = PCA(n_components=args.components[1], whiten=True)
    else:
        print("Invalid estimator:", args.estimator[1])
        print("Supported estimators: 'GMM', 'FA', or 'PCA'")
        error_exit()

    dual_estimator = dual_cov_detector(first_est, second_est, neighbors=args.neighbors, weights='uniform')
    experiment(dual_estimator, seed=args.seed, dual=True)


def error_exit():
    parser.print_usage()
    sys.exit(-1)


def main(args):
    if args.estimator is None:
        print("Error: missing an estimator. Valid options are: 'GMM', 'FA', or 'PCA'")
        error_exit()
    elif args.components is None:
        print("Error: missing number of components.")
        error_exit()
    elif len(args.estimator) == 1:
        single_estimator_experiment(args)
    elif len(args.estimator) == 2:
        dual_estimator_experiment(args)
    else:
        error_exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--estimator", help="the covariance matrix estimator", nargs='+')
    parser.add_argument("-c", "--components", help="the number of components", type=int, nargs='+')
    parser.add_argument("-n", "--neighbors", help="the number of neighbors", type=int, nargs='?', default=10)
    parser.add_argument("-s", "--seed", help="initial seed", type=int, nargs='?', default=0)

    main(args=parser.parse_args())
