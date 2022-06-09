import dataa as dt
import numpy as np
import pandas as pd
import scipy.stats.stats as st
data_ob = dt.ob_data

class metrics:

    def order_book_metrics(data_ob):
        # -- Median Time of OrderBook update -- #
        ob_ts = list(data_ob.keys())
        l_ts = [pd.to_datetime(i_ts) for i_ts in ob_ts] # Modificar todos los valores de str a unidades de tiempo
        ob_m1 = np.mean([l_ts[n_ts+1] - l_ts[n_ts] for n_ts in range(len(l_ts)-1)]).total_seconds()

        # -- Spread -- #
        ob_m2 = [data_ob[ob_ts[i]]['ask'][0] - data_ob[ob_ts[i]]['bid'][0] for i in range(len(ob_ts))]

        # -- Midprice -- #
        ob_m3 = [(data_ob[ob_ts[i]]['ask'][0] + data_ob[ob_ts[i]]['bid'][0])/2 for i in range(len(ob_ts))]

        # -- Number of price levels -- #
        ob_m4 = [data_ob[i_ts].shape[0] for i_ts in ob_ts]

        # -- Bid Volume -- #
        ob_m5 = [np.round(data_ob[i_ts]['bid_size'].sum(), 6) for i_ts in ob_ts]

        # -- Ask Volume -- #
        ob_m6 = [np.round(data_ob[i_ts]['ask_size'].sum(), 6) for i_ts in ob_ts]

        # -- Total Volume -- #
        ob_m7 = [ob_m5[i] + ob_m6[i] for i in range(len(ob_ts))]

        # -- Order book imbalance -- #
        # v[0] Bid Volume  // v[1] Ask Volume
        obimb = lambda v,d : np.sum(v[0][:d]) / np.sum([v[0][:d], v[1][:d]])
        v = [[data_ob[ob_ts[i]].iloc[0:,0].values,data_ob[ob_ts[i]].iloc[0:,3].values] for i in range(len(ob_ts))]
        ob_m8 = [obimb(v[i],25) for i in range(len(ob_ts))]

        # Comprobación:
        #o1 = data_ob[ob_ts[-1]] 
        #np.sum(o1.iloc[0:,0]) / (np.sum(o1.iloc[0:,0]) + np.sum(o1.iloc[0:,3])), ob_m8[-1] # Imbalance del primer orderbook

        # -- Weighted-Midprice (A)
        ob_m9 = np.array(ob_m3)*(ob_m8) # MidPrice * OrderBook Imbalance


        # -- Weighted-Midprice (B) (p: price, v: volume)
        w_midprice = lambda p,v : (v[1] /(v[0] + v[1])) * p[0] + (v[0] /(v[0] + v[1])) * p[1] 

        v2 = [[data_ob[ob_ts[i]].iloc[0,0],data_ob[ob_ts[i]].iloc[0,3]] for i in range(len(ob_ts))]
        p = [[data_ob[ob_ts[i]].iloc[0,1],data_ob[ob_ts[i]].iloc[0,2]] for i in range(len(ob_ts))]
        ob_m10 = [w_midprice(p[i],v2[i]) for i in range(len(ob_ts))]

        
        # -- VWAP (Volume-Weighted Average Price) (p: price, v: volume, d: depth)
        vwap = lambda p, v, d : np.sum(np.array(p[0][:d]) * np.array(v[0][:d]) + np.array(p[1][:d]) * np.array(v[1][:d])) / np.sum([v[0][:d], v[1][:d]])
        p2 = [[data_ob[ob_ts[i]].iloc[0:,1].values,data_ob[ob_ts[i]].iloc[0:,2].values] for i in range(len(ob_ts))]
        ob_m11 = [np.round(vwap(p2[i],v[i], 5),6) for i in range(len(ob_ts))]

        # -- OHLCV: Open, High, Low, Close, Volume (Quoted Volume) (Quoted Volume) -- # Hacerlo con resample y con el mid price
        df_ohlcv = pd.DataFrame(data = ob_m3, index = l_ts, columns = ['M_Price'])
        ob_12 = df_ohlcv.resample('60T').ohlc()
        df_ohlcv['Volume'] = ob_m7
        ob_12['Volume'] = df_ohlcv['Volume'].resample('60T').sum().values

        # -- Media, Varianza, Sesgo y Kurtosis del imbalance -- # (lista con los 4 calculos)
        ib_media = np.mean(ob_m8)
        ib_varianza = np.var(ob_m8)
        ib_sesgo = st.skew(ob_m8)
        ib_kurtosis = st.kurtosis(ob_m8)

        ob_m13 = [ib_media,ib_varianza,ib_sesgo,ib_kurtosis]

        final = {'Median_time_update':ob_m1,'Spread':ob_m2,'Mid_Price':ob_m3,'#_price_levels':ob_m4,'Bid_Volume':ob_m5,'Ask_Volume':ob_m6,
                'Total_Volume':ob_m7,'Order_book_imbalance':ob_m8,'Weighted-Midprice (A)':ob_m9,'Weighted-Midprice (B)':ob_m10,
                'VWAP':ob_m11,'OHLCV':ob_12,'Estadistica':ob_m13,}

        return final



    # --- Public Trades --- #
    def public_trades_metrics(pt_data):
        # -- Cantida de trades publicos que ocurren en 1 hora -- #
        #pt_data.drop('Unnamed: 0', inplace=True, axis = 1)
        pt_data.index = pd.to_datetime(pt_data['timestamp']) # Convertir de str a timestamp

        # -- (1) Buy Trade Count -- # 
        pt_m1 = (pt_data['side'][pt_data['side'] == 'buy']).resample('60T').count()

        # -- (2) Sell Trade Count -- # 
        pt_m2 = (pt_data['side'][pt_data['side'] == 'sell']).resample('60T').count()

        # -- (3) Total Trade Count -- # 
        pt_m3 = pt_m1 + pt_m2

        # -- (4) Difference in Total Trade Count -- # 
        pt_m4 = pt_m1 - pt_m2

        # -- (5) Sell Volume -- #
        pt_m5 = (pt_data['amount'][pt_data['side'] == 'buy']).resample('60T').sum()

        # -- (6) Buy Volume -- #
        pt_m6 = (pt_data['amount'][pt_data['side'] == 'sell']).resample('60T').sum()

        # -- (7) Total Volume -- #
        pt_m7 = pt_m5 + pt_m6

        # -- (8) Difference in volume -- 
        pt_m8 = pt_m5 - pt_m6

        # -- (9) Crear un dataframe con los precios OHLCV (pista utilizar resample y algo mas o menos tipo 'fill') -- # Cada Hora (funcin pd.ohlc) con trade price
        pt_m9 = pt_data['price'].resample('60T').ohlc()
        pt_m9['Volume'] = pt_m7

        # -- (10) TradeFlow Imbalance -- # Cada Hora (Suma con buy + y con sell -)
        pt_m10 = pt_m4

        # # Media, Varianza, Sesgo y Kurtosis del Difference in volume -- # (lista con los 4 calculos)

        pt_media = np.mean(pt_m8)
        pt_varianza = np.var(pt_m8)
        pt_sesgo = st.skew(pt_m8)
        pt_kurtosis = st.kurtosis(pt_m8)

        pt_m11 = [pt_media,pt_varianza,pt_sesgo,pt_kurtosis]

        final = {'Buy Trade':pt_m1,'Sell Trade':pt_m2,'Total Trade':pt_m3,'Difference in Total Trade':pt_m4,'Sell Volume':pt_m5,'Buy Volume':pt_m6,'Total Volume':pt_m7,
        'Difference in volume':pt_m8,'OHLCV':pt_m9,'TradeFlow Imbalance':pt_m10,'Estadistica':pt_m11}

        return final


# pt_data = pd.read_csv('btcusdt_binance.csv', header=0)
# public_trades(pt_data)
    

# order_book_metrics(data_ob)




