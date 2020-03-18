import pandas as pd
from fil import time_plot, EasyDF
from datetime import date, timedelta

from os import environ
environ['TK_SILENCE_DEPRECATION'] = "1"

if __name__ == '__main__':

    print('downloading data...')
    CONFIRMED_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
    confirmed = pd.read_csv(CONFIRMED_URL)
    confirmed['3/12/20'] = (confirmed['3/13/20']+confirmed['3/11/20'])//2
    confirmed.index.name = 'Confirmed cases'

    DEATHS_URL = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv'
    deaths = pd.read_csv(DEATHS_URL)
    deaths['3/12/20'] = (deaths['3/13/20']+deaths['3/11/20'])//2
    deaths.index.name = 'Deaths'

    REGIONI_URL = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
    regioni = EasyDF(pd.read_csv(REGIONI_URL).drop(columns=['stato', 'codice_regione', 'lat', 'long']))

    print('generating plots...')
    time_plot(confirmed, ['Italy', 'Spain', 'France', 'Germany', 'United Kingdom']).figure.savefig('plots/europe1_confirmed.png', bbox_inches='tight')
    time_plot(confirmed, ['Italy', 'Austria', 'Switzerland', 'Belgium', 'Netherlands']).figure.savefig('plots/europe2_confirmed.png', bbox_inches='tight')
    time_plot(confirmed, ['Italy', 'US', 'Canada']).figure.savefig('plots/usca_confirmed.png', bbox_inches='tight')
    time_plot(confirmed, ['China', 'Italy']).figure.savefig('plots/zh-it_confirmed.png', bbox_inches='tight')
    time_plot(deaths, ['Italy', 'Spain', 'France', 'Germany', 'United Kingdom']).figure.savefig('plots/europe1_deaths.png', bbox_inches='tight')
    time_plot(deaths, ['Italy', 'Austria', 'Switzerland', 'Belgium', 'Netherlands']).figure.savefig('plots/europe2_deaths.png', bbox_inches='tight')
    time_plot(deaths, ['Italy', 'US', 'Canada']).figure.savefig('plots/usca_deaths.png', bbox_inches='tight')
    time_plot(deaths, ['China', 'Italy']).figure.savefig('plots/zh-it_deaths.png', bbox_inches='tight')

    yesterday = date.today() - timedelta(1)
    five_most_cases = list(regioni[regioni['data']==yesterday].sort_values(by=['totale_casi']).denominazione_regione)[-5:]

    regioni.plot('totale_casi', five_most_cases, title='Total cases').figure.savefig('plots/IT-cases.png', bbox_inches='tight')
    regioni.plot('deceduti', five_most_cases, title = 'Total deaths', ylabel='Deaths').figure.savefig('plots/IT-deaths.png', bbox_inches='tight')
    regioni.plot('deceduti', five_most_cases, norm='totale_casi', title = 'Mortality rate (deaths/tot cases)', ylabel = 'Rate').figure.savefig('plots/IT-mortality.png', bbox_inches='tight')
    regioni.plot('terapia_intensiva', five_most_cases, norm='totale_ospedalizzati', title = 'ICU rate among hospitalized', ylabel = 'Rate').figure.savefig('plots/IT-ICU_rate.png', bbox_inches='tight')
