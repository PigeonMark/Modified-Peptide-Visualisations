import os
import pickle

from src.data import parse_modifications, read_file, merge_duplicates
from src.splitted_plots import plot_mod_unmod_split, plot_col_split
from src.util import add_length, split


def mod_unmod_example():
    df, mod_id_to_name_dict = read_and_cache('data/iRT_unimod_unfiltered.csv')
    df = merge_duplicates(df, how='median', col='modified_sequence', to_merge=['iRT', 'length'])
    mod_df_dict = split(df, 'mods', mod_id_to_name_dict, single_mod_only=True, keep_same_unmodified_sequence=True)
    mod_df_dict = {mod_id_to_name_dict[k]: v for k, v in mod_df_dict.items()}

    mod_df_dict = {k: mod_df_dict[k] for k in ['Methyl', 'hydroxyisobutyryl', 'Succinyl']}
    plot_mod_unmod_split(mod_df_dict, subsample=100, mod_dict_col='mod_dict', col_wrap=3, height=5,
                         save_file='plots/mod_unmod_example.png')


def length_charge_example():
    df, mod_id_to_name_dict = read_and_cache('data/CCS_unimod.csv')

    len_df_dict = split(df, 'col', col_name='length')
    len_df_dict = {k: len_df_dict[k] for k in [15, 20, 25]}
    plot_col_split(len_df_dict, plot_col='CCS', subsample=100, split1_name='length', col_name='Charge', col_wrap=3,
                   height=5, save_file='plots/length_charge_example.png')


def mod_charge_example(single_mod_only):
    df, mod_id_to_name_dict = read_and_cache('data/CCS_unimod.csv')

    mod_df_dict = split(df, 'mods', mod_id_to_name_dict, single_mod_only=single_mod_only, keep_same_unmodified_sequence=False)
    mod_df_dict = {mod_id_to_name_dict[k]: v for k, v in mod_df_dict.items()}
    plot_col_split(mod_df_dict, plot_col='CCS', subsample=100, split1_name='modification', col_name='Charge',
                   col_wrap=3,
                   height=5, save_file=f'plots/mod_charge_example{"_single_mod" if single_mod_only else "_multi_mod"}.png')


def read_and_cache(datafile):
    use_cache = True
    cache_file = os.path.join('cache', '.'.join(datafile.replace('/', '-').split('.')[:-1]) + '.p')
    if use_cache and os.path.exists(cache_file):
        df, mod_id_to_name_dict = pickle.load(open(cache_file, 'rb'))
    else:
        df = read_file(datafile)
        df, mod_id_to_name_dict = parse_modifications(df, 'modified_sequence')
        df = add_length(df)
        pickle.dump((df, mod_id_to_name_dict), open(cache_file, 'wb'))
    return df, mod_id_to_name_dict


if __name__ == "__main__":
    # mod_unmod_example()
    # length_charge_example()
    mod_charge_example(True)
    mod_charge_example(False)

