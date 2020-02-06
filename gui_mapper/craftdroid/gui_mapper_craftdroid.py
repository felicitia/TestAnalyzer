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
                    event_row = mapping.loc[mapping['source xpath'] == gui_event['id_or_xpath'][6:]]
                if event_row.shape[0] != 0:
                    # when event_row has multiple rows, use the first row's result (event_row.iloc[0])
                    # because the mapped tgt events are the same in the ground truth
                    gui_event['score'] = event_row.iloc[0]['score']
                    if pd.isnull(event_row.iloc[0]['target resource id']):
                        if pd.isnull(event_row.iloc[0]['target xpath']):
                            gui_event['id_or_xpath'] = "NONE"
                        else:
                            gui_event['id_or_xpath'] = "xpath@" + event_row.iloc[0]['target xpath']
                    else:
                        if pd.isnull(event_row.iloc[0]['target resource id']):
                            gui_event['id_or_xpath'] = "NONE"
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
    count = 0
    for source_path in glob.glob("/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/craftdroid/*.csv"):
        source_csv = read_csv(source_path, header=0)
        source_csv['event_array'] = source_csv['event_array'].apply(json.loads)

        for target_path in glob.glob("/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/craftdroid/*.csv"):
            if source_path != target_path:
                count += 1
                mapping = read_csv(
                    "CraftDroid Transfer Results - " + os.path.splitext(os.path.basename(source_path))[
                        0] + "-" + os.path.basename(target_path))

                target_csv = pickle.loads(pickle.dumps(source_csv))  # deep copy
                i = 0
                target_csv['event_array'] = target_csv['event_array'].apply(craftdroid_map, args=(mapping,))

                target_csv['event_array'] = target_csv['event_array'].apply(json.dumps)
                target_csv.to_csv(
                    "/Users/yixue/Documents/Research/FrUITeR/Results/craftdroid/mapping_results/"
                    + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(
                        target_path), index=False)
                print('processing #####  ', count, '/6')
                print('src = ', source_path, 'tgt = ', target_path, 'i = ', i)
