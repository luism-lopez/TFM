import pandas as pd
import algorithm

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

def perform_cross_validation(dataset, user_origin, user_month, min_days, max_days, min_expense, max_expense):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    mae_scores = []
    accuracy_scores = []

    for train_idx, test_idx in kf.split(dataset):
        train_data, test_data = dataset.iloc[train_idx], dataset.iloc[test_idx]

        train_recommendations = algorithm.generate_recommendations(train_data, user_origin, user_month, min_days, max_days, min_expense, max_expense, 5)
        test_recommendations = algorithm.generate_recommendations(test_data, user_origin, user_month, min_days, max_days, min_expense, max_expense, 5)

        num_recommendations = min(len(train_recommendations), len(test_recommendations))

        train_scores = [item[2] for item in train_recommendations[:num_recommendations]]
        test_scores = [item[2] for item in test_recommendations[:num_recommendations]]

        # CLEAN NaN VALUES
        train_scores = [score for score in train_scores if not pd.isna(score)]
        test_scores = [score for score in test_scores if not pd.isna(score)]

        # Check if both train_scores and test_scores have data
        if len(train_scores) > 0 and len(test_scores) > 0:
            # MAE
            mae = mean_absolute_error(train_scores, test_scores)
            mae_scores.append(mae)

            # ACCURACY
            tolerance = 15.0

            num_within_tolerance = sum(1 for a, b in zip(train_scores[:num_recommendations], test_scores[:num_recommendations]) if abs(a - b) <= tolerance)
            accuracy = (num_within_tolerance / num_recommendations) * 100.0
            accuracy_scores.append(accuracy)

    if mae_scores and accuracy_scores:
        avg_mae = sum(mae_scores) / len(mae_scores)
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        return avg_mae, avg_accuracy
    else:
        return None, None
