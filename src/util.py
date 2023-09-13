import pandas as pd


def add_length(df, len_col='length', unmod_seq_col='unmodified_sequence'):
    df[len_col] = df[unmod_seq_col].str.len()
    return df


def split_mod_unmod(df, mod_dict_col='mod_dict'):
    num_mods = df[mod_dict_col].str.len()
    return {'mod': df[num_mods > 0], 'unmod': df[num_mods == 0]}


def split_col(df, col_name):
    return {k: d for k, d in df.groupby(col_name)}


def has_mod(mod_dict, mod):
    return mod in mod_dict.values()


def split_mods(df, mod_id_to_name_dict, mod_dict_col='mod_dict', single_mod_only=True,
               keep_same_unmodified_sequence=True, unmod_seq_col='unmodified_sequence'):
    if single_mod_only:
        df = df[df[mod_dict_col].str.len() <= 1]

    unmod_records = df[df[mod_dict_col].str.len() == 0]

    mod_dfs = {}
    for m in mod_id_to_name_dict.keys():
        mod_df = df[df[mod_dict_col].apply(has_mod, args=(m,))]
        if keep_same_unmodified_sequence:
            unmod_seqs = unmod_records[unmod_records[unmod_seq_col].isin(mod_df[unmod_seq_col])]
            mod_df = pd.concat([mod_df, unmod_seqs])
        mod_dfs[m] = mod_df

    return mod_dfs


def split(df, split_type, mod_id_to_name_dict=None, mod_dict_col='mod_dict', single_mod_only=False,
          keep_same_unmodified_sequence=False, unmod_seq_col='unmodified_sequence', col_name=None):
    if split_type == 'mod_unmod':
        ret = split_mod_unmod(df, mod_dict_col)
    elif split_type == 'mods':
        ret = split_mods(df, mod_id_to_name_dict, mod_dict_col, single_mod_only, keep_same_unmodified_sequence,
                         unmod_seq_col)
    elif split_type == 'col':
        ret = split_col(df, col_name)
    else:
        raise NotImplementedError(f'Unexpected value for split_type: {split_type}')

    return ret


def subsample_df(df, subsample):
    if len(df) > subsample:
        df = df.sample(n=subsample)
    return df

