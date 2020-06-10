# File which contains helper functions for cleaning data

from pandas import to_datetime


def convert_to_datetime(df, colname, format):
    """
    Function to convert a column into datetime
    df      : Input Dataframe
    colname : Column which needs to be converted
    format  : Datetime Format
    return  : DataFrame
    """

    # Convert to datetime
    df[colname] = to_datetime(df[colname], format=format)


def rename_columns(df, mapping):
    # Rename columns
    df = df.rename(columns=mapping)
    return df
