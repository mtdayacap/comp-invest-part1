'''
Created on Nov 29, 2014

@author: mike
'''
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import pandas as pd
import matplotlib.pyplot as plt


def get_actual_price(dt_start, dt_end, symbols):
    dt_timeofday = dt.timedelta(hours=16)

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    c_dataobj = da.DataAccess('Yahoo')

    ls_keys = ['close']

    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    
    df_data = ldf_data[0]
    
    for symbol in symbols:
        df_data[symbol].fillna(method='ffill')
        df_data[symbol].fillna(method='bfill')
        df_data[symbol].fillna(1.0)

    return df_data, ldt_timestamps


def main():
    # Get GOOGLE's closing prices
    df_closing_prices, ldt_timestamps = get_actual_price(dt.datetime(2010,1,1), dt.datetime(2010,12,31), ['MSFT'])
    
    #print "df_closing_prices"
    #print str(df_closing_prices) 
    
    #
    rolling_mean = pd.rolling_mean(df_closing_prices, 20)
    rolling_std = pd.rolling_std(df_closing_prices, 20)
    #print 'rolling_mean type: ' + str(type(rolling_mean))
    #print 'rolling_std: ' + str(rolling_std)
    
    
    np_closing_prices = df_closing_prices.values
    np_std = rolling_std.values
    np_mean = rolling_mean.values
    #print 'np_mean: ' + str(np_std)
    np_upper_band = np_mean + np_std
    np_lower_band = np_mean - np_std
    #print 'np_upper_band: ' + str(np_upper_band)
    #print 'np_lower_band: ' + str(np_lower_band)
    
    #print "closing_prices length: " + str(len(np_closing_prices[20:(len(np_closing_prices) - 1)]))
    #print "np_upper_band length: " + str(len(np_upper_band))
    
    bollinger_val = (np_closing_prices - np_mean) / (np_std)
    #print "bollinger_val: " + str(pd.DataFrame(bollinger_val, index=ldt_timestamps))
    df_bollinger = pd.DataFrame(bollinger_val, index=ldt_timestamps)
    for i in range(0,len(ldt_timestamps)-1):
        ts = ldt_timestamps[i]
        print str(ts) + " " + str(df_bollinger[0].ix[ts])
    
    plt.clf()
    plt.plot(ldt_timestamps, np_closing_prices)
    plt.plot(ldt_timestamps, np_mean)
    plt.plot(ldt_timestamps, np_upper_band)
    plt.plot(ldt_timestamps, np_lower_band)
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.savefig('boolingerbands.pdf', format='pdf')
    
if __name__ == '__main__':
    main()