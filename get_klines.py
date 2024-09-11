### ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК ###

from pybit.unified_trading import HTTP
import pandas as pd
import getpass
import datetime
import numpy as np
import tqdm


#АПИ-КЛЮЧИ К ТОРГОВОМУ-АККАУНТУ BYBIT

a_k = ...
a_sk = ...


#ЗАГРУЗКА ДАННЫХ:  АПРЕЛЬ 2020 - ДЕКАБРЬ 2023
ts = [ i for i in range(1585699200, 1585699200 + 1440*30*45*60 , 60 * 1000)]

total_quotes = []

for t in ts :
    
    try :
        

        session = HTTP(
        testnet=False,
        api_key=a_k,
        api_secret=a_sk
        
        )
        
        # ПРИ API-ЗАПРОСЕ к BYBIT CУЩЕСТВУЕТ ЛИМИТ В 1000 СВЕЧЕЙ, ПОЭТОМУ КАЖДЫЙ РАЗ ПАРСИМ ПО 1000 СВЕЧЕЙ и ДОБАВЛЯЕМ К ОБЩЕМУ ДАТАФРЕЙМУ
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
#КАК ТОЛЬКО "ПРОШЛИСЬ" ПО ДИАПАЗОНУ ДАТ И ДОБАВИЛИ ВСЕ СВЕЧИ, СКАЧИВАЕМ ГОТОВЫЙ ДАТАФРЕЙМ    
