__author__ = 'kemele'

import json
import sys
import re
import os
import pprint
import pandas as pd

'''
Publication text processing
'''
def getVenueYear (filename):
    venue = re.finditer("^([A-Z]*)", filename.upper())
    year = re.finditer("[0-9]{4}", filename)
    for v in venue:
        venue = v.group()
        break
    for y in year:
        year = y.group()
        break
    return venue, year


def getListOfFiles(loc):
    if os.path.exists(loc) and os.path.isdir(loc):
        dirs = os.listdir(loc)
        return [d for d in dirs if d[-1] is not "~"]
    else:
        return []


def readText (path, name):
    if os.path.isdir(path):
        loc = os.path.join(path, name)
        with open(loc) as inFile:
            text = inFile.read()
            #text = re.sub(r"[^\\P{Cc}\\P{Cf}\\P{Co}\\P{Cs}\\P{Cn}\\s]", "", text)
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
            text = text.replace("[^\\P{Cc}\\P{Cf}\\P{Co}\\P{Cs}\\P{Cn}\\s]", "")
            return text
    else:
        return ""


def getHeadings(text):
    pat = r"(\n|\r)+[1-9]\.{0,1}\s{1,3}[A-Z](\w{1,15}[\-:_~!@#$%^&*\(\)=+><\?\|\}\{\[\];'\"`,/\.]{0,4}[^\x00-\x7F]{0,3}[ \t]{0,3}){5,12}(\n|\r)"
    headings = re.finditer(pat, text)
    hs = []
    for h in headings:
        hs.append(h.group())
    heading = [h for h in hs if len(h) > 0 and isProperHeading(h)]
    return heading


def cleanUpHeadings(headings, text):

    heading =[]
    resolved = []
    nums = [a.strip()[0] for a in headings]
    prevValidLoc = -1
    index = 0
    for h in headings:
        oc = [a for a in headings if a.strip()[0] == h.strip()[0]]
        if len(oc) > 1:
            if h not in resolved:
                selectedLoc = text.find(h)
                selectedH = h

                print "duplicates:"
                nextH = headings[index+1]
                i =0
                while nextH in oc:
                    i += 1
                    if len(headings) <= index + i:
                        break
                    nextH = headings[index + i]
                nextLoc = text.find(nextH)

                if nextH.replace('\n', '').strip()[0] < h.replace('\n', '').strip()[0]:
                    nextLoc = len(text)

                for o in oc:
                    loc = text.find(o)
                    if loc > prevValidLoc and loc < nextLoc:
                        if selectedLoc > prevValidLoc and selectedLoc < nextLoc:
                            if loc > selectedLoc:
                                selectedLoc = loc
                                selectedH =o
                        else:
                            selectedLoc = loc
                            selectedH = o
                    resolved.append(o)
                heading.append(selectedH)
                if nextLoc > selectedLoc:
                    prevValidLoc = selectedLoc
        else:
            heading.append(h)
            prevValidLoc = text.find(h)
        index += 1
    return heading


def isProperHeading(h):
    stopword = ['the', 'a', 'and', 'of', 'an', 'to']
    words = h.replace('\n', '').split(' ')
    for w in words:
        w = w.strip()
        if len(w) == 0 or w in stopword:
            continue

        df = False
        for i, c in enumerate(w.strip()):
            if c.isdigit():
                df = True
                break
        if df:
            continue
        if not w[0].isupper():
            return False
    return True


def separateFromAbstractToReferences(text):
    rest, references, appe = getSparateReferences(text)
    loc = getAbstractLoc(rest)
    if loc > 0:
        rest = rest[loc:]
    return rest, references, appe

def getAbstractLoc(text):
    loc = text.find('\nAbstract')
    return loc


def getSparateReferences(text):
    loc = getloc(text)
    bloc=loc
    aloc = loc
    if loc < 0:
        loc = getloc(text, "Bibliography")
        aloc = loc
    if bloc != aloc:
        print bloc, aloc, text.splitlines()[0]
    appat = re.finditer("\n(\d|[A-Z]){0,4}\.{0,1}\s{0,3}Appendix", text[loc:], re.IGNORECASE)
    endpos = len(text)

    for a in appat:
        g = a.group()
        lg = text.find(g)
        if lg > 0 and lg > loc:
            endpos = lg
            break

    ref = text[loc:endpos]
    rest = text[:loc]
    appe = text[endpos:]
    references = cleanUpReferences(ref)
    return rest, references, appe


def cleanUpReferences(references):
    text = ""
    line = ""
    refStarted = False
    refFound = False
    pat ="^(\[{0,1}\d+\]{0,1}\w+)"
    for l in references.splitlines():
        if len(l.strip()) == 0:
            continue
        if refFound is False:
            if 'references' in l.lower() or 'bibliography' in l.lower():
                text += 'References\n'
                refFound = True
            continue
        if not refStarted:
            reg = re.finditer("^(\[{0,1}[1]\]{0,1})", l)
            v = False
            for r in reg:
                refStarted = True
                line = l
                if l.find("[1") > -1:
                    pat ="^(\[\d{1,3}\]\s*\w+)"
                else:
                    pat = "^(\d{1,3})\.*\s*\w+"
                v = True
            if not v:
                text += l +'\n'
        else:
            reg = re.finditer(pat, l)
            v = False
            for r in reg:
                text += line + "\n"
                line = l
                v = True
            if not v:
                line += l +" "

    return text

def getAllURLs(text):
    patFootNote = "\d+[^\<](ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?"
    patAll = "(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\/\-\/]))?"
    sobj = re.finditer(patAll, text)
    if sobj:
        values = [s.group().strip() for s in sobj]
        return values
    else:
        return []


def getloc(text, ref='References'):

    loc = text.rfind('\n' + ref + '\n')
    pat = "\n(\d|[A-Z]){0,7}\.{0,1}\s{0,3}" + ref + "\s*\n"
    locitr = re.finditer(pat, text, re.IGNORECASE)
    for l in locitr:
        g = l.group()

        lg = text.rfind(g)

        if lg > 0:
            loc = lg
            break
    return loc


def separateEvaluations(text):
    headings = getHeadings(text)
    evalLoc = 0
    concLoc = 0
    relworkLoc = 0
    for h in headings:
        if "Experiment" in h or  "Evaluat" in h or "Result" in h:
            if evalLoc == 0:
                evalLoc = text.find(h)
        if "related work" in h.lower():
            if relworkLoc == 0:
                relworkLoc = text.find(h)
        if "Conclusion" in h or "Conclu" in h:
            concLoc  = text.find(h)
    if evalLoc > 0:

        if relworkLoc > 0 and relworkLoc > evalLoc:
            if concLoc > 0 and relworkLoc != concLoc:
                return text[:evalLoc] + text[relworkLoc:concLoc], text[evalLoc:relworkLoc], text[concLoc:]
            else:
                return text[:evalLoc] + text[relworkLoc:], text[evalLoc:relworkLoc], text[relworkLoc:]
        if concLoc > 0:
            return text[:evalLoc], text[evalLoc:concLoc], text[concLoc:]
        else:
            return text[:evalLoc], text[evalLoc:], ""
    else:
        '''
        if concLoc > 0:
            return text[:concLoc], text[evalLoc:], text[concLoc:]
        else:
            return text, text, text[relworkLoc:]
        '''
        return "", "", ""


def csv_to_pickle(csvFile, pickleFile):
    datasets = pd.read_csv(csvFile)
    datasets.to_pickle(pickleFile +".pkl")
    return datasets


'''
 =====================================
 dataset dictionary processing
 =====================================
'''

'''
loads lod dataset metadata from json file
'''


def load_dataset_json_file(path):
    with open(path, 'r') as f:
        lod_ds = json.load(f)
        return lod_ds


'''
loads dataset dictionary from csv file
'''


def load_dataset_dict(fname):
    ds = pd.read_csv(fname)
    data = pd.DataFrame(ds, columns=["id", "ds_name", "title", "alt_name", "url", "res_url", "publications"])
    return data


'''
 convert json data to two dictionaries, dataset and resources dictionary
'''


def to_dict(lod_all, dataset_header, name=None):
    data = {}


    for d in lod_all:
        header = d
        if name is not None and name in ['resources', 'extras', 'tags']:
            for r in d[name]:
                for t in dataset_header:
                    if t == 'ds_id':
                        value = d['id']
                    else:
                        if t in r:
                            value = r[t]
                        else:
                            value = None
                    if t in data:
                        data[t].append(value)
                    else:
                        data[t] = [value]
        else:
            if name is 'organization':
                header = d[name]
            for t in dataset_header:
                if t == 'ds_id':
                    value = d['id']
                else:
                    if t in header:
                        value = header[t]
                    else:
                        value = None
                if t in data:
                    data[t].append(value)
                else:
                    data[t] = [value]

    return data


def to_dicts(lod_all, dataset_header, resource_header):
    data = {}
    res = {}
    for d in lod_all:
        #dataset metadata
        for t in dataset_header:
            value = d[t]
            if data.has_key(t):
                if t == 'tags':
                    tags = get_tags(value)
                    data[t].append(tags)
                else:
                    data[t].append(value)
            else:
                if t == 'tags':
                    tags = get_tags(value)
                    data[t] = [tags]
                else:
                    data[t] = [value]
        # resources list metadata for this dataset
        resources = d["resources"]
        for r in resources:
            for t in resource_header:
                if t == 'res_id':
                    value = r['id']
                elif t == 'id':
                    value = d['id']
                elif t == 'res_state':
                    value = r['state']
                elif t == 'res_url':
                    value = r['url']
                else:
                    if t not in r:
                        value = None
                    else:
                        value = r[t]
                if res.has_key(t):
                    res[t].append(value)
                else:
                    res[t] = [value]
    return data, res


'''
 extracts tags (display_name) from json object and returns a list of tags separated by '|'
'''


def get_tags(value):
    tags = ""
    for n in value:
        if len(tags) == 0:
            tags = n['display_name']
        else:
            tags = tags + "|"+ n['display_name']
    return tags


'''
 convert dataset and resource dict to pandas DataFrame
'''


def to_DataFrame(data, res, dataset_header=None, resource_header=None):
    if dataset_header is None:
        datasets = pd.DataFrame(data)
    else:
        datasets = pd.DataFrame(data, columns=dataset_header)
    if resource_header is None:
        resources = pd.DataFrame(res)
    else:
        resources = pd.DataFrame(res, columns=resource_header)

    return datasets, resources


'''
  appends resources url to res_url column of dataset dictionary (DataFrame)
'''


def appendResourceUrls(datasets, resources):
    datasets['res_url'] = ""
    for i, d in datasets.iterrows():
        val = get_ress(resources, d)
        url = ""
        for v in val:
            if len(url) > 0:
                url = url + "|" + v
            else:
                url = v
        dd = datasets[datasets['id'] == d["id"]]
        dd['res_url'] = url
        datasets.update(dd)

    return datasets


def get_ress(resources, d):
    res = resources[resources['id'] == d['id']]
    res = res.copy()
    return res['res_url']


def getBasicColumns(datasets, resources):

    r = appendResourceUrls(datasets, resources)
    # d = r[r['isopen']==True]
    ds = r[["id", "name", "title", "url", "res_url"]]

    return ds


'''
 returns dataset dictionary with selected column names from json represented lod datasets metadata
'''

def getDatasets(fname=None):
    if fname is not None:
        lod_ds = load_dataset_json_file(fname)
    else:
        lod_ds = load_dataset_json_file("lod.txt")

    dataset_header = ['id', 'name', 'title', 'url', 'version', 'type', 'notes', 'num_resources', 'tags', 'isopen',
                      'state', 'metadata_created', 'metadata_modified', 'license_id', 'license_title']
    resource_header = ['id', 'res_id', 'description', 'created', 'last_modified', 'format', 'mimetype',
                       'mimetype_inner', 'size', 'res_state', 'res_url', 'url_type', 'webstore_url',
                       'webstore_last_updated']

    data, res = to_dict(lod_ds, dataset_header, resource_header)
    datasets, resources = to_DataFrame(data, res)
    bds = getBasicColumns(datasets, resources)

    return bds


def process_metadata(fname=None, out_folder="dataset_metadata"):
    if fname is not None:
        lod_ds = load_dataset_json_file(fname)
    else:
        lod_ds = load_dataset_json_file("lod.txt")

    dataset_header = ['id', 'name', 'title', 'url', 'version', 'type', 'notes', 'num_resources', 'num_tags', 'isopen',
                      'private', 'state', 'metadata_created', 'metadata_modified', 'license_id', 'license_title',
                      'license_url', 'owner_org', 'revision_id', 'maintainer', 'maintainer_email', 'author',
                      'author_email']
    resource_header = ['id', 'ds_id', 'name', 'description', 'created', 'last_modified', 'format', 'mimetype', 'mimetype_inner',
                       'size', 'state', 'url', 'url_type', 'webstore_url','webstore_last_updated', 'cache_url',
                       'cache_last_updated', 'hash', 'resource_type']
    organization_header = ['id', 'name', 'title', 'state', 'is_organization', 'description', 'created', 'approval_status', 'image_url', 'type', 'revision_id']
    tags_header = ['id', 'ds_id', 'display_name', 'name', 'state', 'vocabulary_id']
    extras_header = ['ds_id', 'key', 'value']

    dsbasic_dict = to_dict(lod_ds, dataset_header)
    resources_dict = to_dict(lod_ds, resource_header, 'resources')

    orgs_dict = to_dict(lod_ds, organization_header, 'organization')
    tags_dict = to_dict(lod_ds, tags_header, 'tags')
    extras_dict = to_dict(lod_ds, extras_header, 'extras')

    datasets = pd.DataFrame(dsbasic_dict)
    resources = pd.DataFrame(resources_dict)
    print resources.head()
    orgs = pd.DataFrame(orgs_dict)
    tags = pd.DataFrame(tags_dict)
    extras = pd.DataFrame(extras_dict)

    if not os.path.exists(out_folder):
        os.makedirs(out_folder +'/pkls')
        os.makedirs(out_folder +'/csvs')

    datasets.to_pickle(out_folder+'/pkls/dataset_basic.pkl')
    datasets.to_csv(out_folder+'/csvs/dataset_basic.csv')

    resources.to_pickle(out_folder+'/pkls/resources.pkl')
    resources.to_csv(out_folder+'/csvs/resources.csv')

    orgs.to_pickle(out_folder+'/pkls/organizations.pkl')
    orgs.to_csv(out_folder+'/csvs/organizations.csv')

    tags.to_pickle(out_folder+'/pkls/tags.pkl')
    tags.to_csv(out_folder+'/csvs/tags.csv')

    extras.to_pickle(out_folder+'/pkls/extras.pkl')
    extras.to_csv(out_folder+'/csvs/extras.csv')

    return datasets, resources, orgs, tags, extras


def get_dataset_metadata(folder_name="dataset_metadata"):
    if not os.path.exists(folder_name +'/pkls'):
        return None, None, None, None, None
    datasets = pd.read_pickle(folder_name +'/pkls/dataset_basic.pkl')
    resources = pd.read_pickle(folder_name +'/pkls/resources.pkl')
    orgs = pd.read_pickle(folder_name +'/pkls/organizations.pkl')
    tags = pd.read_pickle(folder_name +'/pkls/tags.pkl')
    extras = pd.read_pickle(folder_name +'/pkls/extras.pkl')

    return datasets, resources, orgs, tags, extras


if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding("utf8")
    # process_metadata()

    datasets, resources, orgs, tags, extras = get_dataset_metadata()
    print resources[resources['created'] == '2016-02-04T11:35:18.024229']
