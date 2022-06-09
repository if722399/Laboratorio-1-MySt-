# Importar Librerias
import pandas as pd
import json 

# Opening JSON file
f = open('orderbooks_05jul21.json')
print(f)

# Returns JSON object as a dictionary
orderbooks_data = json.load(f)
ob_data = orderbooks_data['bitfinex']

# Drop Keys with none values
ob_data = {i_key: i_value for i_key,i_value in ob_data.items() if i_value is not None}

# Convert to DataFrame and rearange columns
ob_data = {i_ob: pd.DataFrame(ob_data[i_ob])[['bid_size', 'bid', 'ask', 'ask_size']]
          if ob_data[i_ob] is not None else None for i_ob in list(ob_data.keys())}

