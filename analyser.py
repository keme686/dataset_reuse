__author__ = 'kemele'

from scipy.stats.stats import pearsonr
import urllib2
import sys
import json
import pprint
import datetime
import os
import urlparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def from_pkl(fname):
    data = pd.read_pickle(fname)

    return data


def from_csv(fname):
    data = pd.read_csv(fname)

    return data


def combine_stat_results():

    pub_usages = from_csv("results/publications/usages/analysis_results_usages.csv")
    print pub_usages.columns
    mcols = ['id', 'name', 'title', 'alt_name', 'publications', 'total_usage', 'total_mentions_pub', 'total_mentions_lod', 'total_mentions_sem', 'enpoint_uptime', 'endpoint_threshold', '']



    #pub_mentions = from_csv("results/mentions/mention_results.csv")
    #lod_mentions = from_csv("results/lod_w3/per_thread/lod_usage_results_in_thread.csv")
    #sem_mentions = from_csv("results/sem_w3/per_thread/lod_usage_results_per_thread.csv")

    #result = pd.concat([pub_mentions, pub_usages, lod_mentions, sem_mentions], axis=1)

    #bf1aad58-4f5c-4344-9b6c-7e24f1def2cf


def do_mention_pub_corr(val=1):
    pub_mentions = pd.read_csv("results/publications/mentions/analysis_results_mentions.csv")
    pub_mentions = pd.DataFrame(pub_mentions,
                          columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                                   '2011', '2012', '2013', '2014', '2015'])
    quality = pd.read_pickle('results/quality_eval.pkl')
    quality = pd.DataFrame(quality, columns=['id', 'ds_name', 'created', 'dump_availability', 'overall_uptime',
                                             'sparql_endpoint'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)
    pub_mentions.loc[:, 'name'] = pd.Series(quality['ds_name'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'sparql_endpoint'] = pd.Series(quality['sparql_endpoint'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'created'] = pd.Series(quality['created'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'dump_availability'] = pd.Series(quality['dump_availability'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'overall_uptime'] = pd.Series(quality['overall_uptime'].fillna(0).values, index=pub_mentions.index)
    if val == 1:
        x = [2016-float(d['created'][:4]) for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Age of Dataset')
    elif val == 2:
        x = [d['dump_availability'] for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Availability of Dataset Dump')
    else:
        x = [d['overall_uptime'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        y = [d['total'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        plt.xlabel('Overall SPARQL endpoint Up-time')

    plt.title('Scatter plot')

    plt.ylabel('Number of Mention in Full-text of Papers')

    print np.corrcoef(x, y)[0, 1]

    print len(x)
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def do_usage_pub_corr(val=1):
    pub_mentions = pd.read_csv("results/publications/usages/analysis_results_usages.csv")
    pub_mentions = pd.DataFrame(pub_mentions,
                          columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                                   '2011', '2012', '2013', '2014', '2015'])
    quality = pd.read_pickle('results/quality_eval.pkl')
    quality = pd.DataFrame(quality, columns=['id', 'ds_name', 'created', 'dump_availability', 'overall_uptime',
                                             'sparql_endpoint'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)
    pub_mentions.loc[:, 'name'] = pd.Series(quality['ds_name'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'sparql_endpoint'] = pd.Series(quality['sparql_endpoint'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'created'] = pd.Series(quality['created'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'dump_availability'] = pd.Series(quality['dump_availability'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'overall_uptime'] = pd.Series(quality['overall_uptime'].fillna(0).values, index=pub_mentions.index)
    if val == 1:
        x = [2016-int(d['created'][:4]) for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Age of Dataset')
    elif val == 2:
        x = [d['dump_availability'] for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Availability of Dataset Dump')
    else:
        x = [d['overall_uptime'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        y = [d['total'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        plt.xlabel('Overall SPARQL endpoint Up-time')


    plt.title('Scatter plot')

    plt.ylabel('Number of Mention in Experiment Section of Papers')

    print np.corrcoef(x, y)[0, 1]

    print len(x)
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def do_mention_lod_corr(val=1):
    pub_mentions = pd.read_csv("results/lod_w3/per_thread/lod_usage_results_in_thread.csv")
    pub_mentions = pd.DataFrame(pub_mentions,
                          columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                                   '2011', '2012', '2013', '2014', '2015'])
    quality = pd.read_pickle('results/quality_eval.pkl')
    quality = pd.DataFrame(quality, columns=['id', 'ds_name', 'created', 'dump_availability', 'overall_uptime',
                                             'sparql_endpoint'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)
    pub_mentions.loc[:, 'name'] = pd.Series(quality['ds_name'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'sparql_endpoint'] = pd.Series(quality['sparql_endpoint'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'created'] = pd.Series(quality['created'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'dump_availability'] = pd.Series(quality['dump_availability'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'overall_uptime'] = pd.Series(quality['overall_uptime'].fillna(0).values, index=pub_mentions.index)
    if val == 1:
        x = [2016-float(d['created'][:4]) for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Age of Dataset')
    elif val == 2:
        x = [d['dump_availability'] for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Availability of Dataset Dump')
    else:
        x = [d['overall_uptime'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        y = [d['total'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        plt.xlabel('Overall SPARQL endpoint Up-time')

    plt.title('Scatter plot')

    plt.ylabel('Number of Mention in lod-w3 Mailing-list')

    print np.corrcoef(x, y)[0, 1]

    print len(x)
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def do_mention_sem_corr(val=1):
    pub_mentions = pd.read_csv("results/sem_w3/per_thread/lod_usage_results_per_thread.csv")
    pub_mentions = pd.DataFrame(pub_mentions,
                          columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                                   '2011', '2012', '2013', '2014', '2015'])
    quality = pd.read_pickle('results/quality_eval.pkl')
    quality = pd.DataFrame(quality, columns=['id', 'ds_name', 'created', 'dump_availability', 'overall_uptime',
                                             'sparql_endpoint'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)
    pub_mentions.loc[:, 'name'] = pd.Series(quality['ds_name'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'sparql_endpoint'] = pd.Series(quality['sparql_endpoint'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'created'] = pd.Series(quality['created'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'dump_availability'] = pd.Series(quality['dump_availability'].values, index=pub_mentions.index)
    pub_mentions.loc[:, 'overall_uptime'] = pd.Series(quality['overall_uptime'].fillna(0).values, index=pub_mentions.index)
    if val == 1:
        x = [2016-float(d['created'][:4]) for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Age of Dataset')
    elif val == 2:
        x = [d['dump_availability'] for i, d in pub_mentions.iterrows()]
        y = [d['total'] for i, d in pub_mentions.iterrows()]
        plt.xlabel('Availability of Dataset Dump')
    else:
        x = [d['overall_uptime'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        y = [d['total'] for i, d in pub_mentions.iterrows() if d['sparql_endpoint'] > 0]
        plt.xlabel('Overall SPARQL endpoint Up-time')

    plt.title('Scatter plot')

    plt.ylabel('Number of Mention in sem-w3 Mailing-list')

    print np.corrcoef(x, y)[0, 1]

    print len(x)
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def metionVsUsage_pub():
    pub_usages = pd.read_csv("results/publications/usages/analysis_results_usages.csv")
    pub_usages = pd.DataFrame(pub_usages, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_usages.iterrows()]

    pub_usages.loc[:, 'total'] = pd.Series(v, index=pub_usages.index)

    pub_mentions = pd.read_csv("results/publications/mentions/analysis_results_mentions.csv")
    pub_mentions = pd.DataFrame(pub_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)

    y = [d['total'] for i, d in pub_usages.iterrows()]
    x = [d['total'] for i, d in pub_mentions.iterrows()]
    plt.title('Scatter plot')
    plt.xlabel('Number of Mentions in Full-text')
    plt.ylabel('Number of Mention in Experiment Section')

    print np.corrcoef(x, y)[0, 1]
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def metionVsUsage_sem():
    pub_usages = pd.read_csv("results/publications/usages/analysis_results_usages.csv")
    pub_usages = pd.DataFrame(pub_usages, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_usages.iterrows()]

    pub_usages.loc[:, 'total'] = pd.Series(v, index=pub_usages.index)

    pub_mentions = pd.read_csv("results/sem_w3/per_thread/lod_usage_results_per_thread.csv")
    pub_mentions = pd.DataFrame(pub_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]

    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)

    y = [d['total'] for i, d in pub_usages.iterrows()]
    x = [d['total'] for i, d in pub_mentions.iterrows()]
    plt.title('Scatter plot')
    plt.xlabel('Number of Mentions in sem-w3 Mailing-list')
    plt.ylabel('Number of Mention in Experiment Section')

    print np.corrcoef(x, y)[0, 1]
    print pearsonr(x, y)
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    #plt.show()


def pubVssem_mentions():
    pub_mentions = pd.read_csv("results/publications/mentions/analysis_results_mentions.csv")
    pub_mentions = pd.DataFrame(pub_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])

    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]
    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)

    #lod_mentions = from_csv("results/lod_w3/per_thread/lod_usage_results_in_thread.csv")
    #lod_mentions = pd.DataFrame(lod_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               #'2011', '2012', '2013', '2014', '2015'])

    sem_mentions = from_csv("results/sem_w3/per_thread/lod_usage_results_per_thread.csv")
    sem_mentions = pd.DataFrame(sem_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])
    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in sem_mentions.iterrows()]
    sem_mentions.loc[:, 'total'] = pd.Series(v, index=sem_mentions.index)

    x = [d['total'] for i, d in sem_mentions.iterrows()]
    y = [d['total'] for i, d in pub_mentions.iterrows()]

    plt.title('Scatter plot')
    plt.xlabel('Number of Mentions in sem-w3 mailing list')
    plt.ylabel('Number of Mention in Papers')

    print np.corrcoef(x, y)[0, 1]
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def pubVslod_mentions():
    pub_mentions = pd.read_csv("results/publications/mentions/analysis_results_mentions.csv")
    pub_mentions = pd.DataFrame(pub_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])

    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]
    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)

    sem_mentions = from_csv("results/lod_w3/per_thread/lod_usage_results_in_thread.csv")
    sem_mentions = pd.DataFrame(sem_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])

    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in sem_mentions.iterrows()]
    sem_mentions.loc[:, 'total'] = pd.Series(v, index=sem_mentions.index)

    x = [d['total'] for i, d in sem_mentions.iterrows()]
    y = [d['total'] for i, d in pub_mentions.iterrows()]

    plt.title('Scatter plot')
    plt.xlabel('Number of Mentions in lod-w3 mailing list')
    plt.ylabel('Number of Mention in Papers')

    print np.corrcoef(x, y)[0, 1]
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()


def lodVssem_mentions():
    pub_mentions = pd.read_csv("results/lod_w3/per_thread/lod_usage_results_in_thread.csv")
    pub_mentions = pd.DataFrame(pub_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])

    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in pub_mentions.iterrows()]
    pub_mentions.loc[:, 'total'] = pd.Series(v, index=pub_mentions.index)

    sem_mentions = from_csv("results/sem_w3/per_thread/lod_usage_results_per_thread.csv")
    sem_mentions = pd.DataFrame(sem_mentions, columns=['id', 'title', 'alt_name', 'publications', '2007', '2008', '2009', '2010',
                               '2011', '2012', '2013', '2014', '2015'])

    v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         for i, d in sem_mentions.iterrows()]
    sem_mentions.loc[:, 'total'] = pd.Series(v, index=sem_mentions.index)

    x = [d['total'] for i, d in sem_mentions.iterrows()]
    y = [d['total'] for i, d in pub_mentions.iterrows()]

    plt.title('Scatter plot')
    plt.xlabel('Number of Mentions in sem-w3 mailing list')
    plt.ylabel('Number of Mention in lod-w3 mailing list')

    print np.corrcoef(x, y)[0, 1]
    for index in range(len(x)):
        plt.scatter(x[index], y[index], c='blue')
    plt.show()

if __name__=='__main__':
    reload(sys)
    sys.setdefaultencoding("utf8")
    #combine_stat_results()

    #for i in range(1, 4):
        #do_mention_pub_corr(i)

    #do_usage_pub_corr(3)

    #do_mention_lod_corr(1)

    #do_mention_sem_corr(1)

    #metionVsUsage_pub()
    #metionVsUsage_sem()
    #pubVssem_mentions()
    #pubVslod_mentions()
    #lodVssem_mentions()

    #results/mentions/mention_results.csv.pkl
    ment = pd.read_pickle("results/publications/mentions/mention_results.csv.pkl")

    #v = [d['2007'] + d['2008'] + d['2009'] + d['2010'] + d['2011'] + d['2012'] + d['2013'] + d['2014'] + d['2015']
         #for i, d in ment.iterrows()]
    #ment.loc[:, 'total'] = pd.Series(v, index=ment.index)
    print ment['total'].sum()
    x = ['']
    y = ['']
