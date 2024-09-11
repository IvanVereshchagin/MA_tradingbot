from pybit.unified_trading import HTTP
import pandas as pd
import getpass
import datetime
import numpy as np
import tqdm
import pybit
import asyncio 
import time
import math
from tapy import Indicators
from datetime import datetime


###НАСТРОЙКА ПАРАМЕТРОВ ТОРГОВОЙ СЕССИИ###

# spot - для спотовой торговли , linear - для деривативов (к примеру бессрочный фьючерс на биткойн - BTCUSDT)
CATEGORY = '...'

# наименование торгового инструмента (к примеру ETHUSDT)
SYMBOL = '...'

# 1 - для торговли на минутном таймфрейме , 5 - на пятиминутном , 15 - на пятнадцати минутном и т.д.
INTERVAL = 1

# Кол-во свечей , которые при каждом запросе к бирже по АПИ будут использовать для рассчёта скользяшек( указывать с запасом)
LIMIT = 50

# Длины скользящих средних (int)

MA_SLOW_LENGTH = ...
MA_FAST_LENGTH = ...

# Объём контракта
QUANTITY = 0.001

# Не изменять данных параметр. Показывает в каком типе сделки находится бот. ( 1 - Long , -1 Short , 0 - вне сделки )
MARKETPOSITION = 0 

# Если не получилось осуществить вход в сделку, бот будет пробовать снова NUM_REPEAT раз.
NUM_REPEAT = 5

# Указываем апи-ключи ByBit
a_k = ...
a_sk = ...



total_quotes = [ ] 

### ТОРГОВЫЙ РОБОТ ###
               
async def session_state(): 
    MARKETPOSITION = 0 
    while True :
        clock = math.trunc(time.time() ) 
        dt_object = datetime.utcfromtimestamp(clock)

        # В КОНЦЕ КАЖДОЙ МИНУТЫ НА 59 СЕКУНДЕ СОБИРАЕМ ИНФОРМАЦИЮ О СВЕЧАХ И АНАЛИЗИРУЕМ СТОИТ ЛИ ВХОДИТЬ В СДЕЛКУ
        if dt_object.minute % INTERVAL == INTERVAL - 1 and dt_object.second == 59:
            
            t1 = time.time()
            
            session = HTTP(
                    
                    api_key=a_k,
                    api_secret=a_sk,
                    recv_window= 50000

                    )

            current_time = math.trunc( time.time()  )
            end_time = (  current_time   ) * 1000 
            start_time = (  current_time - 60 * LIMIT * INTERVAL + 1  ) * 1000 

            q = session.get_kline(
            category= CATEGORY,
            symbol= SYMBOL,
            interval= INTERVAL,
            start= start_time , 
            
            end= end_time,
            limit = LIMIT 
            ).get('result').get('list')
            
            q = list(reversed(q))

            total_quotes.extend(q)


            last_quotes = pd.DataFrame(q)   

            last_quotes = last_quotes.rename( columns = { 0 : 'Timestamp', 1 : 'Open' , 2 : 'High' ,
                                                        3 : 'Low' , 4 : 'Close' , 5 : 'VolumeBTC', 6 : 'VolumeUSDT' })

            

            i= Indicators(last_quotes)
            i.sma(period=MA_FAST_LENGTH, column_name=f'sma{MA_FAST_LENGTH}', apply_to='Close')
            i.sma(period=MA_SLOW_LENGTH, column_name=f'sma{MA_SLOW_LENGTH}', apply_to='Close')
            last_quotes = i.df
            
            last_quotes[f'prev_sma{MA_SLOW_LENGTH}'] = last_quotes[f'sma{MA_SLOW_LENGTH}'].shift(1)
            last_quotes[f'prev_sma{MA_FAST_LENGTH}'] = last_quotes[f'sma{MA_FAST_LENGTH}'].shift(1)
            last_row = last_quotes.iloc[-1 , :]
            
            
            #LONG(BUY) SIGNAL
            if ( last_row[f'sma{MA_FAST_LENGTH}'] > last_row[f'sma{MA_SLOW_LENGTH}'] ) and  ( last_row[f'prev_sma{MA_FAST_LENGTH}'] < last_row[f'prev_sma{MA_SLOW_LENGTH}'] ) :
                
                #Если открыта шорт сделка до этого то закрываем ее 
                if MARKETPOSITION == -1 :
                    counter = 0 
                    while counter < NUM_REPEAT  :

                        

                        try :
                            buy_order = session.place_order(
                                category="linear",
                                symbol=SYMBOL,
                                side="Buy",
                                orderType="Market",
                                qty= QUANTITY ,
                                timeInForce="GTC"
                                )
                            

                        except pybit.exceptions.InvalidRequestError as e :
                            print(f'(REVERSE-ORDER)Failed to place BUY order. {counter+1}/{NUM_REPEAT} ')
                            сounter += 1 
                            await asyncio.sleep(1)

                        else :
                            print(f'(REVERSE-ORDER)Order is placed. BUY/{QUANTITY}')
                            counter = NUM_REPEAT
                            

                #Если противоположных сделок не открыто:
                
                    
                counter = 0 
                while counter < NUM_REPEAT  :

                        

                    try :
                        buy_order = session.place_order(
                                category="linear",
                                symbol=SYMBOL,
                                side="Buy",
                                orderType="Market",
                                qty= QUANTITY ,
                                timeInForce="GTC"
                                )
                            

                    except pybit.exceptions.InvalidRequestError as e :
                        print(f'Failed to place BUY order. {counter+1}/{NUM_REPEAT} ')
                        сounter += 1 
                        await asyncio.sleep(1)

                    else :
                        print(f'Order is placed. BUY/{QUANTITY}')
                        counter = NUM_REPEAT
                        MARKETPOSITION = 1
                            
                       
                        
                
                
                
                

            #SHORT(SELL) POSITION ENTER
            elif ( last_row[f'sma{MA_FAST_LENGTH}'] < last_row[f'sma{MA_SLOW_LENGTH}'] ) and  ( last_row[f'prev_sma{MA_FAST_LENGTH}'] > last_row[f'prev_sma{MA_SLOW_LENGTH}'] ) :
                # Если до этого открыта лонг сделка - закрываем её.
                if MARKETPOSITION == 1:
                    counter = 0 
                    while counter < NUM_REPEAT  :
                        try :
                            buy_order = session.place_order(
                                category="linear",
                                symbol=SYMBOL,
                                side="Sell",
                                orderType="Market",
                                qty= QUANTITY ,
                                timeInForce="GTC" 
                                 )
                            

                        except pybit.exceptions.InvalidRequestError as e :
                            print(f'Failed to place SELL order. {counter+1}/{NUM_REPEAT} ')
                            сounter += 1 

                        else :
                            print(f'Order is placed. SELL/{QUANTITY}')
                            counter = NUM_REPEAT
                            


                
                # Основной ордер на продажу.
                counter = 0 
                while counter < NUM_REPEAT  :
                    try :
                        buy_order = session.place_order(
                                category="linear",
                                symbol=SYMBOL,
                                side="Sell",
                                orderType="Market",
                                qty= QUANTITY ,
                                timeInForce="GTC" 
                                 )
                            

                    except pybit.exceptions.InvalidRequestError as e :
                        print(f'Failed to place SELL order. {counter+1}/{NUM_REPEAT} ')
                        сounter += 1 
                        await asyncio.sleep(1)

                    else :
                        print(f'Order is placed. SELL/{QUANTITY}')
                        counter = NUM_REPEAT
                        MARKETPOSITION = -1
                            
                            
            else :
                print('No conditions to place an order')


            t2 = time.time()
            print("The time of execution of above program is :",(t2-t1) * 10**3, "ms")
            
        

        await asyncio.sleep(1)

async def main():
    task1 = asyncio.create_task(session_state())
            
    await task1

asyncio.run(main())
     

