from sklearn.preprocessing import LabelEncoder


def get_status(df, Title_Dictionary):
    # a map of more aggregated title
    # we map each title
    df['Status'] = df["Title"].map(lambda x: Title_Dictionary[x])
    return df


def add_title_features(df):

    Title_Dictionary = {"Capt": "Officer", "Col": "Officer",
                        "Major": "Officer", "Jonkheer": "Royalty",
                        "Don": "Royalty", "Sir": "Royalty",
                        "Dr": "Officer", "Rev": "Officer",
                        "the Countess": "Royalty", "Mme": "Mrs",
                        "Mlle": "Miss", "Ms": "Mrs", "Mr": "Mr",
                        "Mrs": "Mrs", "Miss": "Miss",
                        "Master": "Master", "Lady": "Royalty"}

    df['Title'] = df['Name'].map(lambda name:
                                 name.split(',')[1].split('.')[0].strip())
    print(df["Title"].isnull().sum())

    new_df = get_status(df, Title_Dictionary)

    return new_df


def create_new_features(clean_df):
    """
    Function to create new features using the cleansed data
    clean_df (DataFrame)    : DataFrame which is used to create new features
    return (DataFrame)      : DataFrame with the derived features
    """
    # Convert gender feature to numbers
    genders = {"male": 0, "female": 1}
    clean_df['Sex'] = clean_df['Sex'].map(genders)

    # use engineered features
    use_eng_features = False

    if use_eng_features:
        # Engineered features
        eng_df = add_title_features(clean_df)
        le = LabelEncoder()
        eng_df['Title'] = le.fit_transform(eng_df['Title'])
        eng_df['Status'] = le.fit_transform(eng_df['Status'])

        # Keep only these columns for modeling
        X_cols = ['Passenger_Class', 'Sex', 'SibSp',
                  'Parch', 'Fare', 'Title', 'Status']
        Y_col = ["Survived"]

        req_df = eng_df[X_cols + Y_col].copy()

    else:
        # Keep only these columns for modeling
        X_cols = ['Passenger_Class', 'Sex', 'SibSp', 'Parch', 'Fare']
        Y_col = ["Survived"]

        eng_df = clean_df.copy()
        req_df = eng_df[X_cols + Y_col].copy()

    return req_df
