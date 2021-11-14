import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pathlib
import os
import zipfile
from multiprocessing import Pool


def df_from_csv_with_geo(file_path, nrows=None):
    """Extract useful columns from birth record csv
    Takes a csv path. CSV must be before 2005 to include geo data.
    """

    # get year of CSV
    year = int(str(file_path).split("/")[-1][4:8])

    # no geo data before 1982 or after 2004
    if year > 2004 or year < 1982:
        pass

    else:

        # load FIPS code data
        df_fips = pd.read_csv(
            file_path.parent.parent / "external" / "all-geocodes-v2017.csv", dtype=str
        )

        # get the fips codes for the states only
        df_fips = df_fips[
            (df_fips["County Code (FIPS)"] == "000")
            & (df_fips["County Subdivision Code (FIPS)"] == "00000")
            & (df_fips["Place Code (FIPS)"] == "00000")
            & (df_fips["Consolidtated City Code (FIPS)"] == "00000")
        ][
            [
                "State Code (FIPS)",
                "Area Name (including legal/statistical area description)",
            ]
        ]

        # rename columns in df
        df_fips.columns = ["state_fips", "state_name_mr"]

        # require differnt column names depending on year
        # columns for 2003+
        col_load_1 = [
            "dob_yy",
            "dob_mm",
            "dob_wk",
            "mrstate",
            "mrcntyfips",
            "mrcityfips",
            "apgar5",
        ]

        # columns for 1989-2002
        col_load_2 = [
            "biryr",
            "birmon",
            "weekday",
            "stresfip",
            "cntyrfip",
            "cityres",
            "fmaps",
        ]
        rename_col2 = [
            "dob_yy",
            "dob_mm",
            "dob_wk",
            "mrstate",
            "mrcntyfips",
            "mrcityfips",
            "apgar5",
        ]

        # columns for 1982 through 1988
        col_load_3 = [
            "datayear",
            "birmon",
            "birday",
            "stresfip",
            "cntyrfip",
            "cityres",
            "fmaps",
        ]
        rename_col3 = [
            "dob_yy",
            "dob_mm",
            "dob_day",
            "mrstate",
            "mrcntyfips",
            "mrcityfips",
            "apgar5",
        ]

        # create dictionary to rename older csvs
        col_rename_dict2 = dict(zip(col_load_2, rename_col2))
        col_rename_dict3 = dict(zip(col_load_3, rename_col3))

        # if the CSVs are of newer format
        if year >= 2003:
            # load abbreviation csv so we can rename AK to Alaska, etc.
            df_abbr = pd.read_csv(
                file_path.parent.parent / "external" / "state_abbreviations.csv",
                header=None,
                names=["state", "abbr"],
            )

            # load only select columns, and set dtype for columns
            df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)

            # get the full state name and append them onto the df
            df = (
                pd.merge(
                    df,
                    df_abbr,
                    left_on="mrstate",
                    right_on="abbr",
                    how="inner",
                    copy=False,
                )
                .drop(["abbr"], axis=1)
                .drop(["mrstate"], axis=1)
            )
            df = df.rename(columns={"state": "state_name_mr"})

            # get state FIPS code and append
            df = pd.merge(
                df,
                df_fips,
                left_on="state_name_mr",
                right_on="state_name_mr",
                how="inner",
                copy=False,
            )
            df = df.rename(columns={"state_fips": "mrstatefips"})

            # drop any rows with NaN's
            df = df.dropna()

        # if the CSVs are of older format
        else:

            if year >= 1989:
                col_load, col_rename_dict = col_load_2, col_rename_dict2
            else:
                col_load, col_rename_dict = col_load_3, col_rename_dict3

            # load only select columns from the birth CSV
            df = pd.read_csv(
                file_path, nrows=nrows, usecols=col_load, dtype=str
            ).rename(columns=col_rename_dict)

            # rename 'mrstate' column
            df = df.rename(columns={"mrstate": "mrstatefips"})

            # merge the df_stat_fips to get the full state name
            df = pd.merge(
                df,
                df_fips,
                left_on="mrstatefips",
                right_on="state_fips",
                how="inner",
                copy=False,
            ).drop(["state_fips"], axis=1)

            # years before 1989 only show a single digit (i.e. 2 for 1982)
            if year < 1989:
                df = df.drop(columns=["dob_yy"])
                df["dob_yy"] = np.array([year] * df.shape[0])

            # drop any rows with NaN's
            df = df.dropna()

        # return the dataframe, and order the columns in a fixed manner
        return df[
            [
                "dob_yy",
                "dob_mm",
                "mrcntyfips",
                "mrcityfips",
                "state_name_mr",
                "mrstatefips",
                "apgar5",
            ]
        ].astype({"dob_mm": int, "dob_yy": int, "apgar5": int})


def df_from_csv_no_geo(file_path, nrows=None):
    """Extract useful columns from birth record csv
    Takes a csv path. Produces a dataframe without geo data.
    Good for all years of data collection.
    """

    # get year of CSV
    year = int(str(file_path).split("/")[-1][4:8])

    # require differnt column names depending on year
    # columns for 2003+
    col_load_1 = ["dob_yy", "dob_mm"]

    # columns for 1989-2002
    col_load_2 = ["biryr", "birmon"]
    rename_col2 = ["dob_yy", "dob_mm"]

    # columns for 1982 through 1988
    col_load_3 = ["datayear", "birmon"]
    rename_col3 = ["dob_yy", "dob_mm"]

    # create dictionary to rename older csvs
    col_rename_dict2 = dict(zip(col_load_2, rename_col2))
    col_rename_dict3 = dict(zip(col_load_3, rename_col3))

    # create dictionary to rename older CSVs from 1991 to 2002
    col_rename_dict = dict(zip(col_load_2, col_load_1))

    # if the CSVs are of newer format
    if year >= 2003:

        # load only select columns, and set dtype for columns
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm"])
        )

    elif year > 1988 and year < 2004:

        # load only select columns from the birth CSV
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_2, dtype=str).rename(
            columns=col_rename_dict2
        )

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm"])
        )

    # if the CSVs are of older format
    else:

        # load only select columns from the birth CSV
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_3, dtype=str).rename(
            columns=col_rename_dict3
        )

        # years before 1989 only show a single digit (i.e. 2 for 1982)
        df = df.drop(columns=["dob_yy"])
        df["dob_yy"] = np.array([year] * df.shape[0])

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm"])
        )

    # return the dataframe, and order the columns in a fixed manner
    return df[["dob_yy", "dob_mm", "births"]].astype(
        {"dob_mm": int, "dob_yy": int, "births": int}
    )


def df_from_csv_no_geo_extra(file_path, nrows=None):
    """Extract useful columns from birth record csv
    Takes a csv path. Produces a dataframe without geo data.
    Includes extra columns, such as apgar5, from 1978 onwards.
    """

    # get year of CSV
    year = int(str(file_path).split("/")[-1][4:8])

    # require differnt column names depending on year
    # columns for 2003+
    col_load_1 = ["dob_yy", "dob_mm", "apgar5"]

    # columns for 1989-2002
    col_load_2 = ["biryr", "birmon", "fmaps"]
    rename_col2 = ["dob_yy", "dob_mm", "apgar5"]

    # columns for 1982 through 1988
    col_load_3 = ["datayear", "birmon", "fmaps"]
    rename_col3 = ["dob_yy", "dob_mm", "apgar5"]

    # create dictionary to rename older csvs
    col_rename_dict2 = dict(zip(col_load_2, rename_col2))
    col_rename_dict3 = dict(zip(col_load_3, rename_col3))

    # create dictionary to rename older CSVs from 1991 to 2002
    col_rename_dict = dict(zip(col_load_2, col_load_1))

    # if the CSVs are of newer format
    if year >= 2003:

        # load only select columns, and set dtype for columns
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm", "apgar5"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm", "apgar5"])
        )

    elif year > 1988 and year < 2004:

        # load only select columns from the birth CSV
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_2, dtype=str).rename(
            columns=col_rename_dict2
        )

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm", "apgar5"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm", "apgar5"])
        )

    # if the CSVs are of older format
    elif year > 1977 and year <= 1988:

        # load only select columns from the birth CSV
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_3, dtype=str).rename(
            columns=col_rename_dict3
        )

        # years before 1989 only show a single digit (i.e. 2 for 1982)
        df = df.drop(columns=["dob_yy"])
        df["dob_yy"] = np.array([year] * df.shape[0])

        # drop any rows with NaN's
        df = df.dropna()

        df["births"] = np.ones(df.shape[0])
        df = (
            df.groupby(["dob_yy", "dob_mm", "apgar5"], as_index=False)
            .count()
            .sort_values(by=["dob_yy", "dob_mm", "apgar5"])
        )
    # if the csvs are older than 1978 they do not have relevant cols
    # like apgar, and thus we skip them
    else:
        pass

    # return the dataframe, and order the columns in a fixed manner
    return df[["dob_yy", "dob_mm", "apgar5", "births"]].astype(
        {"dob_mm": int, "dob_yy": int, "apgar5": int, "births": int}
    )
