import pandas as pd
import pyteomics.proforma

# TODO: support more filetypes
from src.util import add_length


def read_file(filepath, filetype='csv', sep=',', index_col=0):
    if filetype == 'csv':
        df = pd.read_csv(open(filepath, 'r'), sep=sep, index_col=index_col)
    else:
        raise NotImplementedError("Only csv files are supported right now")
    df = df.reset_index(drop=True)
    return df


def parse_modifications(df, mod_seq_col, proforma_col='proforma', unmod_seq_col='unmodified_sequence', remove_old=True):
    def extract_unmod_seq(p):
        return ''.join([a[0] for a in p[0]])

    df[proforma_col] = df[mod_seq_col].apply(pyteomics.proforma.parse)
    df[unmod_seq_col] = df[proforma_col].apply(extract_unmod_seq)

    if remove_old:
        del df[mod_seq_col]

    return df


if __name__ == "__main__":
    df = read_file('data/iRT_unimod_unfiltered.csv')
    df = parse_modifications(df, 'modified_sequence')
    df = add_length(df)
