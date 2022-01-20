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
        df (pd.DataFrame): The prepared birth data. Requires columns: 
            "conc_yy", "conc_month", "dob_yy", "birth_month", "conc_mm", "dob_mm", "births",
        years_greater_than (int): Only include data from above this year.

    """
    df["avg_births"] = df.groupby(["dob_yy", "dob_mm"])["births"].transform("mean")
    df["percent_above_average"] = (
        df["births"] / df["avg_births"] - 1
    ).round(2)

    return df


def human_format(num):
    """Make a nice human readable format for numbers."""
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return "%.2f%s" % (num, ["", "K", "M", "B", "T", "P"][magnitude])


###############################################################################
# Main functions
###############################################################################


def plot_births_by_month(df, year=1990, path_save_dir=None, dpi=300, save_plot=True):
    """Plot the births by month for a given year.

    Args:
        df (pd.DataFrame): The raw birth data. Requires columns: dob_yy, dob_mm, births.
        year (int): The year to filter the data to.

    """

    df = filter_by_year(df, filter_cat="dob_yy", year=year)

    # plot
    sns.set(font_scale=1.1, style="whitegrid")  # set format

    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(6, 8),
    )

    y_val = "birth_month"

    sns.barplot(x="births", y=y_val, data=df, palette="Blues_d", ci=None)

    for i, p in enumerate(ax.patches):
        # help from https://stackoverflow.com/a/56780852/9214620
        space = df["births"].max() * 0.01
        _x = p.get_x() + p.get_width() + float(space)
        _y = p.get_y() + p.get_height() / 2
        value = p.get_width()
        ax.text(
            _x,
            _y,
            f"{human_format(value)}",
            ha="left",
            va="center",
            weight="semibold",
            size=12,
        )

    ax.spines["bottom"].set_visible(True)
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.grid(alpha=1, linewidth=1, axis="x")
    ax.set_xticks([0])
    ax.set_xticklabels([])
    ax.set_xlim(left=3e4)
    plt.title(
        f"Month Babies Were Born\n(for babies born in {year})", loc="left"
    )

    sns.despine(left=True, bottom=True)

    # save plot as svg and png
    if save_plot:
        if path_save_dir is None:
            path_save_dir = Path.cwd().parent.parent

        plt.savefig(
            path_save_dir / f"{year}_births_by_month.svg", bbox_inches="tight", dpi=dpi
        )

        plt.savefig(
            path_save_dir / f"{year}_births_by_month.png", bbox_inches="tight", dpi=dpi
        )
    else:
        plt.show()


def main():
    logger = logging.getLogger(__name__)
    logger.info("making figures from consolidated tables")

    path_save_dir = root_dir / "reports/figures/"
    path_data_dir = root_dir / "data/processed/"

    # load the births_simple.csv file and prepare for analysis
    df = pd.read_csv(path_data_dir / "births_simple.csv", dtype=int).sort_values(
        by=["dob_yy", "dob_mm"]
    )
    # create dfp
    dfp = df_birth_no_geo_prep(df)

    plot_births_by_month(
        dfp, year=1990, path_save_dir=path_save_dir, dpi=300, save_plot=True
    )


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    root_dir = Path(__file__).resolve().parents[2]

    main()
