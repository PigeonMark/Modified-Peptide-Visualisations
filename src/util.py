def add_length(df, len_col='length', unmod_seq_col='unmodified_sequence'):
    df[len_col] = df[unmod_seq_col].str.len()
    return df


def split(df, split_type):
    if split_type == 'mod_unmod':
        pass
    elif split_type == 'col':
        raise NotImplementedError('Splitting on column value is not yet implemented')
