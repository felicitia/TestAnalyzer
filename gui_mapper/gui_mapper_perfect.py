import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle

def perfect_map(test, ground_truth_source, ground_truth_target):
    global i
    for gui_event in test:
        if 'id_or_xpath' in gui_event:
            if gui_event['id_or_xpath'][:3] == "id@":
                source_event = ground_truth_source.loc[ground_truth_source['id'] == gui_event['id_or_xpath'][3:]]
            else:
                source_event = ground_truth_source.loc[ground_truth_source['xpath'] == gui_event['id_or_xpath'][6:]]
            if source_event.shape[0] != 0:
                canonical = source_event.iloc[0]['canonical']
                target_event = ground_truth_target.loc[ground_truth_target['canonical'] == canonical]
                if target_event.shape[0] == 0:
                    gui_event['id_or_xpath'] = "NONE"
                elif pd.isnull(target_event.iloc[0]['id']):
                    gui_event['id_or_xpath'] = "xpath@" + target_event.iloc[0]['xpath']
                else:
                    gui_event['id_or_xpath'] = "id@" + target_event.iloc[0]['id']
            else:
                gui_event['id_or_xpath'] = "NONE_SOURCE"
                i += 1
        else:
            print(gui_event)
    return test

if __name__ == "__main__":
    for source_path in glob.glob("../src/test_csv/*.csv"):
        source_csv = read_csv(source_path, names=["method", "json"])
        source_csv['json'] = source_csv['json'].apply(json.loads)

        ground_truth_source = read_csv("ground_truth_mapping/GUI Mapping Ground Truth - " + os.path.basename(source_path))
        for target_path in glob.glob("../src/test_csv/*.csv"):
            if source_path != target_path:
                ground_truth_target = read_csv("ground_truth_mapping/GUI Mapping Ground Truth - " + os.path.basename(target_path))

                target_csv = pickle.loads(pickle.dumps(source_csv)) #deep copy
                i=0
                target_csv['json'] = target_csv['json'].apply(perfect_map, args=(ground_truth_source, ground_truth_target))
                print(source_path, target_path, i)

                target_csv['json'] = target_csv['json'].apply(json.dumps)
                target_csv.to_csv("perfect_out/" + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(target_path), index=False)
