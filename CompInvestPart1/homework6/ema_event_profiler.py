'''
Created on Dec 16, 2014

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
            and f_bollinger_val_spy >= 1.3:
                ts = ldt_timestamps[i]
                df_events[s_sym].ix[ts] = 1
    
    return df_events


def ema(ls_symbols, d_data, period):
    df_prices = d_data['actual_close']
    np_close = df_prices.values
    
    np_ema = copy.deepcopy(np_close)
    np_ema = np_ema * np.NAN

    int_period = int(period)    
    np_first_ema = np.average(np_close[0:(int_period - 2),:], axis=0)
    
    np_ema[int_period - 1, :] = np_first_ema

    alpha_one = 2.0 / (period + 1.0)
    alpha_two = 1.0 - (2.0/(period + 1.0))
    i = int_period
    for close in np_close[period:,:]:
        np_ema_temp = (close * alpha_one) + (np_ema[i - 1,:] * alpha_two)
        np_ema[i,:] = np_ema_temp
        i = i + 1
        
    df_ema = pd.DataFrame({ls_symbols[0]:np_ema[:,0]}, index=df_prices.index)
    for i in range(1, len(ls_symbols)):
        df_ema[ls_symbols[i]] = np_ema[:,i]

    print 'DEBUG: df_ema \n' + str(df_ema)
    
    return df_ema

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
    
    df_ema_12 = ema(ls_symbols, d_data, 12)
    df_ema_26 = ema(ls_symbols, d_data, 26)

    #df_events = find_events(ls_symbols, df_ema)
    #print "Creating Study"
    #ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
    #           s_filename='HW6_sp5002012_bollingerbands.pdf', b_market_neutral=True, b_errorbars=True,
    #            s_market_sym='SPY')
