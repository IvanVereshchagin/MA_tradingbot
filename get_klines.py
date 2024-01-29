from pybit.unified_trading import HTTP
import pandas as pd
import getpass
import datetime
import numpy as np
import tqdm
#Скрипт для получения минутных данных с криптобиржи bybit для бэктестинга и анализа.

# API_KEYS
#АПИ-КЛЮЧИ К АККАУНТУ

a_k = "..."
a_sk = "..."

# DOWNLOADING DATA FROM APRIL 2020 TILL DECEMBER 2023
#СКАЧИВАЕМ ДАННЫЕ С АПРЕЛЯ 2020 по ДЕКАБРЬ 2023
ts = [ i for i in range(1585699200, 1585699200 + 1440*30*45*60 , 60 * 1000)]

total_quotes = []

for t in ts :
    
    try :
        

        session = HTTP(
        testnet=False,
        api_key=a_k,
        api_secret=a_sk
        
        )
        #WE FETCH EVERY 1000 KLINES (limit) and FULLFILL THE TOTAL DATAFRAME WITH IT.
        # При апи запросе существует лимит - 1000 свечей/ запрос. 
        q = session.get_kline(
        category="linear",
        symbol="BTCUSDT",
        interval=1,
        start=t * 1000,
        
        end= (t + 60*1000 + 1  ) * 1000,
        limit = 1000
        ).get('result').get('list')
        
        q = list(reversed(q))
        

        total_quotes.extend(q)


        print(len(total_quotes))
        print('Data is catched , current candle`s datetime is ' , t)
        

        
    
    except:
        print(('Failed to connect' , t))
        break




    

else :
    #DOWNLOAD DATA
    #Скачиваем итоговый датафрейм
    df = pd.DataFrame(total_quotes)
    df.to_csv('bybit_data.csv' , index = False )

    
