'''
Created on Dec 3, 2014

@author: mike
'''

import datetime as dt
import pandas as pd
import numpy as np
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import csv
import matplotlib.pyplot as plt

def convert_orders_csv_to_dataframe(np_orders):
    l_datetime = []
    closing_prices = []
    for row in np_orders:
        print 'DEBUG: ' + str(row[0])
        date_tokens = row[0].split('/')
        print 'DEBUG: ' + str(date_tokens) 
        year = int('20' + date_tokens[2])
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        price = float(row[1])
            
        # Create datetimeindex
        dt = pd.datetime(year, month, day, 16, 0, 0)
        l_datetime.append(dt)
        
        # Price
        closing_prices.append(price)
        
    datetimeindex = pd.DatetimeIndex(l_datetime)
    
    df_prices = pd.DataFrame({'price': closing_prices},index=datetimeindex)
    
    return df_prices


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

def ema(period, np_prices):
    l_emas = []
    time = period
    for i in range(0,int(time) - 1):
        l_emas.append(float('NaN'))
    
    # Set 12th day to MA
    first_ema = np.average(np_prices[0:(int(time) - 2),0])
    l_emas.append(first_ema)
    
    print 'DEBUG: l_emas first = ' + str(l_emas)
    
    # Compute succeeding emas
    alpha_one = 2.0 / (time + 1.0)
    alpha_two = 1.0 - (2.0/(time + 1.0))
    i = int(time)
    for price in np_prices[time:,0]:
        ema = (price * alpha_one) + (l_emas[i - 1] * alpha_two)
        
        print 'price: ' + str(price)
        print 'alpha_one: ' + str(alpha_one)
        print 'ema_yest: ' + str(l_emas[i - 1])
        print 'alpha_two: ' + str(alpha_two)
        print 'ema: ' + str(ema)
        print '==============='
        
        l_emas.append(ema)
        i = i + 1
    
    return l_emas

def main():
    # Get closing price
    msft_price_file = open('msft_2013.csv', 'rU')
    reader = csv.reader(msft_price_file, delimiter=',')
    np_price = []
    for row in reader:
        np_price.append(row)
    print 'DEBUG: Before ' + str(np_price)
    np_price = np.delete(np_price, 0, 0)
    print 'DEBUG: After ' + str(np_price)
    
    df_price = convert_orders_csv_to_dataframe(np_price) 
    df_price.sort_index(inplace=True)    
    
    # Get 12-day average
    np_prices = df_price.values
    #print 'np_prices:' + str(np_prices)
    
    #print '12 days prices: ' + str(np_prices[0:11,0])
    #print 'first_ema: ' + str(first_ema)
    '''
    l_emas = []
    # Set day 1 to 11 to NAN
    time = 26.0
    for i in range(0,int(time) - 1):
        l_emas.append(float('NaN'))
    
    # Set 12th day to MA
    first_ema = np.average(np_prices[0:(int(time) - 2),0])
    l_emas.append(first_ema)
    
    print 'DEBUG: l_emas first = ' + str(l_emas)
    
    # Compute succeeding emas
    alpha_one = 2.0 / (time + 1.0)
    alpha_two = 1.0 - (2.0/(time + 1.0))
    i = int(time)
    for price in np_prices[time:,0]:
        ema = (price * alpha_one) + (l_emas[i - 1] * alpha_two)
        
        #print 'price: ' + str(price)
        #print 'alpha_one: ' + str(alpha_one)
        #print 'ema_yest: ' + str(l_emas[i - 1])
        #print 'alpha_two: ' + str(alpha_two)
        #print 'ema: ' + str(ema)
        #print '==============='
        
        l_emas.append(ema)
        i = i + 1
    '''
    l_emas_12 = ema(12, np_prices)
    l_emas_26 = ema(26, np_prices)
    dt_index = df_price.index
    #print 'DEBUG: dt_index.length = ' + str(len(dt_index))
    #print 'DEBUG: l_emas.length = ' + str(len(l_emas))
    df_ema_12 = pd.DataFrame({'prices':np_prices[:,0],\
                           'ema':l_emas_12},\
                          index=dt_index)
    df_ema_26 = pd.DataFrame({'prices':np_prices[:,0],\
                           'ema':l_emas_26},\
                          index=dt_index)
    print '12 ' + str(df_ema_12)
    print '26 ' + str(df_ema_26)
    
    np_ema_12 = df_ema_12.values
    np_ema_26 = df_ema_26.values
    
    plt.clf()
    plt.plot(dt_index, np_prices)
    plt.plot(dt_index, np_ema_12)
    plt.plot(dt_index, np_ema_26)
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.savefig('ema_msft_2013.pdf', format='pdf')
        
if __name__ == '__main__':
    main()