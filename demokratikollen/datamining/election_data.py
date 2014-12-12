import pandas as pd
import json

df = pd.read_excel('D:/data/demokratikollen/valresultat_kommun-parti_1978-2014_clean.xls',
                    index_col=None,na_values='..')

# Replace NaN in Kommun and Parti
df[['Kommun','Parti']] = df[['Kommun','Parti']].fillna(method='ffill')

# Remove name of Kommun (keep id)
df.loc[:,'Kommun'] = df.loc[:,'Kommun'].map(lambda x: x.split()[0])
munic_sums = df.groupby('Kommun').sum()

# Set index and sort
df.set_index(['Parti','Kommun'],inplace=True)
df.sortlevel(inplace=True)

json_dict = {y: {p: df[y].xs(p,level='Parti').to_dict() for p in df.index.levels[0]} for y in df.columns}

for y,dy in json_dict.items():
    for p,dp in dy.items():
        for k in dp.keys():
            dp[k] = dp[k]/munic_sums.loc[k,y]


with open('D:/data/demokratikollen/elections.json','w') as f:
    json.dump(json_dict,f)

# Bad format
# df.to_json('D:/data/demokratikollen/election.json')