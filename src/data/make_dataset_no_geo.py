import click
import logging
from pathlib import Path
import pandas as pd
import pathlib
from src.data.data_prep_utils import df_from_csv_no_geo
from multiprocessing import Pool
import os
import numpy as np


# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
def main(folder_raw_data):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # get a list of file names
    files = os.listdir(folder_raw_data)
    file_list = [Path(folder_raw_data) / filename for filename in files if filename.endswith('.csv')]

    # set up your pool
    with Pool(processes=6) as pool: # or whatever your hardware can support

        # have your pool map the file names to dataframes
        df_list = pool.map(df_from_csv_no_geo, file_list)

        # reduce the list of dataframes to a single dataframe
        combined_df = pd.concat(df_list, ignore_index=True)
        
        return combined_df
    
    


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    print(type(project_dir))


    df = main(project_dir / 'data/raw/')
    print('Final df shape:', df.shape)

    df.to_csv(project_dir / 'birth__no_geo_test.csv', index=False)

