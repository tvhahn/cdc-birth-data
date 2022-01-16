import logging
from pathlib import Path
import pandas as pd
from src.data.data_prep_utils import df_from_csv_no_geo_extra
from multiprocessing import Pool
import os
import argparse


def main(folder_raw_data):
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info(
        "making the final data set WITHOUT geo data, but INCLUDING extra data (e.g APGAR data)"
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
        df_list = pool.map(df_from_csv_no_geo_extra, file_list)

        # reduce the list of dataframes to a single dataframe
        combined_df = pd.concat(df_list, ignore_index=True)

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

    df.to_csv(
        project_dir / "data/processed" / "births_simple_with_apgar.csv", index=False
    )
