import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from src.util import split, subsample_df


def connected_scatterplot(lbl, val, id, **kwargs):
    df = pd.DataFrame({'lbl': lbl, 'val': val, 'id': id})
    if 'x_values' in kwargs:
        x_ticks = np.linspace(0, 1, len(kwargs['x_values']))
        x_values = kwargs['x_values']
    else:
        x_ticks = np.linspace(0, 1, len(df['lbl'].unique()))
        x_values = sorted(df['lbl'].unique())
    for p, grp in df.groupby('id'):
        plt.plot(np.linspace(0, 1, len(grp)),
                 [grp[grp['lbl'] == lbl]['val'].iloc[0] for lbl in sorted(grp['lbl'].unique())])
    plt.xticks(x_ticks, x_values, rotation=-45, ha="left")


def annotate(data, **kws):
    len_dict = kws['len_dict']
    split1_name = kws['split1_name']
    ax = plt.gca()
    ax.text(.1, 0.01, f"N = {len_dict[data.iloc[0][split1_name]]}", transform=ax.transAxes)


def plot_mod_unmod_split(df_dict, plot_col='iRT', subsample=None, split1_name='modification',
                         unmod_seq_col='unmodified_sequence', col_wrap=5, height=10, aspect=0.5,
                         save_file=None, dpi=600, **mod_unmod_kwargs):
    all_dfs = []
    len_dict = {}
    for k, df in df_dict.items():
        m_um_dict = split(df, split_type='mod_unmod', **mod_unmod_kwargs)

        overlap = pd.merge(m_um_dict['mod'], m_um_dict['unmod'], how='outer', on=unmod_seq_col)

        len_dict[k] = len(overlap)

        if subsample is not None:
            overlap = subsample_df(overlap, subsample)

        overlap['_id'] = range(len(overlap))
        new_dfs = []
        for m, val in zip(['mod', 'unmod'], ['x', 'y']):
            new_df = overlap.copy()
            new_df[plot_col] = new_df[f'{plot_col}_{val}']
            new_df['mod/unmod'] = m
            new_dfs.append(new_df)
        new_dfs = pd.concat(new_dfs)
        new_dfs[split1_name] = k
        all_dfs.append(new_dfs)
    all_dfs = pd.concat(all_dfs)

    g = sns.FacetGrid(all_dfs, col=split1_name, col_wrap=col_wrap, height=height, aspect=aspect)
    g.map(connected_scatterplot, 'mod/unmod', plot_col, '_id')
    g.map_dataframe(annotate, len_dict=len_dict, split1_name=split1_name)
    plt.savefig(save_file, dpi=dpi)


def plot_col_split(df_dict, plot_col='iRT', subsample=None, split1_name='modification', mod_seq_col='modified_sequence',
                   col_wrap=5, height=10, aspect=0.5, save_file=None, dpi=600, **split_kwargs):
    all_dfs = []
    len_dict = {}
    for k, df in df_dict.items():
        col_dict = split(df, split_type='col', **split_kwargs)
        m0, overlap = list(col_dict.items())[0]
        overlap[f'{plot_col}_{m0}'] = overlap[plot_col]
        for m, d in list(col_dict.items())[1:]:
            d = d[[mod_seq_col, plot_col]]
            overlap = pd.merge(overlap, d, on=mod_seq_col, how='outer', suffixes=("", f"_{m}"))

        len_dict[k] = len(overlap)

        if subsample is not None:
            overlap = subsample_df(overlap, subsample)

        overlap['_id'] = range(len(overlap))
        new_dfs = []
        for val in col_dict.keys():
            new_df = overlap.copy()
            new_df[plot_col] = new_df[f'{plot_col}_{val}']
            new_df[split_kwargs['col_name']] = val
            new_dfs.append(new_df)
        new_dfs = pd.concat(new_dfs)
        new_dfs[split1_name] = k
        all_dfs.append(new_dfs)
    all_dfs = pd.concat(all_dfs)
    all_x_values = all_dfs[split_kwargs['col_name']].unique()

    g = sns.FacetGrid(all_dfs, col=split1_name, col_wrap=col_wrap, height=height, aspect=aspect)
    g.map(connected_scatterplot, split_kwargs['col_name'], plot_col, '_id', x_values=all_x_values)
    g.map_dataframe(annotate, len_dict=len_dict, split1_name=split1_name)
    plt.savefig(save_file, dpi=dpi)


def plot_multi_col_split(df_dict, compare_cols=None, y_name=None, subsample=None, split1_name='modification'):
    if y_name is None:
        y_name = compare_cols[0]
    x_name = '_'.join(compare_cols)
    all_dfs = []
    len_dict = {}
    for k, df in df_dict.items():
        len_dict[k] = len(df)

        if subsample is not None:
            df = subsample_df(df, subsample)

        df['_id'] = range(len(df))

        new_dfs = []
        for c in compare_cols:
            new_df = df.copy()
            new_df[y_name] = new_df[c]
            new_df[x_name] = c
            new_dfs.append(new_df)
        new_dfs = pd.concat(new_dfs)
        new_dfs[split1_name] = k
        all_dfs.append(new_dfs)
    all_dfs = pd.concat(all_dfs)

    g = sns.FacetGrid(all_dfs, col=split1_name, col_wrap=6, height=6, aspect=.5)
    g.map(connected_scatterplot, x_name, y_name, '_id')
    g.map_dataframe(annotate, len_dict=len_dict, split1_name=split1_name)
    plt.show()
