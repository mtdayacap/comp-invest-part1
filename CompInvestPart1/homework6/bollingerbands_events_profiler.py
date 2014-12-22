'''
Created on Dec 14, 2014

@author: mike
'''

import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
import copy
import numpy as np
import pandas as pd

def find_events(ls_symbols, df_bollinger_val):
    ''' Finding the event dataframe '''
    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger_val)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_bollinger_val.index

    for s_sym in ls_symbols:
        if(s_sym == 'SPY'):
            continue
        
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_bollinger_val_today = df_bollinger_val[s_sym].ix[ldt_timestamps[i]]
            f_bollinger_val_yest = df_bollinger_val[s_sym].ix[ldt_timestamps[i - 1]]
            f_bollinger_val_spy = df_bollinger_val['SPY'].ix[ldt_timestamps[i]]
            
            if f_bollinger_val_today < -2.0\
            and f_bollinger_val_yest >= -2.0\
            and f_bollinger_val_spy >= 1.5:
                ts = ldt_timestamps[i]
                df_events[s_sym].ix[ts] = 1
    
    return df_events

def calculate_bollinger_bands(ls_symbols, d_data):
    df_close = d_data['actual_close']
    
    print 'Calculate Bollinger Bands'
    df_rolling_mean = pd.rolling_mean(df_close, 20)
    df_rolling_std = pd.rolling_std(df_close, 20)
    
    np_mean = df_rolling_mean.values
    np_std = df_rolling_std.values
    np_closing_prices = df_close.values
    
    np_bollinger_val = (np_closing_prices - np_mean) / np_std
    
    # Store the bollinger values to a dataframe
    df_bollinger_vals = pd.DataFrame({ls_symbols[0]:np_bollinger_val[:,0]}, index=df_close.index)
    for i in range(1, len(ls_symbols)):
        df_bollinger_vals[ls_symbols[i]] = np_bollinger_val[:,i]
    
    return df_bollinger_vals
    
if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    

    df_bollinger_val = calculate_bollinger_bands(ls_symbols, d_data)    
    df_events = find_events(ls_symbols, df_bollinger_val)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='HW6_sp5002012_bollingerbands.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
