import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle

def fse_map(test, target):
    global fse_dataset
    for gui_event in test:
        if gui_event['id_or_xpath'][:3] == "id@":
            source_event = fse_dataset.loc[fse_dataset['original GUI event id'] == gui_event['id_or_xpath'][3:]]
        else:
            source_event = fse_dataset.loc[fse_dataset['original GUI event xpath'] == gui_event['id_or_xpath'][6:]]
        
        if source_event.shape[0] == 0: #search returns nothing
            gui_event['case'] = "notFound"
            gui_event['id_or_xpath'] = "NONE"
        else:
            source_prediction = source_event.iloc[0]['prediction canonical id']
            source_correct = source_event.iloc[0]['correct canonical id']
            if source_prediction == "NONE":
                gui_event['case'] = "missed"
                gui_event['id_or_xpath'] = "NONE"
            
            else:
                if source_prediction == source_correct:
                    gui_event['case'] = "correct"
                else:
                    gui_event['case'] = "incorrect"
                    
                target_event = fse_dataset.loc[(fse_dataset['prediction canonical id'] == source_prediction) & (fse_dataset['app'] == target)]
                if target_event.shape[0] == 0: #search returns nothing
                    gui_event['case'] = "notFound"
                    gui_event['id_or_xpath'] = "NONE"
                else:
                    target_prediction = target_event.iloc[0]['prediction canonical id']
                    target_correct = target_event.iloc[0]['correct canonical id']
                    if pd.isnull(target_correct):
                        gui_event['case'] = "incorrect"
                        gui_event['id_or_xpath'] = "NONE"
                    else:
                        if target_prediction != target_correct:
                            gui_event['case'] = "incorrect"
                        if pd.isnull(target_event.iloc[0]['original GUI event id']):
                            gui_event['id_or_xpath'] = "xpath@" + target_event.iloc[0]['original GUI event xpath']
                        else:
                            gui_event['id_or_xpath'] = "id@" + target_event.iloc[0]['original GUI event id']
    return test

if __name__ == "__main__":
    fse_dataset = read_csv("prediction_widget_results.csv")
    
    fse_names = [str.lower(os.path.splitext(os.path.basename(file))[0]) for file in glob.glob("../src/test_csv/*.csv")]
    fse_names = {e:e for e in fse_names}
    fse_names['sixpm'] = "6:00 PM"
    fse_names['fivemiles'] = "5miles"
    fse_names['googleexpress'] = "googleexp"
    
    for source_path in glob.glob("../src/test_csv/*.csv"):
        source_csv = read_csv(source_path, names=["method", "json"])
        source_csv['json'] = source_csv['json'].apply(json.loads)
        
        for target_path in glob.glob("../src/test_csv/*.csv"):
            if source_path != target_path:
                target_csv = pickle.loads(pickle.dumps(source_csv)) #deep copy
                target_name = fse_names[str.lower(os.path.splitext(os.path.basename(target_path))[0])]
                target_csv['json'] = target_csv['json'].apply(fse_map, args=(target_name,))

                target_csv['json'] = target_csv['json'].apply(json.dumps)
                target_csv.to_csv("fse_out/" + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(target_path), index=False)
                print(source_path, target_path)
