import pandas as pd
import numpy as np

def create_df():
    # key name
    df = pd.read_excel('data/HC.xlsx', 
                   sheet_name=None)

    keys = list(df.keys())
    df3 = pd.DataFrame(columns=['seq', '成分', 'price', 'source'])
    
    for k in keys:
        cur = pd.read_excel('data/HC.xlsx', sheet_name=k)
        cur['source'] =  k
        cur = cur[['编号','成分','成品价', 'source']].rename(columns={'编号': 'seq', '成品价': 'price'})
        cur['price'] =np.round(cur['price'] * 1.2 / 7.6, 3)
        df3 = pd.concat([df3, cur], axis = 0)
        
    df3.to_csv('data/price.csv', index=None)
        
        
if __name__ == '__main__':
    create_df()