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
from src.data.data_prep_utils import percentage_birts_by_month, filter_by_year, df_birth_no_geo_prep

###############################################################################
# Helper functions
###############################################################################

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


def plot_births_by_month_violin(df, start_year=1981, end_year=2020, path_save_dir=None, dpi=300, save_plot=True):
    """"Take the prepared df and output the violin plot of percentage change by month"""

    dfp = percentage_birts_by_month(df, years_greater_than=1980)
    dfp = dfp[(dfp['dob_yy'] >= start_year) & (dfp['dob_yy'] <= end_year)]

    # round to 2 decimal places to look nice
    dfp['percent_above_avg'] = np.round(dfp['percent_above_avg'],2)

    print(dfp['dob_yy'].max())

    TITLE = f"Monthly Increase/Decrease in Births, {start_year}-{end_year}"
    X_LABEL = 'Percentage Above/Below Yearly Average'

    # make plotly violin plot
    fig = go.Figure(data=go.Violin(x=dfp["percent_above_avg"],
                                y=dfp['birth_month'],
                                
                                # add a custom text using list comprehension and zip
                                text = [f'{month}, {v:.2f}%' for month, v, in 
                                        zip(dfp['dob_yy'],dfp['percent_above_avg'])],
                                
                                hoverinfo='text', # show the custom text for hover
                                orientation='h', #horizontal orientation
                                box_visible=False, # don't show box-plot
                                meanline_visible=False, # hide meanline in violins
                                line_color='dimgrey', 
                                fillcolor='white',
                                opacity=1,
                                marker_symbol="circle",
                                marker_color='dimgrey',
                                marker_opacity=0.3, 
                                marker_size=10,
                                pointpos=0, # put scatters in middle of violin
                                jitter=0.7, 
                                scalemode='width',
                                width=1.2,
                                points='all',
                                ))


    # add shaded regions
    shaded_region_list = []

    # get min/max for shaded region
    xmin = np.min(dfp['percent_above_avg'])*1.3
    xmax = np.max(dfp['percent_above_avg'])*1.3

    # negative birth percentage area
    shaded_region_list.append(
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=xmin*0.95,
                        y0=0,
                        x1=0,
                        y1=1,
                        fillcolor="red",
                        opacity=0.1,
                        layer="below",
                        line_width=0,
                    )
                )

    # positive birth percentage area
    shaded_region_list.append(
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=0,
                        y0=0,
                        x1=xmax*0.95,
                        y1=1,
                        fillcolor="green",
                        opacity=0.1,
                        layer="below",
                        line_width=0,
                    )
                )

    # set "tight" layout https://community.plotly.com/t/plt-tight-layout-in-plotly/10204/2
    fig.update_layout(yaxis_zeroline=False, 
                    width=600, 
                    height=700,
                    template='plotly_white',
                    margin=dict(l=2, r=2, t=25, b=2), # create a "tight" layout
                    xaxis=dict(range=[xmin, xmax], tickvals = [-10, -5, 0, 5, 10]),
                    title=TITLE,
                    title_x=0.55, # title position
                    titlefont=dict(family='DejaVu Sans', color='#333333', size=16), 
                    shapes=shaded_region_list
                    )


    # update x and y axes
    # https://plotly.com/python/axes/
    fig.update_xaxes(showgrid=False, 
                    zeroline=True,
                    zerolinecolor='lightgrey',
                    zerolinewidth=2,
                    title_text=X_LABEL,
                    tickfont=dict(family='DejaVu Sans', color='#333333', size=14), # set custom font
                    titlefont=dict(family='DejaVu Sans', color='#333333', size=14),
                    fixedrange=False # allow zooming by not fixing range
                    )

    fig.update_yaxes(tickfont=dict(family='DejaVu Sans', color='#333333', size=14), 
                    fixedrange=False
                    )

    # other config options: https://plotly.com/python/configuration-options/
    # fig.show(config={"displayModeBar": False, "showTips": False})

    # save fig as a png
    if save_plot:
        if path_save_dir is None:
            path_save_dir = Path.cwd().parent.parent

        fig.write_image(path_save_dir / f"{start_year}-{end_year}_births_by_month_percent_above_avg.png", scale=2)
    else:
        pass






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
    df = df_birth_no_geo_prep(df)

    plot_births_by_month(
        df, year=1990, path_save_dir=path_save_dir, dpi=300, save_plot=True
    )

    plot_births_by_month_violin(df, start_year=1981, end_year=2020, path_save_dir=path_save_dir, dpi=300, save_plot=True)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    root_dir = Path(__file__).resolve().parents[2]

    main()
