import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pathlib
import seaborn as sns
import datetime
import logging
import os
import argparse

from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import plotly.io as pio

###############################################################################
# Helper functions
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


def df_birth_no_geo_prep(df, filter_year=None):
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


###############################################################################
# Main function
###############################################################################


def main():
    pass


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    root_dir = Path(__file__).resolve().parents[2]

    main()
