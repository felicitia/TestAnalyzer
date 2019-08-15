import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv

def generate_result(test):
    for gui_event in test:
        if gui_event['id_or_xpath'] == "NONE":
            gui_event['case'] = "nonExist"
        else:
            gui_event['case'] = "correct"
    return test

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
    for path in glob.glob("perfect_out/*.csv"):
        perfect_csv = read_csv(path)
        perfect_csv['json'] = perfect_csv['json'].apply(json.loads)
        perfect_csv['json'] = perfect_csv['json'].apply(generate_result)
        perfect_csv = pd.concat([perfect_csv, perfect_csv['json'].apply(list_cases).apply(pd.Series)], axis=1)
        perfect_csv = pd.concat([perfect_csv, perfect_csv.apply(count_cases, axis=1).apply(pd.Series)], axis=1)
        perfect_csv['json'] = perfect_csv['json'].apply(json.dumps)
        perfect_csv.to_csv("perfect_results/" + os.path.basename(path), index=False)
        print(path)
        