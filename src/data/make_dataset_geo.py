import logging
from pathlib import Path
import pandas as pd
from src.data.data_prep_utils import df_from_csv_with_geo
from multiprocessing import Pool
import os
import numpy as np
import argparse


def main(folder_raw_data):
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info(
        "making the final data set with geo data, but nothing extra (e.g APGAR data)"
    )

    # get a list of file names
    files = os.listdir(folder_raw_data)

    file_list = [
        Path(folder_raw_data) / filename
        for filename in files
        if filename.endswith(".csv")
    ]

    # set up your pool
    with Pool(processes=args.n_cores) as pool:  # or whatever your hardware can support

        # have your pool map the file names to dataframes
        df_list = pool.map(df_from_csv_with_geo, file_list)

        # reduce the list of dataframes to a single dataframe
        combined_df = pd.concat(df_list, ignore_index=True)
        print(combined_df.shape)

        return combined_df


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    parser = argparse.ArgumentParser(description="Build data sets for analysis")

    parser.add_argument(
        "--n_cores",
        type=int,
        default=16,
        help="Number of cores to use for multiprocessing",
    )

    args = parser.parse_args()

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    print(type(project_dir))

    df = main(project_dir / "data/raw/")
    print("Final df shape:", df.shape)

    df["births"] = np.ones(df.shape[0])
    df.to_csv(
        project_dir / "data/processed" / "births_with_geo_apgar.csv.gz",
        compression="gzip",
        index=False,
    )

    # create a birth count for each unique geo and date
    # this should reduce the size of the df significantly
    # df = df.drop(columns=["apgar5"]) # not needed in consolidated table
    df = (
        df.groupby(list(df.columns)[:-1], as_index=False)
        .count()
        .sort_values(by=["dob_yy", "dob_mm"])
    )
    print("Shape after consolidated birth count:", df.shape)

    df.to_csv(
        project_dir / "data/processed" / "births_with_geo_apgar_consolidated.csv.gz",
        compression="gzip",
        index=False,
    )
