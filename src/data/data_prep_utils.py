import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pathlib
import os
import zipfile
from multiprocessing import Pool
import datetime
from dateutil.relativedelta import relativedelta


def df_from_csv_with_geo(file_path, nrows=None):
    """Extract useful columns from birth record csv
    Takes a csv path. CSV must be before 2005 to include geo data.
    """

    # get year of CSV
    year = int(str(file_path).split("/")[-1][4:8])
    # print(year)

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
        print(f'{year} processing complete')
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
    # print(year)

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

        # 2019 and 2020 columns are capitalized
        if year >= 2019:
            col_load_1 = [col_name.upper() for col_name in col_load_1]

        # load only select columns, and set dtype for columns
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)

        df.columns = df.columns.str.lower()

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
    print(f'{year} processing complete')
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
    # print(year)

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

        # 2019 and 2020 columns are capitalized
        if year >= 2019:
            col_load_1 = [col_name.upper() for col_name in col_load_1]

        # load only select columns, and set dtype for columns
        df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)
        df.columns = df.columns.str.lower()

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
        df = pd.DataFrame(columns=["dob_yy", "dob_mm", "apgar5", "births"])

    # return the dataframe, and order the columns in a fixed manner
    print(f'{year} processing complete')
    return df[["dob_yy", "dob_mm", "apgar5", "births"]].astype(
        {"dob_mm": int, "dob_yy": int, "apgar5": int, "births": int}
    )

###############################################################################
# Functions for processing the collated data files and returning a dataframe
###############################################################################

def get_month_string(cols):
    month_index = int(cols[0])

    # from https://stackoverflow.com/a/28446432/9214620
    return datetime.date(1900, month_index, 1).strftime("%B")


def get_conception_month(cols):
    month_index = int(cols[0])
    concept_date = datetime.date(1900, month_index, 1) + relativedelta(months=-9)

    return concept_date.strftime("%B")


def get_conception_year(cols):
    month_index = int(cols[0])
    year = int(cols[1])
    concept_date = datetime.date(year, month_index, 1) + relativedelta(months=-9)

    return int(concept_date.strftime("%Y"))


def get_conception_month_index(cols):
    month_index = int(cols[0])
    concept_date = datetime.date(1900, month_index, 1) + relativedelta(months=-9)

    return int(concept_date.strftime("%m"))


def df_birth_no_geo_prep(df):
    """Prepare the birth data for analysis.

    Args:
        df (pd.DataFrame): The raw birth data. Requires columns: dob_yy, dob_mm, births.
        filter_year (int): The year to filter the data to.

    """

    # load csv is like this...
    # df = pd.read_csv(data_file, dtype=int).sort_values(by=['dob_yy', 'dob_mm', 'dob_wk'])

    # add conception month columns and birth month
    df["conc_month"] = df[["dob_mm"]].apply(get_conception_month, axis=1)
    df["birth_month"] = df[["dob_mm"]].apply(get_month_string, axis=1)
    df["conc_mm"] = df[["dob_mm"]].apply(get_conception_month_index, axis=1)
    df["conc_yy"] = df[["dob_mm", "dob_yy"]].apply(get_conception_year, axis=1)
    df = df.sort_values(by=["conc_yy", "conc_mm"])

    return df[
        [
            "conc_yy",
            "conc_month",
            "dob_yy",
            "birth_month",
            "conc_mm",
            "dob_mm",
            "births",
        ]
    ]


def df_birth_with_geo_prep(df, df_abbr):
     
     
    df = pd.merge(df, df_abbr, 
                  left_on='state_name_mr',
                  right_on='state', 
                  how='inner', copy=False).drop(['state'], axis=1)
    
    
    df = df.groupby(
        ['dob_yy', 'dob_mm', 'state_name_mr','mrstatefips','abbr'], 
        as_index=False).sum().sort_values(by=['dob_yy',
                                              'dob_mm', 
                                              'state_name_mr']).drop(columns=['mrcntyfips'])
    
    # add conception month columns and birth month
    df['conc_month'] = df[['dob_mm']].apply(get_conception_month, axis=1)
    df['birth_month'] = df[['dob_mm']].apply(get_month_string, axis=1)
    df['conc_mm'] = df[['dob_mm']].apply(get_conception_month_index, axis=1)
    df['conc_yy'] = df[['dob_mm', 'dob_yy']].apply(get_conception_year, axis=1)

    return df[['dob_yy', 'dob_mm', 'state_name_mr', 
               'mrstatefips', 'abbr', 'conc_month', 
               'birth_month', 'conc_mm', 'conc_yy', 'births']]


def filter_by_year(df, filter_cat="conc_yy", year=1990):
    """Filter df by year, either with conception year ('conc_yy')
    or birth year ('dob_yy')
    """
    df = (
        df[df[filter_cat] == year]
        .groupby(
            [
                "conc_yy",
                "conc_month",
                "dob_yy",
                "birth_month",
                "conc_mm",
                "dob_mm",
            ],
            as_index=False,
        )
        .sum()
    )
    if filter_cat == "conc_yy":
        df = df.sort_values(by=["conc_mm"]).reset_index(drop=True)
        return df
    else:
        df = df.sort_values(by=["dob_mm"]).reset_index(drop=True)
        return df


def percentage_birts_by_month(df, years_greater_than=1980):
    """Take the prepared df and calculage the average births (avg_births)
    and percent above average (percent_above_average) for each month.

    Args:
        df (pd.DataFrame): The prepared birth data (created using df_birth_no_geo_prep). 
            Requires columns: "conc_yy", "conc_month", "dob_yy", "birth_month", 
            "conc_mm", "dob_mm", "births",
        years_greater_than (int): Only include data from above this year.

    """
    # group by month
    df = df.groupby([
        'conc_yy', 'conc_month','dob_yy',
        'birth_month','conc_mm','dob_mm',], as_index=False).sum()

    df = df.sort_values(by=['dob_yy','dob_mm']).reset_index(drop=True)

    # add 12 month rolling average
    df['avg_births'] = df['births'].rolling(window=12).mean() 
    df['percent_above_avg'] = (df['births'] - df['avg_births'])/df['avg_births']*100

    # only select dates > years_greater_than
    df = df[df['dob_yy'] > years_greater_than]

    return df
