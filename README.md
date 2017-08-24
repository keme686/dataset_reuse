# Dataset reuse analysis
Code repository to analyse indications of dataset reuse in different communication channels including mailing lists and publications.

# Data
## Dataset dictionary 
`dataset_dictionary.csv` file contains a detailed metadata of datasets from datahub.com

## Dataset metadata
`dataset_metadata` contains metadata of datasets extracted from datahub.com, separated to different files: basic info, extras, resources, tags and organization. 

## Mailing lists
`mailing_lists` contains json dumps of mailing lists: e.g., semantic-web@w3.org (`sem-w3.json`) and public-lod@w3.org (`lod-w3.json`).

## Publications (papers)
`publication_txt` contains textual (.txt) forms of papers from three well known conferences: ISWC, ESWC and WWW. The publication texts should be placed in a folder named `Conf+Year`: e.g., `ESWC2013` for papers from ESWC 2013 conference).

# Scripts
## Dataset reuse in publications
`reuse_counter.py` analyzes dataset reuse (mentions) in different parts of articles. 
## Dataset reuse in mailing lists
`mailinig_list_counter.py` analyzes dataset reuse (mentions) in mailing lists.
