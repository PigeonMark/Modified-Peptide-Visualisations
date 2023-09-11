import pandas as pd


def add_length(df, len_col='length', unmod_seq_col='unmodified_sequence'):
    df[len_col] = df[unmod_seq_col].str.len()
    return df


def num_modifications(proforma_tuple):
    mod_count = sum(1 for s in proforma_tuple[0] if s[1] is not None)
    n_term = proforma_tuple[1]['n_term']
    c_term = proforma_tuple[1]['c_term']

    if n_term is not None:
        mod_count += len(n_term)

    if c_term is not None:
        mod_count += len(c_term)

    return mod_count


def filter_num_mods(df, num=None, proforma_col='proforma', add_to_df=False):
    if num is None:
        raise ValueError('num must be an int or a list of ints')

    if isinstance(num, int):
        num = [num]

    num_mods = df[proforma_col].apply(num_modifications)

    if add_to_df:
        df['num_mods'] = num_mods

    return pd.concat([df[num_mods == n] for n in num])


def split_mod_unmod(df, proforma_col='proforma'):
    if 'num_mods' not in df.columns:
        num_mods = df[proforma_col].apply(num_modifications)
    else:
        num_mods = df['num_mods']

    return df[num_mods > 0], df[num_mods == 0]


def split_col(df, col_name):
    return [d for _, d in df.groupby(col_name)]


def has_mod(proforma_tuple, mod):
    for p in proforma_tuple[0]:
        if p[1] is not None:
            for m in p[1]:
                if m.value == mod:
                    return True
    n_term = proforma_tuple[1]['n_term']
    c_term = proforma_tuple[1]['c_term']
    if n_term is not None:
        for n in n_term:
            if n.value == mod:
                return True
    if c_term is not None:
        for c in c_term:
            if c.value == mod:
                return True
    return False


def get_all_mods(proforma_col):
    all_mods = set()
    for p in proforma_col:
        for aa, m in p[0]:
            if m is not None:
                all_mods.update(n.value for n in m)

        n_term = p[1]['n_term']
        c_term = p[1]['c_term']
        if n_term is not None:
            all_mods.update(n.value for n in n_term)
        if c_term is not None:
            all_mods.update(c.value for c in c_term)

    return all_mods


def split_mods(df, proforma_col='proforma', single_mod_only=True, keep_same_unmodified_sequence=True,
               unmod_seq_col='unmodified_sequence'):
    if single_mod_only:
        df = filter_num_mods(df, [0, 1], proforma_col, add_to_df=True)
        unmod_records = df[df['num_mods'] == 0]
    else:
        unmod_records = filter_num_mods(df, 0, proforma_col)

    all_mods = get_all_mods(df[proforma_col])
    mod_dfs = {}
    for m in all_mods:
        mod_df = df[df[proforma_col].apply(has_mod, args=(m,))]
        if keep_same_unmodified_sequence:
            unmod_seqs = unmod_records[unmod_records[unmod_seq_col].isin(mod_df[unmod_seq_col])]
            mod_df = pd.concat([mod_df, unmod_seqs])
        mod_dfs[m] = mod_df

    return mod_dfs


def split(df, split_type, proforma_col='proforma', single_mod_only=False, keep_same_unmodified_sequence=False,
          unmod_seq_col='unmodified_sequence', col_name=None):
    if split_type == 'mod_unmod':
        ret = split_mod_unmod(df, proforma_col=proforma_col)
    elif split_type == 'mods':
        ret = split_mods(df, proforma_col=proforma_col, single_mod_only=single_mod_only,
                         keep_same_unmodified_sequence=keep_same_unmodified_sequence, unmod_seq_col=unmod_seq_col)
    elif split_type == 'col':
        ret = split_col(df, col_name)
    else:
        raise NotImplementedError(f'Unexpected value for split_type: {split_type}')

    return ret
