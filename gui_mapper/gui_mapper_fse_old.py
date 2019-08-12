import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv

def gui_map(test):
    global fse_dataset
    for gui_event in test:
        if gui_event['id_or_xpath'][:3] == "id@":
            search = fse_dataset.loc[fse_dataset['original GUI event id'] == gui_event['id_or_xpath'][3:]]
        else:
            search = fse_dataset.loc[fse_dataset['original GUI event xpath'] == gui_event['id_or_xpath'][6:]]
        
        if search.shape[0] == 0: #search returns nothing
            gui_event['case'] = "notFound"
        else:
            prediction = search.iloc[0]['prediction']
            correct = search.iloc[0]['correct']
            if prediction != "NONE":
                if prediction == correct:
                    gui_event['case'] = "correct"
                else:
                    gui_event['case'] = "incorrect"
            else:
                if correct != "NONE":
                    gui_event['case'] = "missed"
                else:
                    gui_event['case'] = "nonExist"
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
    fse_dataset = read_csv("prediction_widget_results.csv")
    
    for source_path in glob.glob("../src/test_csv/*.csv"):
        source_csv = read_csv(source_path, names=["method", "json"])
        source_csv['json'] = source_csv['json'].apply(json.loads)
        source_csv['json'] = source_csv['json'].apply(gui_map)

        output_csv = pd.concat([source_csv, source_csv['json'].apply(list_cases).apply(pd.Series)], axis=1)
        output_csv = pd.concat([output_csv, output_csv.apply(count_cases, axis=1).apply(pd.Series)], axis=1)

        output_csv['json'] = output_csv['json'].apply(json.dumps)
        output_csv.to_csv("fse_out/" + os.path.basename(source_path), index=False)
