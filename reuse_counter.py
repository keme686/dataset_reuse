__author__ = 'kemele'

import sys
import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import utils


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
                         columns=["id", "ds_name", "title", 'alt_name', 'url', 'res_url', 'publications',  # 'license_id', 'license_url', 'license_title'
                                  "2007", "2008", "2009", "2010",
                                  "2011", "2012", "2013", "2014", "2015"])

    return stats, dstat


def doAdvAnalysis(loc="publications_txt", usage=True, fname="results/publications/usages/usage_results.csv"):
    stats, dstat = getPdDs()
    folders = utils.getListOfFiles(loc)
    dstat['papers'] = ""
    dstat['total'] = 0
    count = 0
    totalCount = 0
    for f in folders:
        path = loc + "/" + f
        papersList = utils.getListOfFiles(path)
        v, y = utils.getVenueYear(f)

        for p in papersList:
            print "................................................."
            print p
            print "................................."
            if os.path.isdir(os.path.join(path, p)) or "SPARQL Query Answering over OWL Ontologies" in p:
                continue
            text = utils.readText(path, p)
            print "<<<<<<<<<<<<<<< read >>>>>>>>>>>>>"
            txt, references, appendix = utils.separateFromAbstractToReferences(text)  # tp.getSparateReferences(text)
            print "<<<<<<<<<<<<<<< ref >>>>>>>>>>>>>"
            if usage:
                first, txt, conc = utils.separateEvaluations(txt)
            print "<<<<<<<<<<<<<<< Separated >>>>>>>>>>>>>"
            totalCount += 1
            found = False
            print txt
            for k, d in stats.iterrows():
                foundInTxt = isPhraseMentioned(d["title"], txt)
                foundInAlt = False

                isInAmbg = False
                ambgNamges = ['UniProt', 'Ocean Drilling', 'OpenUpLabs', 'EnAKTing', 'Eagle-i', 'ChEMBL',
                              'Cell line ontology', 'Europeana', 'Eurostat', 'Library of congress subject headings',
                              'Open Data Communities',
                              'Entrez Gene', 'MeSH', 'oboe', 'olia', 'medline', 'VIVO', 'Instance Hub',
                              'Linked Geo Data', 'dbpedia', 'thesaurus', 'WordNet', 'biomodels', 'Reactome',
                              'WorldBank', 'UIS', "IMF", "FAO", 'FRB', 'ECB', 'BFS', 'BIS', 'ABS']

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
                    foundInDatahub = dhburl.lower() in txt.lower()

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
                            foundInReff = isPhraseMentioned(pt, references)
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
                    dd[y + ""] += 1
                    dd['papers'] += os.path.join(f, p) + "|=|"
                    total = dd["2007"] + dd["2008"] + dd["2009"] + dd["2010"] + dd["2011"] + dd["2012"] + dd["2013"] + dd["2014"] + dd["2015"]
                    dd['total'] = total
                    dstat.update(dd)
                    found = True
            if found:
                count += 1
            print "Total papers we found dataset mentions in exp: ", count
            print "Total count: ", totalCount

    #dstat.sort(columns=["2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015"])
    #dstat.to_csv(fname)
    #dstat.to_pickle(fname+".pkl")
    print "Total papers we found dataset mentions in exp: ", count
    print "Total count: ", totalCount
    return dstat


def fromCsv(fname="results/publications/usages/usage_results.csv"):
    dst = pd.read_csv(fname)
    return dst


def draw_results(dst, filepath="results/publications/usages"):

    prefix = 'inbt'
    splits = [1e6, 50, 40, 30, 20, 10, 5, 1]
    secplits = splits[1:]
    print zip(splits[:-1], secplits)
    for x, y in zip(splits[:-1], secplits):
        #dst = dst[dst['res_url'] != 'http://www.bioontology.org/wiki/index.php/BioPortal_REST_services|http://sparql.bioontology.org/|http://rest.bioontology.org/bioportal/ontologies/download/47017?apikey=BP_API_KEY']
        sds = dst[dst["2007"] + dst["2008"] + dst["2009"] + dst["2010"] + dst["2011"] + dst["2012"] + dst["2013"] + dst["2014"] + dst["2015"] < x]
        sds = sds[sds["2007"] + sds["2008"] + sds["2009"] + sds["2010"] + sds["2011"] + sds["2012"] + sds["2013"] + sds["2014"] + sds["2015"] >= y]
        if sds is None or len(sds) <= 0:
            print "nothing to show", x, y
            continue
        dd = sds[['title', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
        sds = sds[['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
        td = sds.T

        td.columns = dd['title']
        p = td.plot(kind='bar',  figsize=(25, 20), fontsize=24)
        plt.savefig(filepath+"/%s%d-%d.png" % (prefix, x, y))


def analyze():
    dst = doAdvAnalysis(usage=True, fname="results/publications/usages/usages_results.csv")  # pd.read_pickle("results/usages/usage_results.csv.pkl")  #
    draw_results(dst, filepath="results/publications/usages")
    print dst


def analyze_from_file(fname="results/publications/usages/usage_results.csv"):
    dst = fromCsv(fname)
    #print dst
    #draw_results(dst)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf8")
    #total papers mentions found = 718
    # usages = 256
        # Query-Independent Learning to Rank for RDF Entity Search , DBpedia, Yago, semanticweb.org
        # EAGLE: Eﬃcient Active Learning of Link Speciﬁcations Using GeneticProgramming: DailyMed, Drugbank, LinkedMDB, ACM-DBLP >> DailyMed and Drugbank no reference/links
    analyze()
