import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle
import random

THRESHOLD = .5

def random_map(test, ground_truth_target):
    global i, THRESHOLD
    
    current_activity = ground_truth_target.iloc[0]['current Activity']
    for gui_event in test['json']:
        gui_event['id_or_xpath'] = "NONE"
        activity_events = ground_truth_target.loc[ground_truth_target['current Activity'] == current_activity]
        if activity_events.shape[0] == 0:
            print(current_activity)
        activity_events = activity_events.sample(frac=1).reset_index(drop=True) #randomize
        
        for index, activity_event in activity_events.iterrows():
            if ((gui_event['action'] == 'click' and activity_event.type == "assertion") or
                (gui_event['action'] == 'sendKeys' and activity_event.type == "input") or
                (activity_event['type'] == "transition")):
                
                similarity = random.random()
                if similarity > THRESHOLD:
                    if pd.isnull(activity_event['id']):
                        gui_event['id_or_xpath'] = "xpath@" + activity_event['xpath']
                    else:
                        gui_event['id_or_xpath'] = "id@" + activity_event['id']
                    
                    if not pd.isnull(activity_event['next Activity']):
                        current_activity = activity_event['next Activity']
                    break
    
    return test

if __name__ == "__main__":
    for source_path in glob.glob("../src/test_csv/*.csv"):
        source_csv = read_csv(source_path, names=["method", "json"])
        source_csv['json'] = source_csv['json'].apply(json.loads)

        for target_path in glob.glob("../src/test_csv/*.csv"):
            if source_path != target_path:
                ground_truth_target = read_csv("ground_truth_mapping/GUI Mapping Ground Truth - " + os.path.basename(target_path))

                target_csv = pickle.loads(pickle.dumps(source_csv)) #deep copy
                i=0
                target_csv = target_csv.apply(random_map, args=(ground_truth_target,), axis=1)
                print(source_path, target_path, i)

                target_csv['json'] = target_csv['json'].apply(json.dumps)
                target_csv.to_csv("random_out/" + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(target_path), index=False)
