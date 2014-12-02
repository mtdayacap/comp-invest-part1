'''
Created on Oct 9, 2014

@author: mike
'''
import sys
import csv
import datetime as dt

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import pandas as pd

''' Global Vars '''
DEBUG = False

def log_debug(msg):
    print "[DEBUG] " + msg

def get_date_range_and_symbols(reader):
    date_list = []
    symbol_list = []
    i = 0
    for row in reader:
        ''' Get date '''
        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        
        date = dt.datetime(year, month, day, 16, 0, 0)
        date_list.append(date)

        #'''Get symbol'''
        symbol = row[3]
        symbol_list.append(symbol)
                
        i = i + 0
    
    #''' Make sure the lists contains unique values '''
    u_symbol_list = list(set(symbol_list))
    
    date_list.sort()
    
    return date_list, u_symbol_list    

def get_actual_price(dt_start, dt_end, symbols):
    dt_timeofday = dt.timedelta(hours=16)

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    c_dataobj = da.DataAccess('Yahoo')

    ls_keys = ['close']

    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    
    df_data = ldf_data[0]   # This is a list of dataframes.
                            # Since we only got 'close' prices then
                            # then we only got one entry in the list.
                            # You may get the dateframe by getting
                            # the first element in the list.
    
    for symbol in symbols:
        df_data[symbol].fillna(method='ffill')
        df_data[symbol].fillna(method='bfill')
        df_data[symbol].fillna(1.0)

    return df_data, ldt_timestamps

'''
Convert orders csv to data frame
'''
def convert_orders_csv_to_dataframe(np_orders):
    l_datetime = []
    symbols = []
    orders = []
    shares = []
    for order_row in np_orders:
        year = int(order_row[0])
        month = int(order_row[1])
        day = int(order_row[2])
        symbol = order_row[3]
        order = order_row[4]
        share = order_row[5]
        
        # Create datetimeindex
        dt = pd.datetime(year, month, day, 16, 0, 0)
        l_datetime.append(dt)
        
        symbols.append(symbol)
        orders.append(order)
        shares.append(share)
        
    datetimeindex = pd.DatetimeIndex(l_datetime)
    
    df_orders = pd.DataFrame({'symbol': symbols, 'order': orders, 'share':shares},index=datetimeindex)
    
    return df_orders

'''
    Method tester
'''
def test_method():
    orders_file = open(orders_filepath, 'rU')
    
    reader = csv.reader(orders_file, delimiter=',')
    
    np_orders = []  #Orders CSV
    for row in reader:
        np_orders.append(row)
    
'''
    Method that describes the market simulation
    @param f_cash: Cash investment
    @param orders_filepath: Relative file path of orders csv
    @param values_filename: filename of output file
'''
def sim(f_cash, orders_filepath, values_filename):
    orders_file = open(orders_filepath, 'rU')
    
    reader = csv.reader(orders_file, delimiter=',')
    
    np_orders = []  #Orders CSV
    for row in reader:
        np_orders.append(row)
    
    # Get adjusted closing prices
    date_list, symbols = get_date_range_and_symbols(np_orders)
    
    dt_start = date_list[0] #Start Date
    dt_end = date_list[len(date_list) - 1] + dt.timedelta(days=1)  #End Date
    
    #GOAL 1: Get Adjusted Closing Prices
    df_closing_prices, ldt_timestamps = get_actual_price(dt_start, dt_end, symbols)
    
    #GOAL 2: Get DateTimeIndex list from list of Timestamps
    l_datetime = []
    for ts in ldt_timestamps:
        l_datetime.append(ts.to_datetime())
    
    datetimindex_daily = pd.DatetimeIndex(l_datetime);
    
    #GOAL 3: Convert order.csv to DataFrame
    df_orders = convert_orders_csv_to_dataframe(np_orders)
    
    #log_debug("df_orders: " + str(type(df_orders.values)))
    #log_debug("df_closing_price: " + str(df_closing_prices))
    
    #GOAL 4: Compute daily portfolio value
    ownership = {"AAPL":0, "IBM":0, "GOOG":0, "XOM":0}
    cash = f_cash
    values_csv = open(values_filename, 'w')
    for dti in datetimindex_daily:
        # Get year, month, day
        year = dti.year
        month = dti.month
        day = dti.day
        
        # Check for market orders and update ownerhsip
        
        if(any(df_orders.index == dti)):
            
            market_orders = df_orders.ix[dti].values
            
            if(len(market_orders) == 3):
                order = market_orders[0]
                shares = int(market_orders[1])
                symbol = market_orders[2]
                
                curr_ownership = ownership[symbol]

                sym_closing_price = df_closing_prices.loc[dti, symbol]
                if(order == 'Buy'):
                    curr_ownership =  curr_ownership + shares
                    cash = cash - (shares * sym_closing_price)
                else:
                    curr_ownership = curr_ownership - shares
                    cash = cash + (shares * sym_closing_price)
                    
                ownership[symbol] = curr_ownership
            
            else:
                for ord in market_orders:
                    symbol = ord[2]
                    order = ord[0]
                    shares = int(ord[1])
                    
                    curr_ownership = ownership[symbol]
                    
                    sym_closing_price = df_closing_prices.loc[dti, symbol]
                    if(order == 'Buy'):
                        curr_ownership =  curr_ownership + shares
                        cash = cash - (shares * sym_closing_price)
                    else:
                        curr_ownership = curr_ownership - shares
                        cash = cash + (shares * sym_closing_price)
                        
                    ownership[symbol] = curr_ownership
        
        # Compute daily value
        daily_val = cash
        for s in symbols:
            sym_shares = ownership[s]
            sym_closing_price = df_closing_prices.loc[dti, s]
            daily_val = (sym_shares * sym_closing_price) + daily_val
        
        log_debug(str(year)+","+str(month)+","+str(day)+","+str(daily_val))
        values_csv.write(str(year)+","+str(month)+","+str(day)+","+str(daily_val)+'\n')
            
''' 
   Main method 
'''
if __name__ == '__main__':
    global DEBUG_LOG 
    
    f_cash = float(sys.argv[1])
    orders_filepath = sys.argv[2]
    output_filename = sys.argv[3]
    DEBUG_LOG = bool(sys.argv[4] == '1')
    
    if(DEBUG_LOG):
        log_debug("Cash: " + str(f_cash))
        log_debug("Orders Filename: " + str(orders_filepath))
        log_debug("Values Filename: " + str(output_filename))
    
    sim(f_cash, orders_filepath, output_filename)
