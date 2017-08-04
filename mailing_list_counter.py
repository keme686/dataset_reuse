__author__ = 'kemele'


import json
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utils

def loadForum(fname="mailing_lists/sem-w3.json"):
    with open(fname, 'rb') as f:
        lod_w3 = json.load(f)
        return lod_w3


def isPhraseMentioned(phrase, text):
    commonWords = ['tip', 'near', 'simple', 'core', 'abs', 'uis', 'units of measurement', 'serendipity', 'this',
                   'knowledge map']
    if phrase.lower() in commonWords:
        return False
    if phrase.lower() == "mond":
        v = ' ' + phrase in text or '\n' + phrase in text
    else:
        v = phrase.lower() in text.lower()

    return v


def isUrlMentioned(url, text):
    # urls = tp.getAllURLs(text)
    v = False
    if url > 0:
        v = url in text
    return v


def inBound(d):
    return int(d) > 2006 and int(d) < 2016


def getPdDs(pkl_path="dataset_dictionary.pkl"):  # datasets_dict2.pkl
    datasets = pd.read_pickle(pkl_path)
    stats = pd.DataFrame(datasets.copy())
    stats["2007"] = 0
    stats["2008"] = 0
    stats["2009"] = 0
    stats["2010"] = 0
    stats["2011"] = 0
    stats["2012"] = 0
    stats["2013"] = 0
    stats["2014"] = 0
    stats["2015"] = 0
    stats['total'] = 0
    dstat = pd.DataFrame(stats,
                         columns=["id", "ds_name", "title", 'alt_name', 'publications', "2007", "2008", "2009", "2010",
                                  "2011", "2012", "2013", "2014", "2015", "total"])

    return stats, dstat


# 1 = per-thread, 2= main_only, 3 =answer_only
def doStats(lod_w3, part=1):
    print 'loading dataset dictionary'
    stats, dstat = getPdDs()
    print 'dataset dictionary loaded'
    dstat['threads'] = ""
    dstat['year'] = ""
    count = 0
    totalcount = 0
    for f in lod_w3:
        print f['title'], f['date'][:4]
        if not inBound(f['date'][:4]):
            continue
        totalcount += 1
        txt = ""
        if part == 1:  # main_only OR per_thread
            txt = f['title'] + " \n " + f['body']

        if part != 2 and len(f['answers']) > 0:  # per_thread or answer_only
            for t in f['answers']:
                txt += " \n " + t['body']
        print 'checking mentions ...'
        dstat, found = check_mention(stats, dstat, txt, f)
        if found:
            count += 1
        print 'chekced ..'
    print "total found count: ", count
    print "total threads: ", totalcount

    dstat.to_csv("results/sem_w3/per_thread/sem_usage_results_per_thread.csv")

    return dstat


def check_mention(stats, dstat, txt, f):
    found = False
    for k, d in stats.iterrows():
        foundInTxt = isPhraseMentioned(d["title"], txt)
        foundInAlt = False
        isInAmbg = False
        ambgNamges = ['UniProt', 'Ocean Drilling', 'OpenUpLabs', 'EnAKTing', 'Eagle-i', 'ChEMBL', 'Cell line ontology', 'Europeana', 'Eurostat', 'Library of congress subject headings', 'Open Data Communities',
                      'Entrez Gene', 'MeSH', 'oboe', 'olia', 'medline', 'VIVO', 'Instance Hub', 'Linked Geo Data', 'dbpedia', 'thesaurus', 'WordNet', 'biomodels', 'Reactome',
                      'WorldBank', 'UIS', "IMF", "FAO", 'FRB', 'ECB','BFS', 'BIS', 'ABS']

        if d["alt_name"] > 0:
            if d['alt_name'] in ambgNamges:
                isInAmbg = True

            foundInAlt = isPhraseMentioned(d["alt_name"], txt)

            if foundInAlt and "Bio2RDF" in d['title']:
                foundInAlt = isPhraseMentioned("Bio2RDF", txt)

        foundInUrls = isUrlMentioned(d['url'], txt)

        foundInResUrls = False
        if d['res_url'] > 0:
            for url in d['res_url'].split("|"):
                foundInResUrls = isUrlMentioned(url, txt)
                if foundInResUrls:
                    break

        foundInDatahub = False
        if d['ds_name'] > 0:
            dhburl = "datahub.io/dataset/" + d['ds_name']
            ckburl = "ckan.net/dataset/" + d['ds_name']
            zdhburl = "thedatahub.org/dataset/" + d['ds_name']
            foundInDatahub = dhburl.lower() in txt.lower() or ckburl.lower() in txt.lower() or zdhburl.lower() in txt.lower()

        foundInReff = False
        if d["publications"] > 0:
            for pub in d['publications'].splitlines():
                if len(pub) == 0:
                    continue
                reob = re.finditer('"(.*?)"', pub)
                ptitles = []
                for o in reob:
                    ptitles.append(o.group()[1:-1])
                for pt in ptitles:
                    foundInReff = isPhraseMentioned(pt, txt)
                    if foundInReff:
                        break
                if foundInReff:
                        break
        shouldUpdate = False
        if isInAmbg and foundInAlt:
            if foundInUrls or foundInResUrls or foundInReff or foundInDatahub:
                shouldUpdate = True
        elif foundInTxt or foundInAlt or foundInUrls or foundInResUrls or foundInReff or foundInDatahub:
            shouldUpdate = True

        if shouldUpdate and len(dstat[dstat['id'] == d['id']]) > 0:
            dd = dstat[dstat['id'] == d['id']]
            dd[f['date'][:4]+""] += 1
            dd['threads'] += f['title'] + "~" + f['from'] + "~" + f['date'] + "|=|\t"
            total = dd["2007"] + dd["2008"] + dd["2009"] + dd["2010"] + dd["2011"] + dd["2012"] + dd["2013"] + dd["2014"] + dd["2015"]
            dd['total'] = total
            dd['year'] = f['date'][:4]
            dstat.update(dd)
            found = True

    return dstat, found


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf8")
    forum = loadForum("mailing_lists/sem-w3.json")
    print 'forum loaded'
    dst =doStats(forum, 1)  # pd.read_csv("results/lod_w3/per_thread/lod_usage_results_per_thread.csv")  #
    print 'stats finished'
    prefix = 'tbt'
    splits = [1e6,50,40,30,20,10,5,1]
    secplits = splits[1:]
    print zip(splits[:-1], secplits)
    for x, y in zip(splits[:-1], secplits):
        sds = dst[dst["2007"] + dst["2008"] + dst["2009"] + dst["2010"] + dst["2011"] + dst["2012"] + dst["2013"] + dst["2014"] + dst["2015"] < x]
        sds = sds[sds["2007"] + sds["2008"] + sds["2009"] + sds["2010"] + sds["2011"] + sds["2012"] + sds["2013"] + sds["2014"] + sds["2015"] >= y]
        if sds is None or len(sds) <= 0:
            print "nothing to show", x, y
            continue
        dd = sds[['title', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
        sds = sds[['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
        td = sds.T

        td.columns = dd['title']

        p = td.plot(kind='bar',  figsize=(25, 20), fontsize=24, legend=True)
        plt.savefig("results/sem_w3/per_thread/%s%d-%d.png" % (prefix, x, y))
