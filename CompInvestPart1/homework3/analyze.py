'''
Created on Oct 29, 2014

@author: mike dayacap
'''

import sys
import csv
import datetime as dt
import math as m

import numpy as np
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
from __builtin__ import str

'''
    Logging for debugging
'''
def log_debug(msg):
    print "[DEBUG] " + msg

'''
    Get actual price of symbol
'''
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
        
    na_data = np.array(df_data.loc[:, symbols[0]])
    
    return na_data

'''
    Calculate Cumulative Return of two sets
'''
def calc_cum_ret(na_data1, na_data2):
    #Compute first set
    na_cum_ret1 = na_data1 / na_data1[0]
    na_cum_ret2 = na_data2 / na_data2[1]
    
    return na_cum_ret1, na_cum_ret2

def calc_fund_daily_ret(na_fund_cum_ret):
    
    na_fund_daily_ret = []
    na_fund_daily_ret.append(0);
    
    for i in range(1, len(na_fund_cum_ret)):
        fund_daily_ret = (na_fund_cum_ret[i]/na_fund_cum_ret[i - 1]) - 1
        na_fund_daily_ret.append(fund_daily_ret)
        
    return na_fund_daily_ret

def sharpe_ratio(ave_daily_ret, stdev_daily_ret):
    sharpe = (m.sqrt(250) * ave_daily_ret) / stdev_daily_ret
    return sharpe

'''
    Benchmark portfolio
'''
def analyze(values_csv_path, benchmark_symbol):
    values_csv = open(values_csv_path, 'r')
    values_reader = csv.reader(values_csv, delimiter=',')
    
    #Create value numpy array and get dates sorted
    a_values = []
    l_date = []
    for row in values_reader:
        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        val = float(row[3])
        
        #Get date
        date = dt.datetime(year, month, day)
        l_date.append(date)

        #Store value
        a_values.append(val)
    
    na_values = np.array(a_values)
    l_date.sort()
    
    #Get start and end date
    dt_start = l_date[0]
    dt_end = l_date[len(l_date) - 1] + dt.timedelta(days=1)
    
    #Get closing prices for benchmark
    na_spx = get_actual_price(dt_start, dt_end, [benchmark_symbol])
    
    #Calculate the cumulative return
    na_val_cum_ret, na_spx_cum_ret = calc_cum_ret(na_values, na_spx)
    
    #Calculate fund daily return
    na_val_fund_daily_ret = calc_fund_daily_ret(na_val_cum_ret)
    na_spx_fund_daily_ret = calc_fund_daily_ret(na_spx_cum_ret)
    
    #Calculate total return fund
    values_tot_ret = na_val_cum_ret[na_val_cum_ret.shape[0] - 1]
    spx_tot_ret = na_spx_cum_ret[na_spx_cum_ret.shape[0] - 1]
    
    #Standard Deviation
    values_std = np.std(na_val_fund_daily_ret)
    spx_std = np.std(na_spx_fund_daily_ret)
    
    #Average daily return
    val_avg_daily_ret = np.average(na_val_fund_daily_ret)
    spx_avg_daily_ret = np.average(na_spx_fund_daily_ret)
    
    #Calc sharpe ratio
    val_sr = sharpe_ratio(val_avg_daily_ret, values_std)
    spx_sr = sharpe_ratio(spx_avg_daily_ret, spx_std)
    
    print "Details of the Performance of the portfolio :"
    print '\n'
    print "Data Range : " + str(dt_start) + " to " + str(dt_end)
    print '\n'
    print "Sharpe Ratio Fund: " + str(val_sr)
    print "Sharpe Ratio SPX: " + str(spx_sr)
    print '\n'
    print "Total Return of Fund :  " + str(values_tot_ret)
    print "Total Return of $SPX : " + str(spx_tot_ret)
    print '\n'
    print "Std Dev of Fund: " + str(values_std)
    print "Std Dev of $SPX: " + str(spx_std)
    print '\n'
    print "Avg Daily Return Fund: " + str(val_avg_daily_ret)
    print "Avg Daily Return $SPX: " + str(spx_avg_daily_ret)
    
    
     
        
'''
    Main method
'''
if __name__ == "__main__":
    values_csv_path = sys.argv[1]
    benchmark = sys.argv[2]
    
    analyze(values_csv_path, benchmark)
    
         
    
    