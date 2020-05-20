

def create_new_features(clean_df):
    """
    Function to create new features using the cleansed data
    clean_df (DataFrame)    : DataFrame which is used to create new features
    return (DataFrame)      : DataFrame with the derived features
    """
    # Convert gender feature to numbers
    genders = {"male": 0, "female": 1}
    clean_df['Sex'] = clean_df['Sex'].map(genders)

    # Keep only these columns for modeling
    X_cols = ['Passenger_Class', 'Sex', 'SibSp', 'Parch', 'Fare']
    Y_col = ["Survived"]

    # Subsetting and keeping only those columns
    req_df = clean_df[X_cols+Y_col].copy()

    return req_df


