import yaml
import os
import pandas as pd

from ff14_utils import get_current_data, get_target_worlds

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    config = load_config('config.yaml')['metadata']

    root_dir = os.getcwd()
    data_dir = os.path.join(root_dir, 'data')

    df = pd.read_csv(os.path.join(data_dir, 'Items_v3.csv'), header=0)
    all_items = df['#'].to_list()
    target_items = all_items

    target_worlds = get_target_worlds(config['data_center'])

    seconds_in_a_day = 60 * 60 * 24
    milliseconds_in_a_day = seconds_in_a_day * 1000

    target_keys = config['target_keys']

    fields_str = ','.join([f'items.{key}' for key in target_keys])

    df_items = pd.DataFrame(columns=target_keys, dtype=float)

    for world in target_worlds:
        # separate the list of items into chunks of 100
        chunks = [target_items[x : x + 100] for x in range(0, len(target_items), 100)]
        for chunk in chunks:
            data = get_current_data(world[0], chunk, 0, '', 7 * milliseconds_in_a_day, fields_str)['items']
            df_temp = pd.DataFrame({key: [data[item][key] for item in data.keys()] for key in target_keys})
            df_items = pd.concat([df_items, df_temp])
            #time.sleep(0.05)

    df_items = df_items.reset_index(drop=True)

    df_items['itemID'] = df_items['itemID'].astype(int)
    df_items['nqSaleVelocity'] = df_items['nqSaleVelocity'].astype(int)
    df_items['hqSaleVelocity'] = df_items['hqSaleVelocity'].astype(int)
    df_items['lastUploadTime'] = pd.to_datetime(df_items['lastUploadTime'], unit='ms')

    df_items.to_csv(os.path.join(data_dir, 'item_metadata.csv'), index=False)

    print('Metadata updated.')