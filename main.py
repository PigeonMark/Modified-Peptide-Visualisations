import os.path
import pickle

import numpy as np

from src.data import read_file, parse_modifications, merge_duplicates, filter_rows, export
from src.util import add_length, split

if __name__ == "__main__":
    datafile = 'data/iRT_unimod_unfiltered.csv'
    use_cache = True
    cache_file = os.path.join('cache', '.'.join(datafile.replace('/', '-').split('.')[:-1]) + '.p')
    if use_cache and os.path.exists(cache_file):
        df, mod_id_to_name_dict = pickle.load(open(cache_file, 'rb'))
    else:
        df = read_file('data/iRT_unimod_unfiltered.csv')
        df, mod_id_to_name_dict = parse_modifications(df, 'modified_sequence')
        df = add_length(df)
        pickle.dump((df, mod_id_to_name_dict), open(cache_file, 'wb'))

    df['quality'] = np.random.randint(30, 100, df.shape[0])

    # TODO: Check same modification in different format will result in the same representation for duplicate removal
    # TODO: remove duplicates before or after Proforma parsing? This is much slower on Proforma data but different
    # representations of same modification will be considered different
    df = merge_duplicates(df, how='median', col='modified_sequence', to_merge=['iRT', 'length'])

    df = filter_rows(df, 'gt', 'quality', 40)
    # export(df, 'data/iRT_unimod_filtered', cols=['modified_sequence', 'iRT', 'length', 'quality'])
    mod_df_dict = split(df, 'mods', mod_id_to_name_dict, single_mod_only=True, keep_same_unmodified_sequence=True)
    for mod, m_df in mod_df_dict.items():
        print(mod_id_to_name_dict[mod])
        mod_df, unmod_df = split(m_df, 'mod_unmod')
        print(mod_df)
        print(unmod_df)

    dfs = split(df, 'col', col_name='length')
    print(dfs)
