import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle
import random

THRESHOLD = .5


def random_map(test, ground_truth_target):
    global i, THRESHOLD

    first_activity = ground_truth_target.iloc[0]['current Activity'] # get the first 'current activity', which is the main activity
    current_activity = first_activity
    for gui_event in test['event_array']:
        gui_event['id_or_xpath'] = "NONE"
        activity_events = ground_truth_target.loc[ground_truth_target['current Activity'] == current_activity]
        if activity_events.shape[0] == 0:
            # print('no current activity: ',current_activity)
            current_activity = first_activity # if hit the end activity, start searching random events from the beginning
        activity_events = activity_events.sample(frac=1).reset_index(drop=True)  # randomize

        for index, activity_event in activity_events.iterrows():
            if ((gui_event['action'] == 'click' and activity_event.type != "input") or
                    (gui_event['action'] == 'sendKeys' and activity_event.type == "input")): # all the input events are marked, but not all the events are marked

                similarity = random.random()
                if similarity > THRESHOLD:
                    if pd.isnull(activity_event['id']):
                        gui_event['id_or_xpath'] = "xpath@" + activity_event['xpath']
                    else:
                        gui_event['id_or_xpath'] = "id@" + activity_event['id']

                    if not pd.isnull(activity_event['next Activity']): # if 'next activity' is null, it means it's the same activity as the current one
                        current_activity = activity_event['next Activity']
                    break

    return test


if __name__ == "__main__":
    count = 0
    test_case_dir = '/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/news/'
    gt_file_prefix = '../ground_truth_mapping/news/GT_'
    mapping_results_dir = '/Users/yixue/Documents/Research/FrUITeR/Results/naive/mapping_results_news/'
    for source_path in glob.glob(test_case_dir + "*.csv"):
        source_csv = read_csv(source_path, header=0)
        source_csv['event_array'] = source_csv['event_array'].apply(json.loads)

        for target_path in glob.glob(test_case_dir + "*.csv"):
            # if source_path != target_path:
            count += 1
            ground_truth_target = read_csv(gt_file_prefix + os.path.basename(target_path))

            target_csv = pickle.loads(pickle.dumps(source_csv))  # deep copy
            i = 0
            target_csv = target_csv.apply(random_map, args=(ground_truth_target,), axis=1)

            target_csv['event_array'] = target_csv['event_array'].apply(json.dumps)
            target_csv.to_csv(mapping_results_dir + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(
                    target_path), index=False)
            print('processing #####  ', count, '/100')
            print('src = ', source_path, 'tgt = ', target_path, 'i = ', i)
