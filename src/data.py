import pandas as pd


def read_file(filepath, filetype='csv', sep=',', index_col=0):
    if filetype == 'csv':
        df = pd.read_csv(open(filepath, 'r'), sep=sep, index_col=index_col)
    else:
        raise NotImplementedError("Only csv files are supported right now")
    return df


if __name__ == "__main__":
    read_file('data/iRT_unimod.csv')
