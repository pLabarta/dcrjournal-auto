from decred.dcr.dcrdata import DcrdataClient

from datetime import datetime

import json, time, sys, requests
import pandas as pd
import numpy as np

client = DcrdataClient('https://explorer.dcrdata.org')

# You can enter any block before the month you want to analyze
# The date crop will take care of it (:

# Enter starting and last block or just use the best one
block_start = 419000
# last_block = 420500
last_block = client.block.best.height()

# YYYY-MM-DD HH:MM:SS format to crop the DataFrame
start_date = '2020-02-01 00:00:00'
end_date = '2020-03-01 00:00:00'


## UTILS

def ts_to_date(ts):
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return date

def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def split_range(start,stop):
    if (stop - start) > 1000:
        print('Splitting range into several requests...')
        print('This will take a while to avoid stressing the Block Explorer')
        range_list = []
        current = start
        while current < stop:
            if (stop - current) > 999:
                range_list.append((current,current+999))
                current = current+1000
                print(f'added ({current},{current+999}) to the list')
            else:
                range_list.append((current,stop))
                current = stop
        return range_list
    else:
        print('Requesting range in one request! Nice little block range!')
        range_list = [(start,stop)]
        return range_list

## GET BLOCK RANGE AND RETURN PANDAS DF

## This could be get using an endpoint similar to TX COUNT https://explorer.dcrdata.org/api/chart/block-size?bin=block

def get_block_size_df(idx0, idx):
    range_list = split_range(idx0,idx)
    df = pd.DataFrame()
    for each in range_list:
        print(f'Getting blocks {each}')
        block_list = client.block.range(each[0],each[1])
        sub_df = pd.DataFrame()
        sub_df['height'] = np.array([block['height'] for block in block_list])
        sub_df['size'] = np.array([block['size'] for block in block_list])
        sub_df['date'] = np.array([ts_to_date(block['time']) for block in block_list])
        df = df.append(sub_df,ignore_index=True)
        time.sleep(1)
    return df

## TX COUNT AND SIZE CHART END POINT

api = 'https://explorer.dcrdata.org/api'
def dcrdata_req(req):
    response = requests.get(api+req).json()
    return response

def get_all_day_tx_count(blocks_dataframe):
    raw_count = dcrdata_req('/chart/tx-count?bin=day')
    dates = blocks_dataframe['date']
    dates = dates.apply(lambda x: x.replace(hour=0,minute=0,second=0))
    df = pd.DataFrame()
    df['count'] = np.array([count for count in raw_count['count']])
    df['date'] = [pd.Timestamp(t,unit='s') for t in raw_count['t']]
    this_mask = (df['date'] >= dates.min()) & (df['date'] <= dates.max())
    df = df.loc[this_mask]
    return df

## MAIN FUNC

if __name__ == '__main__':
    df = get_block_size_df(block_start, last_block)
    # print('Before the mask')
    # print(df)

    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] > start_date) & (df['date'] < end_date)
    df = df.loc[mask]
    # print('After the mask')
    # print(df)

    tx_count_df = get_all_day_tx_count(df)
    # print(tx_count_df['count'])

    monthly_tx_count_sum = tx_count_df['count'].sum()
    monthly_tx_count_mean = tx_count_df['count'].mean()
    monthly_tx_count_min = tx_count_df['count'].min()
    monthly_tx_count_max = tx_count_df['count'].max()

    monthly_block_size_mean = df['size'].mean()
    monthly_block_size_sum = df['size'].sum()
    monthly_block_size_max = df['size'].max()
    monthly_block_size_min = df['size'].min()

    print(f'This month, the blockchain size grew {GetHumanReadable(monthly_block_size_sum,precision=2)}. Blocks had an average size of {GetHumanReadable(monthly_block_size_mean,precision=2)}. The smallest block had a size of {GetHumanReadable(monthly_block_size_min,precision=2)} and the largest one, {GetHumanReadable(monthly_block_size_max,precision=2)}.')

    print(f'{monthly_tx_count_sum} transactions were included in the blockchain. On average, there were {int(monthly_tx_count_mean)} per day. The busiest day saw {monthly_tx_count_max} TXs and the least one {monthly_tx_count_min} TXs.')


    # DATAFRAME TO CSV    
    tx_count_df.to_csv('daily_tx_count.csv')
    df.to_csv('block_size.csv')

# This month, the blockchain size grew 112.98MB. Blocks had an average size of 13.92KB. The smallest block had a size of 1.36KB and the largest one 366.37KB.
# 132323 transactions were included in the blockchain. On average, there were 4562 transactions per day. The busiest day saw 5175 TXs and the least one 3709.

## TODO
# IDEAL USAGE   "python3 getTransactionsText.py year month(english) "
