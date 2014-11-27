'''dt
Created on Oct 1, 2014

@author: mike
'''
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    event_counter = 0
    l_datetime = []
    symbols = []
    orders = []
    shares = []
    last_day = ldt_timestamps[len(ldt_timestamps) - 1]
    print "last_day: " + str(last_day)
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            if f_symprice_today < 9.0 and f_symprice_yest >= 9.0:
                ts = ldt_timestamps[i]
                
                df_events[s_sym].ix[ts] = 1
                event_counter = event_counter + 1
                
                #Build orders
                l_datetime.append(ts.to_datetime())
                symbols.append(s_sym)
                orders.append('Buy')
                shares.append(100)
                
                #After 5 days sell the shares
                next_5_days = du.getNextNNYSEdays(ts, 6, dt.timedelta(hours=16))
                fifth_day = next_5_days[len(next_5_days) - 1]
                if(fifth_day <= last_day.to_datetime()):
                    l_datetime.append(fifth_day)
                else:
                    l_datetime.append(last_day.to_datetime())
                symbols.append(s_sym)
                orders.append('Sell')
                shares.append(100)
    
    #datetimeindex = pd.DatetimeIndex(l_datetime)            
    #df_orders = pd.DataFrame({'symbol':s_sym,'order':orders,'shares':shares},index=datetimeindex)

    orders_file = open('orders.csv', 'w')
    i = 0
    for datetime in l_datetime:
        year = datetime.year
        month = datetime.month
        day = datetime.day
        symbol = symbols[i]
        order = orders[i]
        num_of_shares = shares[i]
        
        orders_file.write(str(year) + ',' + str(month) + ',' + str(day) + ',' + str(symbol) + ',' + str(order) + ',' + str(num_of_shares) + '\n')
        
        i = i + 1


    return df_events
    
    print 'Number of events: ' + str(event_counter)
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

    df_events = find_events(ls_symbols, d_data)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='HW2_sp5002012.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
