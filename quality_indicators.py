__author__ = 'kemele'


import urllib2
import sys
import json
import pprint
import datetime
import os
import urlparse
import pandas as pd
import numpy as np


def get_datasets(pkl_path="dataset_dictionary.pkl"):

    datasets = pd.read_pickle(pkl_path)
    v = datasets.columns.values
    ba = ['created', 'license_id', 'license_title', 'license_url', 'dump_availability', 'sparql_endpoint', 'overall_uptime',
          'threshold', 'ask_cold_spo', 'ask_warm_spo',
          'join_cold_ss', 'join_cold_so', 'join_cold_oo', 'join_warm_ss', 'join_warm_so', 'join_warm_oo']

    colm = np.append(v, ba)

    stats = pd.DataFrame(datasets.copy(), columns=colm)
    dstat = pd.DataFrame(stats, columns=["id", "name", "title", 'alt_name', 'publications', "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015"])

    return stats, dstat


def start():
    stats, dstats = get_datasets()
    with open('lod.txt', 'r') as f:
        lod_ds = json.load(f)

    dump_formats = ['rdf/turtle', 'tgz', 'text/rdf+n3', 'text/turtle', 'text/n3', 'gz:txt', 'JSON', 'HTML', 'rdf+xml',
                    'appliation/x-trig', 'XML', 'ZIP', 'URI', 'RDF', 'RDF/XML, Turtle, HTML', 'gzip:ntriples', 'CSV',
                    'WordNet', 'Turtle', 'application/marc', 'gzip::nquads', 'HTML/RDF','application/x-ntriples',
                    'application/x-bzip', 'RDFa', 'weblog', 'linked data', 'Linked Data', 'PDF', '-']
    for d in lod_ds:
        if not d['isopen']:
            continue
        dstat = stats[stats['id'] == d['id']]
        dstat['license_id'] = d['license_id']
        dstat['license_title'] = d['license_title']
        if 'license_url' in d:
            dstat['license_url'] = d['license_url']


        res = d['resources']

        endpoint = None
        endpoint_checked = False
        dump_availability_checked = False

        for r in res:
            if not dump_availability_checked and r['format'] in dump_formats:
                dstat['dump_availability'] = 1
                dump_availability_checked = True

            if not endpoint_checked and (r['format'] in ['api/sparql', 'SPARQL', 'sparql endpoint', 'SPARQL endpoint', 'api/query', 'RDF, SPARQL+XML'] or ('sparql' in r['url'] and r['format'] in ['RDF', ''])):
                endpoint = r['url']
                endpoint_checked = True

            if not endpoint_checked and ('sparql' in r['url'] and r['format'] not in ['api/sparql', 'SPARQL', 'sparql endpoint', 'SPARQL endpoint', 'api/query', 'RDF, SPARQL+XML']):
                if '?' in r['url']:
                    url = r['url']
                    l = url.find('?')
                    endpoint = url[:l]
                else:
                    endpoint = r['url']
                endpoint_checked = True

        dstat['created'] = d['metadata_created']
        dstat['sparql_endpoint'] = endpoint
        if endpoint is not None:
            res = sparqles(endpoint)
            uptimeOverall = extract_uptime(res)
            threshold, ask_cold_spo, ask_warm_spo = extract_ask_performance(res)
            threshold, join_cold_ss, join_cold_so, join_cold_oo, join_warm_ss, join_warm_so, join_warm_oo = extract_join_performance(res)

            dstat['overall_uptime'] = uptimeOverall
            dstat['threshold'] = threshold
            dstat['ask_cold_spo'] = ask_cold_spo
            dstat['ask_warm_spo'] = ask_warm_spo

            dstat['join_cold_ss'] = join_cold_ss
            dstat['join_cold_so'] = join_cold_so
            dstat['join_cold_oo'] = join_cold_oo
            dstat['join_warm_ss'] = join_warm_ss
            dstat['join_warm_so'] = join_warm_so
            dstat['join_warm_oo'] = join_warm_oo

        if not dump_availability_checked:
            dstat['dump_availability'] = 0

        stats.update(dstat)

    return stats
def analysis():
    with open('lod.txt', 'r') as f:
        lod_ds = json.load(f)
    voi = 0
    endp = 0
    endpoints = []
    dswithendpoints = {}
    licenseIDs = {}
    for d in lod_ds:
        if not d['isopen']:
            continue
        res = d['resources']
        if d['license_id'] not in licenseIDs:
            licenseIDs[d['license_id']] = d['license_title']

        if d['license_id'] not in ['other-open', 'other-at', 'other-pd']:
            print d['name'], d['license_id'], ' title: ', d['license_title']
            if 'license_url' in d:
                print 'url: ', d['license_url']
            print '-------------'
        for r in res:

            if 'void' in r['url'] or r['format'] in ['void', 'meta/void', 'rdf/void']:
                voi += 1

            endpoint = None
            if 'sparql' in r['url'] and r['format'] not in ['api/sparql', 'SPARQL', 'sparql endpoint', 'SPARQL endpoint', 'api/query', 'RDF, SPARQL+XML']:
                if '?' in r['url']:
                    url = r['url']
                    l = url.find('?')
                    if url[:l] not in endpoints:
                        endpoints.append(url[:l])
                        endpoint = url[:l]
                else:
                    if r['url'] not in endpoints:
                        endpoints.append(r['url'])
                        endpoint = r['url']
            if r['format'] in ['api/sparql', 'SPARQL', 'sparql endpoint', 'SPARQL endpoint', 'api/query', 'RDF, SPARQL+XML'] or ('sparql' in r['url'] and r['format'] in ['RDF', '']):
                endp += 1
                endpoint = r['url']
            if endpoint is not None:
                if d['name'] not in dswithendpoints:
                    dswithendpoints[d['name']] = endpoint
                #res = sparqles(endpoint)
                #extract_value(res)
                #break
    print 'void: ', voi, ' endpoints: ', (len(endpoints)+endp)
    i = 0
    for l in licenseIDs:
        i += 1
        print i, l, '-', licenseIDs[l]


def sparqles(endpoint):
    response = urllib2.urlopen('http://sparqles.ai.wu.ac.at/api/endpoint/info?uri=' + endpoint)
    r = response.read()
    response_dict = json.loads(r)

    return response_dict


def extract_uptime(res):
    for i in res:
        av = i['availability']
        uptimeOverall = av['uptimeOverall']

        return uptimeOverall


def extract_ask_performance(res):

    for i in res:
        per = i['performance']
        threshold = per['threshold']
        ask_cold_spo = 0
        ask_warm_spo = 0
        for ad in per['ask']:
            for a in ad['data']:
                if a['label'] == 'spo':
                    if ad['key'] == 'Cold ASK Tests':
                        ask_cold_spo = a['value']
                    elif ad['key'] == 'Warm ASK Tests':
                        ask_warm_spo = a['value']

        return threshold, ask_cold_spo, ask_warm_spo
    return 0, 0, 0

def extract_join_performance(res):
    for i in res:
        per = i['performance']
        threshold = per['threshold']
        join_cold_ss = 0
        join_cold_so = 0
        join_cold_oo = 0

        join_warm_ss = 0
        join_warm_so = 0
        join_warm_oo = 0

        for jd in per['join']:
            for j in jd['data']:

                if jd['key'] == 'Cold JOIN Tests':
                    if j['label'] == 'ss':
                        join_cold_ss = j['value']
                    elif j['label'] == 'so':
                        join_cold_so = j['value']
                    elif j['label'] == 'oo':
                        join_cold_oo = j['value']
                elif jd['key'] == "Warm JOIN Tests":
                    if j['label'] == 'ss':
                        join_warm_ss = j['value']
                    elif j['label'] == 'so':
                        join_warm_so = j['value']
                    elif j['label'] == 'oo':
                        join_warm_oo = j['value']
        return threshold, join_cold_ss, join_cold_so, join_cold_oo, join_warm_ss, join_warm_so, join_warm_oo
    return 0,0,0,0,0,0,0

if __name__=='__main__':

    reload(sys)
    sys.setdefaultencoding("utf8")

    stat = start()
    stat.to_pickle('results/quality_eval.pkl')
    stat.to_csv('results/quality_eval.csv')

    #stat = pd.read_pickle('results/quality_eval.pkl')
    '''
    for i, d in stat.iterrows():
        if not d['overall_uptime'] >= 0:
            print i, d['title']
            d.loc[i, 'overall_uptime'] = 0
            #d[i, 'overall_uptime'] = 0
            #stats.update(d)
    '''
    print stat[['title', 'sparql_endpoint', 'overall_uptime', 'threshold','dump_availability']]
