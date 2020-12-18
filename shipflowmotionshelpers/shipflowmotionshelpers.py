"""Main module."""

import pandas as pd
import numpy as np
import re
import os
from shipflowmotionshelpers import errors

def _load_time_series(file_path:str)->pd.DataFrame:
    """Load time series from ShipFlowMotions into a pandas data frame

    Parameters
    ----------
    file_path : str
        Where is the motions file?

    Returns
    -------
    pd.DataFrame
        Pandas data frame with time as index
    """
    _,ext = os.path.splitext(file_path)
    if ext == '.csv':
        return _load_motions_csv(file_path=file_path)
    elif ext == '.ts':
        return _load_motions_old(file_path=file_path)
    else:
        raise ValueError('Unknown time series file extension:%s' % ext)

def _load_motions_old(file_path:str):
    """
    Load time series data from ShipFlow Motions file (old format).
    """
    
    df = pd.read_csv(file_path, sep=' +', index_col=1)
    df['phi'] = np.deg2rad(df['P4'])
    df['dX'] = df['V1']  # Speed in global X-direction
    return df

def _load_motions_csv(file_path:str):
    """
    Load time series data from ShipFlow Motions file.
    """
    
    df = pd.read_csv(file_path, sep=',', index_col=1)
    df['phi'] = np.deg2rad(df['P4'])
    df['dX'] = df['V1']  # Speed in global X-direction
    df['ts'] = df['Time_step']
    #print(df['ts'])
    return df

def _extract_parameters(s:str)->dict:
    """
    The functions parses all parameters from a ShipFlow Motions indata file.
    The function searches for:
    x = ...
    and saves all those occurences as a key value pair in a dict.
    
    Parameters
    ----------
    s : str
        Motions indata file content as string.
    
    Returns
    ----------
    parameters : dict
    
    """
    # matching: x = ....
    key_value_pairs = re.findall(pattern='(\w+) *= *"*([^ ^, ^" ^ ^\n ^)]+)', string=s)
    
    # matching x (jadadajada...)  : ....
    key_value_pairs_2 = re.findall(pattern='(\w+) *\([^\)]+\) *: *([^\n]+)', string=s)

    # adding the key_value_pairs_2 to the list:
    key_value_pairs+=key_value_pairs_2  # (This list may contain duplicates so that certain value are overwritten below)

    parameters = {}
    for key_value_pair in key_value_pairs:
        key = key_value_pair[0]
        value = key_value_pair[1]
        
        try:
            value=float(value)
        except:
            pass
        else:
            if value%1 == 0:  # if no decimals...
                value=int(value)
            pass
        
        parameters[key]=value
    
    return parameters

def extract_parameters_from_file(file_path:str)->pd.Series:
    """
    The functions parses all parameters from a ShipFlow Motions indata file.
    The function searches for:
    x = ...
    and saves all those occurences as a key value pair in a dict.
    
    Parameters
    ----------
    file_path : str
        path to Motions indata file
    
    Returns
    ----------
    parameters : dict
    
    """
    
    with open(file_path, mode='r') as file:
        s = file.read()
    
    ## Remove commented lines:
    s_without_commented_lines = re.sub(pattern='\/.*\n', repl='', string=s)
    
    parameters = _extract_parameters(s=s_without_commented_lines)
    
    s_parameters = pd.Series(data=parameters, name=file_path)
    
    return s_parameters

def load_parameters(file_path:str)->pd.DataFrame:
    """Load input file, output file and time series from a ShipFlow Motions simulation

    The files should follow the following nameing convention:
    input file name: {file_path}
    output file name: {file_path}_OUTPUT
    output time series: {file_path}_TS.csv or {file_path}.ts
    
    Parameters
    ----------
    file_path : str
        file path to the input file name (the other files are assumed to follow the naming convention above)
        Note! This can also be a list of paths
        
    Returns
    ----------
    parameters : pd.DataFrame
        All parameters from input file(s) and output file(s)
        
    """
    if isinstance(file_path,str):
        file_paths=[file_path]
    else:
        file_paths = file_path

    df_parameters = pd.DataFrame()

    for file_path in file_paths:
        parameters = _load_parameters(file_path=file_path)
        df_parameters =  df_parameters.append(parameters)

    return df_parameters

def _load_parameters(file_path:str)->pd.DataFrame:
    """Load input file, output file and time series from a ShipFlow Motions simulation

    The files should follow the following nameing convention:
    input file name: {file_path}
    output file name: {file_path}_OUTPUT
    output time series: {file_path}_TS.csv or {file_path}.ts
    
    Parameters
    ----------
    file_path : str
        file path to the input file name (the other files are assumed to follow the naming convention above)

    Returns
    ----------
    parameters : pd.DataFrame
        All parameters from input file(s) and output file(s)
        
    """

    ## Input parameter file:
    file_path_indata = file_path
    parameters_in = extract_parameters_from_file(file_path = file_path_indata)
    
    ## Output parameter file:
    file_path_output = '%s_OUTPUT' % file_path
    parameters_out = extract_parameters_from_file(file_path = file_path_output)
    
    ## Joining Input and Output parameters:
    data = dict(parameters_in)
    data.update(dict(parameters_out))  # overwriting duplicates
    _,name = os.path.split(file_path)
    
    parameters = pd.Series(data =data, name=name)

    parameters['file_path_ts'] = os.path.abspath('%s_TS.csv' % file_path)
    
    return parameters

def load_time_series(df_parameters:pd.DataFrame):
    """Load all time series associated with the file sin the df_parameters.
    
    Parameters
    ----------
    df_parameters : pd.DataFrame
        Data fram with input and output parameters and with the column "file_path_ts" so that the time series can be found
    """

    if not 'file_path_ts' in df_parameters:
        raise errors.TimeSeriesFilePathError('df_parameters must contain the column "file_path_ts"')

    time_series = {}    
    for name, parameters in df_parameters.iterrows():
        file_path = parameters['file_path_ts']
        time_series[name] = _load_time_series(file_path=file_path)

    return time_series
