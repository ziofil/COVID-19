import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt

# LOADING DATA

# with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as file:
#     confirmed = pd.read_csv(file)
#     confirmed.index.name='Confirmed Cases'
    
# with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv") as file:
#     deaths = pd.read_csv(file)
#     deaths.index.name='Deaths'
    
# with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv") as file:
#     recovered = pd.read_csv(file)
#     recovered.index.name='Recovered'

def select_country(dataframe, country, sum=True):
    if sum:
        series = dataframe[dataframe['Country/Region'] == country].sum().drop(['Province/State','Country/Region','Lat','Long'])
    else:
        series = dataframe[dataframe['Country/Region'] == country]

    series.index = pd.to_datetime(series.index)
    series.name = country + f' ({series[-1]} cases)'
    return series

def compute_lag(ref_series, other_series):
    '''returns the number of days to shift other_series backward
    in order to maximize overlap with ref_series'''
    adj_ref_series = np.pad(np.array(ref_series), (len(ref_series), 0))
    adj_other_series = np.pad(np.array(other_series), (len(ref_series), 0))
    penalties = [np.sum(np.abs(adj_ref_series[:-r] - adj_other_series[r:])) for r in range(1, len(ref_series))]
    delay = np.argmin(penalties) + 1
    return delay

def time_plot(dataframe, countries:list, lag:int = None, **kwargs):
    selected_series = [select_country(dataframe, country) for country in countries]
    order = list(reversed(np.argsort([s[-1] for s in selected_series]))) # order by latest number of cases
    data = pd.DataFrame()
    data = data.append(selected_series[order[0]])
    for o in order[1:]:
        series = selected_series[o]
        lag_ = lag or compute_lag(selected_series[order[0]], series)
        shifted = series.shift(-lag_)
        shifted.name = shifted.name + f', {lag_} days behind {countries[order[0]]})'
        data = data.append(shifted)
        
    data = data.transpose()
    data = data[data.index > '2020-01-23']

    ax = data.plot(figsize=(10,7), linewidth=3.0, grid=True, title = dataframe.index.name, **kwargs)
    ax.title.set_size(18)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.tick_params(axis='both', which='minor', labelsize=18)
    ax.set_ylabel(dataframe.index.name, fontsize=18)
    ax.legend(prop={'size':16})

    return ax


class EasyDF(pd.DataFrame):
    
    def __init__(self, df):
        df.data = pd.to_datetime(df.data).dt.date
        super().__init__(df)
    
    def select_from_column(self, col:str, lst:list):
        if lst is None:
            return self
        return self[self[col].isin(lst)]
    
    def exclude_from_column(self, col:str, lst:list):
        if lst is None:
            return self
        return self[~self[col].isin(lst)]
    
    def renormalize(self, col):
        self_num = self.select_dtypes(include=[np.number])
        tmp = self_num.divide(self[col], axis='index')
        tmp = tmp.fillna(0)
        self_copy = self.copy()
        self_copy[tmp.columns] = tmp
        return self.__class__(self_copy)
    
    def plot(self, col:str, regioni:list=None, norm:str=None, title:str=None, ylabel:str=None):
        if regioni is None:
            hue = None
        else:
            hue = 'denominazione_regione'
        if norm is None:
            data = self.select_from_column('denominazione_regione', regioni)
        else:
            data = self.renormalize(norm).select_from_column('denominazione_regione', regioni)
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="data", y=col, hue=hue, data=data)
        ax.get_xticklabels()
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        plt.legend(loc='best')
        if title is not None:
            title = title
        else:
            title = col+'/'+norm if norm else col
        
        ax.set_ylabel(ylabel or 'Cases')
        ax.set_title(title)
        return ax