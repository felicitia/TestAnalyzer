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
            else: # id_or_xpath starts with xpath@
                source_event = ground_truth_source.loc[ground_truth_source['xpath'] == gui_event['id_or_xpath'][6:]]
            if source_event.shape[0] != 0:
                if len(source_event.index) > 1:
                    i += 1
                    gui_event['info'] = 'multiple in src' # multiple matched rows in the ground_truth_source

                canonical = source_event.iloc[0]['canonical']
                target_event = ground_truth_target.loc[ground_truth_target['canonical'] == canonical]
                if target_event.shape[0] == 0: # the same canonical doesn't exist in the target app
                    # gui_event['case'] = 'nonExist'
                    gui_event['id_or_xpath'] = "NONE"
                else: # when the same canonical also exists in the target app
                    if len(target_event.index) > 1:
                        i += 1
                        gui_event['info'] = 'multiple in tgt' # multiple matched rows in the ground_truth_target
                    if pd.isnull(target_event.iloc[0]['id']):
                        gui_event['id_or_xpath'] = "xpath@" + target_event.iloc[0]['xpath']
                    else:
                        gui_event['id_or_xpath'] = "id@" + target_event.iloc[0]['id']

            else:
                # tmp = ['id@bbc.mobile.news.ww:id/content']
                # if gui_event['id_or_xpath'] not in tmp:
                print(gui_event['id_or_xpath'])
                print(source_csv)
                print('missing ground truth!!! should add the missing widget to the ground truth file :)')
                gui_event['id_or_xpath'] = "NONE_SOURCE"
                i += 1
        else:
            print('id_or_xpath is not in', gui_event, '!!!')
    return test

if __name__ == "__main__":
    count = 0
    test_case_dir = '/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/news/'
    gt_file_prefix = '../ground_truth_mapping/news/GT_'
    mapping_results_dir = '/Users/yixue/Documents/Research/FrUITeR/Results/perfect/mapping_results_news/'
    for source_path in glob.glob(test_case_dir + "*.csv"):
        source_csv = read_csv(source_path, header=0)
        source_csv['event_array'] = source_csv['event_array'].apply(json.loads)

        ground_truth_source = read_csv(gt_file_prefix + os.path.basename(source_path))
        for target_path in glob.glob(test_case_dir + "*.csv"):
            count += 1
            # if source_path != target_path: # consider same src-tgt app pair as well
            ground_truth_target = read_csv(gt_file_prefix + os.path.basename(target_path))

            target_csv = pickle.loads(pickle.dumps(source_csv)) #deep copy
            i=0
            target_csv['event_array'] = target_csv['event_array'].apply(perfect_map, args=(ground_truth_source, ground_truth_target))

            target_csv['event_array'] = target_csv['event_array'].apply(json.dumps)
            target_csv.to_csv(mapping_results_dir + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(target_path), index=False)

            print('processing #####  ', count, '/100')
            print('src = ', source_path, 'tgt = ', target_path, 'i = ', i)
