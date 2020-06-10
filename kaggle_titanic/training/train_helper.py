from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


def split_data(df, X_cols, target_col):
    X = df[X_cols].values
    y = df[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42)
    data = {"train": {"X": X_train, "y": y_train},
            "test": {"X": X_test, "y": y_test}}
    return data


# Evaluate the metrics for the model
def get_model_metrics(model, data):
    preds = model.predict(data["test"]["X"])
    accuracy = round(accuracy_score(data["test"]["y"], preds), 2)
    metrics = {"accuracy": accuracy}
    return metrics


# Train the model, return the model
def train_model(data, train_params):

    # Getting the number of estimators from the parameters file
    n_estimators = train_params["Random_Forest"]["n_estimators"]

    # Fit the model
    clf_model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf_model.fit(data["train"]["X"], data["train"]["y"])

    return clf_model
