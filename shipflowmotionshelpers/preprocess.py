import pandas as pd


def remove_acceleration_part(df:pd.DataFrame, q=0.99, steady_ratio=10**-4)->pd.DataFrame:
    """Preprocess removing the initial acceleration part

    Parameters
    ----------
    df : pd.DataFrame
        Time series
    q : float
        quantile to decide most common speed
    steady_ratio : float
        Margin to steady speed where we consider we have reached it.

    Returns
    -------
    pd.DataFrame
        Cut time series.
    """
            
    interesting = ['phi','dX']   
    # Removing the initial acceleration part:
    dX_steady = df['dX'].quantile(q=q)
    X = df
    
    index = ((dX_steady-X['dX'])/dX_steady < steady_ratio).idxmax()
    mask = X.index > index
    X = X.loc[mask].copy()
    
    return X