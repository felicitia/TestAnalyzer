import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle

def craftdroid_map(test, mapping):
    global i
    for gui_event in test:
        if 'id_or_xpath' in gui_event:
            try:
                if gui_event['id_or_xpath'][:3] == "id@":
                    event_row = mapping.loc[mapping['source resource id'] == gui_event['id_or_xpath'][3:]]
                else:
                    event_row = mapping.loc[mapping['target xpath'] == gui_event['id_or_xpath'][6:]]
                if event_row.shape[0] != 0:
                    if pd.isnull(event_row.iloc[0]['target resource id']):
                        if pd.isnull(event_row.iloc[0]['target xpath']):
                            gui_event['id_or_xpath'] = "NONE"
                        else:
                            gui_event['id_or_xpath'] = "xpath@" + event_row.iloc[0]['target xpath']
                    else:
                        gui_event['id_or_xpath'] = "id@" + event_row.iloc[0]['target resource id']
                else:
                    gui_event['id_or_xpath'] = "NONE"
                    i += 1
            except TypeError:
                gui_event['id_or_xpath'] = "NONE_SOURCE"
                i += 1
            
        else:
            print(gui_event)
    return test

if __name__ == "__main__":
    for source_path in glob.glob("../src/test_csv/craftdroid/*.csv"):
        source_csv = read_csv(source_path, names=["method", "json"])
        source_csv['json'] = source_csv['json'].apply(json.loads)

        for target_path in glob.glob("../src/test_csv/craftdroid/*.csv"):
            if source_path != target_path:
                mapping = read_csv("craftdroid/CraftDroid Transfer Results - " + os.path.splitext(os.path.basename(source_path))[0] + "-" + os.path.basename(target_path))

                target_csv = pickle.loads(pickle.dumps(source_csv)) #deep copy
                i=0
                target_csv['json'] = target_csv['json'].apply(craftdroid_map, args=(mapping,))
                print(source_path, target_path, i)

                target_csv['json'] = target_csv['json'].apply(json.dumps)
                target_csv.to_csv("craftdroid_out/" + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(target_path), index=False)
