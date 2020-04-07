#!/usr/bin/env python
# coding: utf-8



import requests
from datetime import datetime, timedelta
import pytz
from bybit import bybit
import time
from bitmex import bitmex
import json
import numpy as np
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
from sympy import symbols, Eq, solve




symbol = ['XBTUSD', 'BTCUSD']




keys = []
#add API Keys and Secrets for as many accounts as you need in the format shown below.
#Replace 'Manual', '1hr', etc. with whatever account name you want
keys.append(['Manual', [('XXX', 'XXX')]])
keys.append(['1hr', [('XXX', 'XXX')]])
keys.append(['2hr', [('XXX', 'XXX')]])
keys.append(['4hr', [('XXX', 'XXX')]])       
connections = []
for x in range(len(keys)):
    connections.append(bitmex(test=False,api_key=keys[x][1][0][0],api_secret=keys[x][1][0][1]))




def mex_rounding(value):
    rounded_value = round(value, 8)
    return rounded_value




def mex_balances():
    balances = []
    for x in range(len(connections)):
        balances.append((keys[x][0], connections[x].User.User_getWalletHistory().result()[0][0]['walletBalance']/100000000))
    return balances




total_mex_balance = 0
for x in range(len(mex_balances())):
    total_mex_balance+=mex_balances()[x][1]
total_mex_balance = round(total_mex_balance, 8)




def mex_positions():
    postions = []
    for x in range(len(connections)):
        if len(connections[x].Position.Position_get(filter=json.dumps({'symbol': symbol[0]})).result()[0]) != 0:
            if connections[x].Position.Position_get(filter=json.dumps({'symbol': symbol[0]})).result()[0][0]['currentQty'] != 0:
                current_bitmex = connections[x].Position.Position_get(filter=json.dumps({'symbol': symbol[0]})).result()[0][0]    
                mex = {}
                mex['Exchange'] = 'Bitmex'
                mex['Account'] = keys[x][0]
                if current_bitmex['currentQty'] < 0:
                    mex['Side'] = 'Short'
                elif current_bitmex['currentQty'] > 0:
                    mex['Side'] = 'Long'
                else:
                    mex['Side'] = 'None'
                if mex['Side'] == 'Short':
                    mex['Size'] = current_bitmex['currentQty']*-1
                else:
                    mex['Size'] = current_bitmex['currentQty']
                mex['ExecPrice'] = current_bitmex['avgEntryPrice']
                mex['OpenValue'] = mex_rounding(mex['Size']*((1/mex['ExecPrice'])-(1/mex['ExecPrice'])*0.00075))
                mex['MarketPrice'] = current_bitmex['markPrice']
                mex['MarketValue'] = mex_rounding(mex['Size']*((1/mex['MarketPrice'])-(1/mex['MarketPrice'])*0.00075))
                if mex['Side'] == 'Long':
                    mex['UnrealisedPnL'] = mex_rounding(mex['OpenValue'] - mex['MarketValue'])
                else:
                    mex['UnrealisedPnL'] = mex_rounding(mex['MarketValue'] - mex['OpenValue'])
                postions.append(mex)
    return postions




for x in range(len(mex_positions())):
    for k, v in mex_positions()[x].items():
        print(k, ':', v)
    print('\n')




custom_input = input('Add Custom Data? y/n'+'\n'+'>')
if custom_input == 'y':
    import_file = input('Import Data From custom_data.txt? y/n'+'\n'+'>')
    if import_file == 'n':
        custom = {}
        custom['Exchange'] = input('Exchange: ')
        custom['Account'] = input('Account: ')
        custom['Side'] = input('Side: ')
        custom['Size'] = int(input('Size: '))
        custom['ExecPrice'] = float(input('ExecPrice: '))
    else:
        import ast
        with open('custom_data.txt', 'r') as inf:
            custom = ast.literal_eval(inf.read())
        custom['Size'] = int(custom['Size'])
        custom['ExecPrice'] = float(custom['ExecPrice'])
    custom['OpenValue'] = mex_rounding(custom['Size']*((1/custom['ExecPrice'])-(1/custom['ExecPrice'])*0.00075))
    custom['MarketPrice'] = mex_positions()[0]['MarketPrice']
    custom['MarketValue'] = mex_rounding(custom['Size']*((1/custom['MarketPrice'])-(1/custom['MarketPrice'])*0.00075))
    if custom['Side'] == 'Long':
        custom['UnrealisedPnL'] = mex_rounding(custom['OpenValue'] - custom['MarketValue'])
    else:
        custom['UnrealisedPnL'] = mex_rounding(custom['MarketValue'] - custom['OpenValue'])
    print('\n')

    for k, v in custom.items():
        print(k, ':', v)
    print('\n')




net_longs = []
net_shorts = []
for x in range(len(mex_positions())):
    if mex_positions()[x]['Side'] == 'Long':
        net_longs.append([mex_positions()[x]['Size'], mex_positions()[x]['ExecPrice'], mex_positions()[x]['UnrealisedPnL']])
    else:
        net_shorts.append([mex_positions()[x]['Size'], mex_positions()[x]['ExecPrice'], mex_positions()[x]['UnrealisedPnL']])




if custom['Side'] == 'Long':
    net_longs.append([custom['Size'], custom['ExecPrice'], custom['UnrealisedPnL']])
else:
    net_shorts.append([custom['Size'], custom['ExecPrice'], custom['UnrealisedPnL']])




keys = []
#add API Keys and Secrets for as many accounts as you need in the format shown below.
#Replace '1hr', '2hr', etc. with whatever account name you want
keys.append(['1hr', [('XXX', 'XXX')]])
keys.append(['2hr', [('XXX', 'XXX')]])
keys.append(['4hr', [('XXX', 'XXX')]])
connections = []
for x in range(len(keys)):
    connections.append(bybit(test=False,api_key=keys[x][1][0][0],api_secret=keys[x][1][0][1]))




def bybit_rounding(value):
    rounded_value = round(float(value), 8)
    return rounded_value




def bybit_balances():
    balances = []
    for x in range(len(connections)):
        balances.append((keys[x][0], bybit_rounding(connections[x].Wallet.Wallet_getBalance(coin='BTC').result()[0]['result']['BTC']['available_balance'])))
    return balances




def bybit_positions():
    positions = []
    for x in range(len(connections)):
        if connections[x].Positions.Positions_myPositionV2(symbol=symbol[1]).result()[0]['result']['side'] != 'None':
            current_bybit = connections[x].Positions.Positions_myPositionV2(symbol=symbol[1]).result()[0]['result']    
            market_price = float(next(item for item in connections[x].Market.Market_symbolInfo().result()[0]['result'] if item["symbol"] == symbol[1])['mark_price'])
            bit = {}
            bit['Exchange'] = 'Bybit'
            bit['Account'] = keys[x][0]
            if current_bybit['side'] == 'Sell':
                bit['Side'] = 'Short'
            elif current_bybit['side'] == 'Buy':
                bit['Side'] = 'Long'
            bit['Size'] = int(current_bybit['size'])
            bit['ExecPrice'] = round(float(current_bybit['entry_price']), 2)
            bit['OpenValue'] = bybit_rounding(bit['Size']*(1/bit['ExecPrice'] - (1/bit['ExecPrice']*0.00075)))
            bit['MarketPrice'] = market_price
            bit['MarketValue'] = bybit_rounding(bit['Size']*((1/bit['MarketPrice']) - (1/bit['MarketPrice'])*0.00075))
            if bit['Side'] == 'Long':
                bit['UnrealisedPnL'] = bybit_rounding(bit['OpenValue'] - bit['MarketValue'])
            else:
                bit['UnrealisedPnL'] = bybit_rounding(bit['MarketValue'] - bit['OpenValue'])
            positions.append(bit)
    return positions




for x in range(len(bybit_positions())):
    for k, v in bybit_positions()[x].items():
        print(k, ':', v)
    print('\n')




total_bybit_balance = 0
for x in range(len(bybit_balances())):
    total_bybit_balance+=bybit_balances()[x][1]
total_bybit_balance = round(total_bybit_balance, 8)




for x in range(len(bybit_positions())):
    if bybit_positions()[x]['Side'] == 'Long':
        net_longs.append([bybit_positions()[x]['Size'], bybit_positions()[x]['ExecPrice'], bybit_positions()[x]['UnrealisedPnL']])
    else:
        net_shorts.append([bybit_positions()[x]['Size'], bybit_positions()[x]['ExecPrice'], bybit_positions()[x]['UnrealisedPnL']])




total_longs = 0
total_shorts = 0
if len(net_longs) == 1:
    sizes = []
    entries = []
    uPnL = []
    sizes.append(net_longs[0][0])
    entries.append(net_longs[0][1])
    uPnL.append(net_longs[0][2])
    total_longs = sum(sizes)
    long_avg_entry = round(np.average(entries, weights=sizes), 2)
    long_open_value = round(sum(sizes)*((1/long_avg_entry)- ((1/long_avg_entry)*0.00075)), 8)
    long_upnl = round(sum(uPnL), 8)
    print('LongSize: '+str(total_longs)+'\n'+
         'LongEntry: '+str(long_avg_entry)+'\n'+
         'LongOpenValue: '+str(long_open_value)+'\n'+
         'LongUpNl: '+str(long_upnl)+'\n')
elif len(net_longs) > 1:
    sizes = []
    entries = []
    uPnL = []
    for x in range(len(net_longs)):
        sizes.append(net_longs[x][0])
        entries.append(net_longs[x][1])
        uPnL.append(net_longs[x][2])
    total_longs = sum(sizes)
    long_avg_entry = round(np.average(entries, weights=sizes), 2)
    long_open_value = round(sum(sizes)*((1/long_avg_entry)- ((1/long_avg_entry)*0.00075)), 8)
    long_upnl = round(sum(uPnL), 8)
    print('LongSize: '+str(total_longs)+'\n'+
         'LongEntry: '+str(long_avg_entry)+'\n'+
         'LongOpenValue: '+str(long_open_value)+'\n'+
         'LongUpNl: '+str(long_upnl)+'\n')

if len(net_shorts) == 1:
    sizes = []
    entries = []
    uPnL = []
    sizes.append(net_shorts[0][0])
    entries.append(net_shorts[0][1])
    uPnL.append(net_shorts[0][2])
    total_shorts = sum(sizes)
    short_avg_entry = round(np.average(entries, weights=sizes), 2)
    short_open_value = round(sum(sizes)*((1/short_avg_entry)- ((1/short_avg_entry)*0.00075)), 8)
    short_upnl = round(sum(uPnL), 8)
    print('ShortSize: '+str(total_shorts)+'\n'+
         'ShortEntry: '+str(short_avg_entry)+'\n'+
         'ShortOpenValue: '+str(short_open_value)+'\n'+
         'ShortUpNl: '+str(short_upnl)+'\n')
    
elif len(net_shorts) > 1:
    sizes = []
    entries = []
    uPnL = []
    for x in range(len(net_shorts)):
        sizes.append(net_shorts[x][0])
        entries.append(net_shorts[x][1])
        uPnL.append(net_shorts[x][2])
    total_shorts = sum(sizes)
    short_avg_entry = round(np.average(entries, weights=sizes), 2)
    short_open_value = round(sum(sizes)*((1/short_avg_entry)- ((1/short_avg_entry)*0.00075)), 8)
    short_upnl = round(sum(uPnL), 8)
    print('ShortSize: '+str(total_shorts)+'\n'+
         'ShortEntry: '+str(short_avg_entry)+'\n'+
         'ShortOpenValue: '+str(short_open_value)+'\n'+
         'ShortUpNl: '+str(short_upnl)+'\n')

if len(net_shorts) > 0 and len(net_longs) > 0:
    print('CurrentUpNl: '+ str(round(short_upnl+long_upnl, 8)))
elif len(net_shorts) > 0 and len(net_longs) == 0:
    print('CurrentUpNl: '+ str(short_upnl))
elif len(net_shorts) == 0 and len(net_longs) > 0:
    print('CurrentUpNl: '+ str(long_upnl))

if total_longs > total_shorts and total_shorts != 0:
    net_position_size = total_longs-total_shorts
    net_open_value = round(long_open_value-short_open_value, 8)
    netBias = 'Long'
elif total_shorts > total_longs and total_longs != 0:
    net_position_size = total_shorts-total_longs
    net_open_value = round(short_open_value-long_open_value, 8)
    netBias = 'Short'
elif total_shorts == 0 and total_longs > 1:
    net_position_size = total_longs
    net_open_value = long_open_value
    netBias = 'Long'
elif total_longs == 0 and total_shorts > 1:
    net_position_size = total_shorts
    net_open_value = short_open_value
    netBias = 'Short'

net_entry = round(net_position_size/net_open_value, 2)
target = net_entry
if total_shorts > 0:
    short_close_value = round((total_shorts*((1/target)-((1/target)*0.00075)))-short_open_value, 8)
if total_longs > 0:
    long_close_value = round(long_open_value - (total_longs*((1/target)-((1/target)*0.00075))), 8)

x = symbols('x')
if total_longs > total_shorts and total_shorts != 0:
    eq1 = Eq((long_open_value - (total_longs*((1/x)-((1/x)*0.00075)))) + ((total_shorts*((1/target)-((1/target)*0.00075)))-short_open_value))
    breakeven = round(solve(eq1)[0], 2)
elif total_shorts > total_longs and total_longs != 0: 
    eq1 = Eq((long_open_value - (total_longs*((1/x)-((1/x)*0.00075)))) + ((total_shorts*((1/target)-((1/target)*0.00075)))-short_open_value))
    breakeven = round(solve(eq1)[0], 2)
elif total_shorts == 0 and total_longs > 1:
    eq1 = Eq((total_longs*((1/x)-((1/x)*0.00075)))-((long_open_value-(long_open_value*0.00075))))
    breakeven = round(solve(eq1)[0], 2)
elif total_longs == 0 and total_shorts > 1:
    eq1 = Eq((total_shorts*((1/x)-((1/x)*0.00075)))-((short_open_value-(short_open_value*0.00075))))
    breakeven = round(solve(eq1)[0], 2)

print('\n'+'NetBias: '+netBias+'\n'+
'NetPositionSize: '+str(net_position_size)+'\n'+
'NetBreakEven: '+str(breakeven))
