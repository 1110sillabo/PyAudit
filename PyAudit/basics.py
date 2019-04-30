import numpy as np
import pandas as pd
from scipy.stats import norm


def dtypes_class(df_in):
    """
    numerical, categorical and bool name list in the DataFrame

    :param df_in: input pandas DataFrame
    :return: numerical, categorical and bool name list

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> from PyAudit.basics import dtypes_class
    >>> df = pd.read_csv('Heart.csv', dtype={'Sex': bool})
    >>> (num_fields, cat_fields, bool_fields, data_types, type_class) = dtypes_class(df)
    >>> num_fields
    ['Age', 'RestBP', 'Chol', 'Fbs', 'RestECG', 'MaxHR', 'ExAng', 'Oldpeak', 'Slope', 'Ca']
    """

    # quantitative data types in pandas dtypes
    num_types = ['int64', 'float64']
    # qualitative data types in pandas dtypes
    cat_types = ['object', 'datetime64', 'category']
    # bool data types in pandas dtypes
    bool_types = ['bool']

    all_types = pd.DataFrame(df_in.dtypes).reset_index() \
                  .rename(columns={'index': 'feature', 0: 'dtypes'})

    data_types = all_types.copy()
    all_types['class'] = ['numeric' if x in num_types else
                          'bool' if x in bool_types else
                          'category' if x in cat_types else
                          'unknown' for x in all_types['dtypes'].tolist()]

    quant_fields = all_types[all_types['class'] == 'numeric']['feature'].tolist()
    quanl_fields = all_types[all_types['class'] == 'category']['feature'].tolist()
    bool_fields = all_types[all_types['class'] == 'bool']['feature'].tolist()
    return quant_fields, quanl_fields, bool_fields, data_types, all_types


def missing_rate(df_in):
    """
    calculate missing rate for each feature in the DataFrame

    :param df_in: input pandas DataFrame
    :return: missing rate

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> import pandas as pd
    >>> d = {'A': [1, 0, None, 3],
             'B': [1, 0, 0, 0],
             'C': ['a', None, 'c', 'd']}
    >>> # create DataFrame
    >>> df = pd.DataFrame(d)
    >>> from PyAudit.basics import missing_rate
    >>> missing_rate(df)
             feature  missing_rate
           0       A          0.25
           1       B          0.00
           2       C          0.25
    """

    rate = df_in.isnull().sum() / df_in.shape[0]
    # rename the column
    percentage_miss = pd.DataFrame(rate).reset_index()\
                        .rename(columns={'index': 'feature', 0: 'missing_rate'})
    return percentage_miss


def zero_rate(df_in):
    """
    calculate the percentage of 0 value for each feature in the DataFrame

    :param df_in: input pandas DataFrame
    :return: zero rate

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> import pandas as pd
    >>> d = {'A': [1, 0, None, 3],
             'B': [1, 0, 0, 0],
             'C': ['a', None, 'c', 'd']}
    >>> # create DataFrame
    >>> df = pd.DataFrame(d)
    >>> from PyAudit.basics import zero_rate
    >>> zero_rate(df)
             feature  zero_rate
           0       A   0.333333
           1       B   0.750000
           2       C   0.000000
    """

    rate = ((df_in == 0).sum(axis=0)) / df_in.notnull().sum()
    # rename the column
    percentage_zero = pd.DataFrame(rate).reset_index()\
                        .rename(columns={'index': 'feature', 0: 'zero_rate'})
    return percentage_zero


def feature_variance(df_in):
    """
    calculate the variance for each feature

    :param df_in: input pandas DataFrame
    :return: feature variance

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> import pandas as pd
    >>> d = {'A': [1, 0, None, 3],
             'B': [1, 0, 0, 0],
             'C': ['a', None, 'c', 'd']}
    >>> # create DataFrame
    >>> df = pd.DataFrame(d)
    >>> from PyAudit.basics import zero_rate
    >>> zero_rate(df)
             feature  feature_variance
           0       A               1.0
           1       B               0.5
           2       C               1.0
    """

    rate = df_in.nunique() / df_in.notnull().sum()
    rate = pd.DataFrame(rate)\
             .reset_index()\
             .rename(columns={'index': 'feature', 0: 'feature_variance'})
    return rate


def freq_items_df(df_in, top_n=3):
    """
    find out the top n values and the corresponding frequency for each feature

    :param df_in: input pandas DataFrame
    :param top_n: the number of the top values
    :return: top n values and the corresponding frequency for each feature

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> d ={
    >>>    'num': list('1223334444'),
    >>>    'cat': list('wxxyyyzzzz')
    >>>    }
    >>> df = pd.DataFrame(d)
    >>> df = df.astype({"num": int, "cat": object})
    >>> print(freq_items_df(df, top_n=4))
          feature     top_items     top_freqs
        0     num  [4, 3, 2, 1]  [4, 3, 2, 1]
        1     cat  [z, y, x, w]  [4, 3, 2, 1]
    """
    def freq_items(x):
        temp = pd.value_counts(x)
        top_items = temp.index[:top_n].values
        top_freqs = temp.values[:top_n]
        return top_items, top_freqs

    temp = df_in.apply(freq_items)

    d = {'feature':  df_in.columns,
         'top_items': [i[0] for i in temp],
         'top_freqs': [i[1] for i in temp]}
    return pd.DataFrame(d)


def feature_len(df_in):
    """
    find out the min and max length of values for each feature

    :param df_in: input pandas DataFrame
    :return: min and max length DataFrame

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com
    
    >>> d = {'A': [1, 0, None, 3],
    >>>      'B': [1, 0, 0, 0],
    >>>      'C': ['a', None, 'c', 'd']}
    >>> # create DataFrame
    >>> df = pd.DataFrame(d)
    >>> print(df)
             A  B     C
        0  1.0  1     a
        1  0.0  0  None
        2  NaN  0     c
        3  3.0  0     d
    >>> print(feature_len(df))
        feature  min_length  max_length
      0       A           3           3
      1       B           1           1
      2       C           1           4
    """
    def fea_len(f):
        temp = f.map(lambda x: len(str(x)))
        return temp.min(), temp.max()

    temp = df_in.apply(fea_len)
    d = {'feature': df_in.columns,
         'min_length': [i[0] for i in temp],
         'max_length': [i[1] for i in temp]}
    return pd.DataFrame(d)


def numeric_summary(df_in, deciles=False):
    """
    generate statistical summary for numerical DateFrame

    :param df_in: input pandas DataFrame
    :param deciles: flag for percentiles style
    :return: statistical summary for numerical data

    :author: Wenqiang Feng and Ming Chen
    :email:  von198@gmail.com

    >>> d = {'A': [1, 0, None, 3],
    >>>      'B': [1, 0, 0, 0],
    >>>      'C': ['a', None, 'c', 'd']}
    >>> # create DataFrame
    >>> df = pd.DataFrame(d)
    >>> print(numeric_summary(df))
          feature data_type  min_digits  ...  zero_rate  pos_rate  neg_rate
        A       A   float64           3  ...   0.333333  0.666667       0.0
        B       B     int64           3  ...   0.750000  0.250000       0.0
    """
    
    (num_fields, cat_fields, bool_fields, data_types, data_class) = dtypes_class(df_in)
    df_in = df_in[num_fields]
    
    if deciles:
        var_name = 'deciles'
        percentiles = np.array(range(0, 110, 10))
    else:
        var_name = 'percentiles'
        percentiles = [25, 50, 75]

    def col_wise(f):
        fea_len = f.map(lambda x: len(str(x)))
        fea_mean = f.mean()
        fea_std = f.std()
        fea_count = np.sqrt(f.count())
        fea_notnull = f.notnull().sum()
        return fea_len.min(),\
               fea_len.max(),\
               f.shape[0],\
               f.count(),\
               len(f.unique()),\
               f.min(), \
               np.percentile(f[f.notnull()], percentiles), \
               f.max(), \
               fea_mean, \
               f.std(), \
               fea_mean - 1.96 * fea_std  / fea_count , \
               fea_mean + 1.96 * fea_std  / fea_count,  \
               f.sum(),\
               f.isnull().sum() /f.shape[0],\
               ((f == 0).sum(axis=0)) / fea_notnull,\
               ((f > 0).sum(axis=0)) / fea_notnull,\
               ((f < 0).sum(axis=0)) / fea_notnull

    temp = np.transpose(df_in.apply(col_wise))
    
    col_names = ['feature','data_type','min_digits','max_digits','row_count',
                 'notnull_count','distinct_count', 'min',var_name,'max','mean',
                 'std','lower_95_ci','upper_95_ci','sum','missing_rate','zero_rate',
                 'pos_rate','neg_rate']
    col_value = [df_in.columns] + [df_in.dtypes] \
              + [[col[i] for col in temp] for i in range(len(col_names)-2)]
    
    d = {key: value for key, value in zip(col_names, col_value)}
    return pd.DataFrame(d)

