# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

# Third party Imports
import datetime as dt
import numpy as np
import math as m

def get_closing_price(dt_start, dt_end, ls_symbols):
	# We need closing prices so the timestamp should be hours=16.
	dt_timeofday = dt.timedelta(hours=16)

	# Get a list of trading days between the start and end
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
	c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
	ls_keys = ['close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	na_price = d_data['close'].values

	return na_price

'''
Calculate Cumulative Return from closing prices

@param na_price: Numpy array of closing prices
'''
def calc_cum_ret(na_price):
	na_rets = na_price / na_price[0, :]
	return na_rets

def calc_invest(cum_rets, alloc):
	cum_ret_port = cum_rets * alloc
	return cum_ret_port

def calc_fund_invest(cum_ret_port):
	fund_invest = []
	for i in range(0, cum_ret_port.shape[0]):
		fund_invest.append(sum(cum_ret_port[i,:]))
	return fund_invest

def calc_fund_cum_ret(na_fund_invest):
	na_fund_cum_re = na_fund_invest / na_fund_invest[0]
	return na_fund_cum_re

def calc_fund_daily_ret(na_fund_cum_ret):
	
	na_fund_daily_ret = []
	na_fund_daily_ret.append(0);
	
	for i in range(1, len(na_fund_cum_ret)):
		fund_daily_ret = (na_fund_cum_ret[i]/na_fund_cum_ret[i - 1]) - 1
		na_fund_daily_ret.append(fund_daily_ret)
		
	return na_fund_daily_ret

def calc_average_daily_ret(fund_daily_ret):
	return np.average(fund_daily_ret)

def calc_fund_daily_cum_ret(fund_cum_ret):
	fund_daily_cum_ret = []
	# Initialize list
	fund_daily_cum_ret.append(1)
	for i in range(0,len(fund_cum_ret) - 1):
		fund_daily_cum_ret.append(fund_cum_ret[i]*fund_daily_cum_ret[i])
	return fund_daily_cum_ret

def calc_annual_ret(na_fund_invest):
	return (na_fund_invest[len(na_fund_invest) - 1] - na_fund_invest[0]) / na_fund_invest[0] 

def sharpe_ratio(ave_daily_ret, stdev_daily_ret):
	sharpe = (m.sqrt(250) * ave_daily_ret) / stdev_daily_ret
	return sharpe

def increment_allocation(allocations, inc):
	
	reachedMax = False
	
	if len(allocations) != 4:
		print 'Allocations should be equal to 4'
		reachedMax = True
		return [allocations, reachedMax]
	
	if allocations[0] == 1.0 and allocations[1] == 1.0 and allocations[2] == 1.0 and allocations[3] == 1.0:
		print 'Reached maximum allocation scenario'
		reachedMax = True
		return [allocations, reachedMax]
	
	notEqualToOne = True
	while notEqualToOne == True:
		if allocations[3] == 1.0:
			if allocations[2] == 1.0:
				if allocations[1] == 1.0:
					if allocations[0] == 1.0:
						pass
					else:
						allocations[0] = round((allocations[0] + inc), 1)
						allocations[1] = 0.0
						allocations[2] = 0.0
						allocations[3] = 0.0
				else:
					allocations[1] = round((allocations[1] + inc), 1)
					allocations[2] = 0.0
					allocations[3] = 0.0
			else:
				allocations[2] = round((allocations[2] + inc), 1)
				allocations[3] = 0.0	
		else:
			allocations[3] = round((allocations[3] + inc), 1)
		
		total = allocations[0] + allocations[1] + allocations[2] + allocations[3]
		if total == 1.0:
			notEqualToOne = False
		elif allocations[0] == 1.0 and allocations[1] == 1.0 and allocations[2] == 1.0 and allocations[3] == 1.0:
			reachedMax = True
			notEqualToOne = False
			allocations = [0.0,0.0,0.0,0.0]
			#print 'DEBUG - allocations: ' + str(allocations)
	
#	if allocations[0] == 1.0 and allocations[1] == 1.0 and allocations[2] == 1.0 and allocations[3] == 1.0:
#		allocations = [0.0, 0.0, 0.0, 0.0]

#	print 'DEBUG - allocations: ' + str(allocations)
	return [allocations, reachedMax]

def simulate(dt_start, dt_end, ls_symbols, alloc):
	na_price = get_closing_price(dt_start,dt_end,ls_symbols)
	na_cum_ret = calc_cum_ret(na_price)
	na_invest = calc_invest(na_cum_ret, alloc)
	na_fund_invest = calc_fund_invest(na_invest)
	na_fund_cum_ret = calc_fund_cum_ret(na_fund_invest)
	na_fund_daily_ret = calc_fund_daily_ret(na_fund_cum_ret)
	
	#Result
	annual_ret = calc_annual_ret(na_fund_invest)
	avg_daily_ret = calc_average_daily_ret(na_fund_daily_ret)
	std_daily_return = np.std(na_fund_daily_ret)
	sharpe = sharpe_ratio(avg_daily_ret, std_daily_return)
	
	return [na_fund_cum_ret[len(na_fund_cum_ret) - 1], avg_daily_ret, std_daily_return, sharpe]
	
	
#######################################
# MAIN
#######################################
def main():
	dt_start = dt.datetime(2011,1,1)
	dt_end = dt.datetime(2011,12,31)

	ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
	
	inc = 0.1
	allocations = [0.0, 0.0, 0.0, 0.0]
	best_sharpe = 0
	best_allocation = allocations
	reachedMax = False
	while reachedMax == False:
		[allocations, reachedMax] = increment_allocation(allocations, inc)
		[annual_ret, avg_daily_ret, std_daily_return, sharpe] = simulate(dt_start, dt_end, ls_symbols, allocations)
		if best_sharpe < sharpe:
			best_sharpe = sharpe
			best_allocation = allocations[:]
	
	print 'Best Allocation'
	print str(best_allocation)
	print str(best_sharpe)

def optimize_port(start_date, end_date, ls_symbols):
	
	dt_start = dt.datetime(start_date[0],start_date[1],start_date[2])
	dt_end = dt.datetime(end_date[0],end_date[1],end_date[2])
	
	inc = 0.1
	allocations = [0.0, 0.0, 0.0, 0.0]
	best_sharpe = 0
	best_allocation = allocations
	reachedMax = False
	while reachedMax == False:
		[allocations, reachedMax] = increment_allocation(allocations, inc)
		[annual_ret, avg_daily_ret, std_daily_return, sharpe] = simulate(dt_start, dt_end, ls_symbols, allocations)
		if best_sharpe < sharpe:
			best_sharpe = sharpe
			best_allocation = allocations[:]
	
	print 'Best Allocation'
	print str(best_allocation)
	print str(best_sharpe)
	
	

def test_simulate():
#	dt_start = dt.datetime(2011,1,1)
#	dt_end = dt.datetime(2011,12,31)
#	ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
#	allocations = [0.4,0.4,0.0,0.2]

	dt_start = dt.datetime(2010,1,1)
	dt_end = dt.datetime(2010,12,31)
	ls_symbols = ["AXP", "HPQ", "IBM", "HNZ"]
	allocations = [0.0,0.0,0.0,1.0]


	[cum_ret, avg_daily_ret, std_daily_return, sharpe] = simulate(dt_start, dt_end, ls_symbols, allocations)
	print 'Sharpe Ratio: ' + str(sharpe)
	print 'Volatility (stdev of daily returns): ' + str(std_daily_return)
	print 'Average Daily Return: ' + str(avg_daily_ret)
	print 'Cumulative Return: ' + str(cum_ret)

def test_generate_allocs():
	allocations = [0.0,0.0,0.0,0.0]
	inc = 0.1
	
#	[allocations, reachedMax] = increment_allocation(allocations, inc)
#	print str(allocations)
	
	reachedMax = False
	while reachedMax == False:
		[allocations,reachedMax] = increment_allocation(allocations, inc)
		print str(allocations)
	
	

def save_adj_closing_price(symbol, file):
	dt_start = dt.datetime(2011,1,1)
	dt_end = dt.datetime(2011,12,31)
	
	na_price = get_closing_price(dt_start, dt_end, [symbol])
	
	for i in range(0, len(na_price) - 1):
		file.write(str(na_price[i,0]) + "\n")
	
	file.close()