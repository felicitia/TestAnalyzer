import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv

def list_cases(test):
    cases = {'correct' : [], 'incorrect' : [], 'missed' : [], 'nonExist' : [], 'notFound' : []}
    for gui_event in test:
        cases[gui_event['case']].append(gui_event['id_or_xpath'])
    return cases

def count_cases(test):
    cases = {}
    cases['# correct'] = len(test['correct'])
    cases['# incorrect'] = len(test['incorrect'])
    cases['# missed'] = len(test['missed'])
    cases['# nonExist'] = len(test['nonExist'])
    cases['# notFound'] = len(test['notFound'])
    return cases

if __name__ == "__main__":
    for path in glob.glob("fse_out/*.csv"):
        fse_csv = read_csv(path)
        fse_csv['json'] = fse_csv['json'].apply(json.loads)
        fse_csv = pd.concat([fse_csv, fse_csv['json'].apply(list_cases).apply(pd.Series)], axis=1)
        fse_csv = pd.concat([fse_csv, fse_csv.apply(count_cases, axis=1).apply(pd.Series)], axis=1)
        fse_csv['json'] = fse_csv['json'].apply(json.dumps)
        fse_csv.to_csv("fse_results/" + os.path.basename(path), index=False)
        print(path)
