import os
import sys
import pandas as pd
from azure.storage.blob import BlobClient


def main():

    blob = BlobClient(account_url=os.getenv("ACCOUNT_URL"),
                      container_name=os.getenv("CONTAINER_NAME"),
                      blob_name=os.getenv("BLOB_NAME"),
                      credential=os.getenv("STORAGE_KEY"))

    with open("raw_data.csv", "wb") as f:
        data = blob.download_blob()
        data.readinto(f)

    req_data = pd.read_csv("raw_data.csv")

    # Check for missing values in the dataset
    # Columns to be used (Add a column called "Age")
    check_cols = ['Pclass', 'Sex', 'SibSp', 'Parch', 'Fare', 'Survived']

    # Uncomment this line to show failure of this test
    # check_cols = ['Pclass', 'Sex', 'SibSp', 'Parch',
    #               'Fare', 'Age', 'Survived']

    # Temp dataset
    tmp_df = req_data[check_cols].copy()

    # Count the missing values in the dataset
    num_missing = sum(tmp_df.isnull().sum())

    if num_missing > 0:
        print("There are missing values in the dataset\n")
        # Printing missing value summary
        print(f"--" * 75)
        print(tmp_df.isnull().sum())
        print(f"--" * 75)
        sys.exit(1)
    else:
        print(f"--" * 75)
        print("There are no missing values in the dataset")
        print(f"--" * 75)


if __name__ == '__main__':
    main()
