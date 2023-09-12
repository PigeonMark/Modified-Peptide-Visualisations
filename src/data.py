import pandas as pd
from pyteomics.proforma import parse


# TODO: support more filetypes
def read_file(filepath, filetype='csv', sep=',', index_col=0):
    if filetype == 'csv':
        df = pd.read_csv(filepath, sep=sep, index_col=index_col)
    else:
        raise NotImplementedError("Only csv files are supported right now")
    df = df.reset_index(drop=True)
    return df


def parse_modifications(df, mod_seq_col, mod_dict_col='mod_dict', unmod_seq_col='unmodified_sequence'):
    mod_id_to_name = {}

    # TODO: optionally compute mass as well, this will probably take more time
    def parse_mod_seq(s):
        seq, additional_info = parse(s[mod_seq_col])
        mod_dict = {}
        unmod_seq = ''
        for i, t in enumerate(seq):
            unmod_seq += t[0]
            if t[1] is not None:
                id = t[1][0].id
                mod_dict[i] = id
                if id not in mod_id_to_name:
                    mod_id_to_name[id] = t[1][0].name

        n_term = additional_info['n_term']
        if n_term is not None:
            id = n_term[0].id
            mod_dict['n_term'] = id
            if id not in mod_id_to_name:
                mod_id_to_name[id] = n_term[0].name

        c_term = additional_info['c_term']
        if c_term is not None:
            id = c_term[0].id
            mod_dict['c_term'] = id
            if id not in mod_id_to_name:
                mod_id_to_name[id] = c_term[0].name
        return mod_dict, unmod_seq

    df[[mod_dict_col, unmod_seq_col]] = df.apply(parse_mod_seq, axis=1, result_type="expand")

    return df, mod_id_to_name


def merge_duplicates(df, how, col='modified_sequence', to_merge=None, merge_val_col=None):
    """
    Merge duplicate records based on `col`.
    :param df: Dataframe to merge the records from
    :param how: {'mean', 'median', 'col_min', 'col_max'}, how to handle duplicate values in `col`. All column values in
    `to_merge` can be merged by taking the 'mean' or 'median'. Alternatively 'col_min' and 'col_max' merge by taking the
     record with the min or max value of an additional column `merge_val_col`
    :param col: column for which to merge duplicates
    :param to_merge: single column name or list of column names to merge with the `how` practice
    :param merge_val_col: Only used when how is 'col_min' or 'col_max'. Additional column from which the min or max
    value will be computed and the corresponding record will be chosen when merging duplicates.
    :return: merged Dataframe
    """
    if to_merge is None:
        to_merge = []
    if isinstance(to_merge, str):
        to_merge = [to_merge]

    other_cols = [c for c in df.columns if c not in to_merge]

    if how == 'mean':
        merged_vals = df.groupby(by=col)[to_merge].mean()
    elif how == 'median':
        merged_vals = df.groupby(by=col)[to_merge].median()

    elif how == 'col_min':
        if merge_val_col is None:
            raise ValueError("Argument 'merge_val_col' must be given when how is col_min or col_max")
        merged_vals = df.groupby(by=col).min(merge_val_col)[to_merge]
    elif how == 'col_max':
        if merge_val_col is None:
            raise ValueError("Argument 'merge_val_col' must be given when how is col_min or col_max")
        merged_vals = df.groupby(by=col).max(merge_val_col)[to_merge]
    else:
        raise ValueError("Possible values for argument 'how' of remove_duplicates are 'mean', 'median', or 'col'")

    df = df[other_cols].drop_duplicates(col)
    df = pd.merge(df[other_cols], merged_vals, how='outer', left_on=col, right_index=True,
                  validate='1:1').reset_index(drop=True)
    return df


def filter_rows(df, how, col, val):
    if how == 'lt':
        return df[df[col] < val]

    elif how == 'lte':
        return df[df[col] <= val]

    elif how == 'gte':
        return df[df[col] >= val]

    elif how == 'gt':
        return df[df[col] > val]

    elif how == 'eq':
        return df[df[col] == val]

    elif how == 'neq':
        return df[df[col] != val]


def export(df, filepath, as_type='csv', cols=None):
    if cols is not None:
        df = df[cols]

    if as_type == 'csv':
        if not filepath.endswith('.csv'):
            filepath += '.csv'
        df.to_csv(filepath)
