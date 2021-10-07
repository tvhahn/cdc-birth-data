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
    year = int(str(file_path).split('/')[-1][4:8])
    
    if year > 2004 or year < 1982:
        pass
    
    else:
        
        # load FIPS code data
        df_fips = pd.read_csv(file_path.parent.parent / 'external' / 'all-geocodes-v2017.csv', dtype=str)


        # get the fips codes for the states only
        df_fips = df_fips[(df_fips['County Code (FIPS)']=='000') & 
                                (df_fips['County Subdivision Code (FIPS)']=='00000') & 
                                (df_fips['Place Code (FIPS)']=='00000') & 
                                (df_fips['Consolidtated City Code (FIPS)']=='00000')
                               ][['State Code (FIPS)','Area Name (including legal/statistical area description)']]

        # rename columns in df
        df_fips.columns = ['state_fips', 'state_name_mr']
        
        # require differnt column names depending on year
        # columns for 2003+
        col_load_1 = ['dob_yy','dob_mm','dob_wk','mrstate','mrcntyfips','mrcityfips',]

        # columns for 1989-2002
        col_load_2 =['biryr', 'birmon', 'weekday', 'stresfip', 'cntyrfip', 'cityres']
        rename_col2 = ['dob_yy','dob_mm','dob_wk','mrstate','mrcntyfips','mrcityfips',]
        
        # columns for 1982 through 1988
        col_load_3 =['datayear', 'birmon','birday','stresfip', 'cntyrfip', 'cityres']
        rename_col3 = ['dob_yy','dob_mm','dob_day','mrstate','mrcntyfips','mrcityfips',]

        # create dictionary to rename older csvs
        col_rename_dict2 = dict(zip(col_load_2, rename_col2))
        col_rename_dict3 = dict(zip(col_load_3, rename_col3))

        # if the CSVs are of newer format
        if year >= 2003:  
            # load abbreviation csv so we can rename AK to Alaska, etc.
            df_abbr = pd.read_csv(file_path.parent.parent / 'external' / 'state_abbreviations.csv',header=None, names=['state','abbr'])

            # load only select columns, and set dtype for columns
            df = pd.read_csv(file_path, nrows=nrows, usecols=col_load_1, dtype=str)

            # get the full state name and append them onto the df
            df = pd.merge(df, df_abbr, left_on='mrstate',right_on='abbr', how='inner', copy=False).drop(['abbr'], axis=1).drop(['mrstate'], axis=1)
            df = df.rename(columns={'state':'state_name_mr'})
            
            # get state FIPS code and append
            df = pd.merge(df, df_fips, left_on='state_name_mr',right_on='state_name_mr', how='inner', copy=False)
            df = df.rename(columns={'state_fips':'mrstatefips'})

            # drop any rows with NaN's
            df = df.dropna()

        # if the CSVs are of older format
        else:

            
            if year >= 1989:
                col_load, col_rename_dict = col_load_2, col_rename_dict2
            else:
                col_load, col_rename_dict = col_load_3, col_rename_dict3

            # load only select columns from the birth CSV
            df = pd.read_csv(file_path, nrows=nrows, usecols=col_load, dtype=str).rename(columns=col_rename_dict)

            # rename 'mrstate' column 
            df = df.rename(columns={'mrstate':'mrstatefips'})

            # merge the df_stat_fips to get the full state name
            df = pd.merge(df, df_fips, left_on='mrstatefips',
                  right_on='state_fips', how='inner', copy=False).drop(['state_fips'], axis=1)
            
            # years before 1989 only show a single digit (i.e. 2 for 1982)
            if year < 1989:
                df = df.drop(columns=['dob_yy'])
                df['dob_yy'] = np.array([year]*df.shape[0])

            # drop any rows with NaN's
            df = df.dropna()
    

        # return the dataframe, and order the columns in a fixed manner
        return df[['dob_yy', 'dob_mm',
                   'mrcntyfips', 'mrcityfips', 'state_name_mr', 'mrstatefips']].astype({'dob_mm':int, 'dob_yy':int})
