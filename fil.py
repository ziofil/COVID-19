import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
import json5 as js

# LOADING DATA

with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv") as file:
    confirmed = pd.read_csv(file)
    confirmed.index.name='Confirmed Cases'
    
with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv") as file:
    deaths = pd.read_csv(file)
    deaths.index.name='Deaths'
    
with open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv") as file:
    recovered = pd.read_csv(file)
    recovered.index.name='Recovered'


def time_plot(dataframe, countries:list, **kwargs):
    """
    Utility function to be used with the datasets from CSSE.
    It automatically computes the delay between countries.
    """
    data = pd.DataFrame()
    series_ref = dataframe[dataframe['Country/Region'] == countries[0]].sum().drop(['Province/State','Country/Region','Lat','Long'])
    series_ref.index = pd.to_datetime(series_ref.index)
    series_ref.name = countries[0]
    data = data.append(series_ref)
    
    for c in countries[1:]:
        series = dataframe[dataframe['Country/Region'] == c].sum().drop(['Province/State','Country/Region','Lat','Long'])
        delay = np.argmin([np.sum(np.abs(np.array(series_ref[:-r]) - np.array(series[r:]))) for r in range(1, len(series_ref)-10)])+1
        series.index = pd.to_datetime(series.index)
        series.index -= pd.Timedelta(f'{delay} day')
        series.name = c if delay == 0 else c + f' ({delay} days behind)'
        data = data.append(series)
    ax = data.transpose().plot(figsize=(10,7), marker='o', title='Time-adjusted confirmed cases', **kwargs)
    ax.set_ylabel(dataframe.index.name)
    return ax


class EasyDF(pd.DataFrame):
    
    def __init__(self, df):
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
    
    def plot(self, col:str, regioni:list=None, norm:str=None):
        if regioni is None:
            hue = None
        else:
            hue = 'denominazione_regione'
        if norm is None:
            data = self.select_from_column('denominazione_regione', regioni)
        else:
            data = self.renormalize(norm).select_from_column('denominazione_regione', regioni)
        fig = plt.figure(figsize=(15,3))
        ax = sns.barplot(x="data", y=col, hue=hue, data=data)
        ax.get_xticklabels()
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        plt.legend(loc='best')
        title = col+'/'+norm if norm else col
        ax.set_title(title)
        return fig




with open("dati-json/dpc-covid19-ita-regioni.json") as file:
    regioni_raw = js.load(file)

regioni = EasyDF(pd.DataFrame.from_dict(regioni_raw).drop(columns=['stato', 'codice_regione', 'lat', 'long']))