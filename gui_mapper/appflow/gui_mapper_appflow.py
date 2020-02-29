import pandas as pd
import json
import glob, os
from pandas.io.parsers import read_csv
import pickle

# test is the processed test case in .csv file
# target_app is the target app's name
def appflow_map(test, target_app):
    global appflow_dataset
    for gui_event in test:
        if gui_event['id_or_xpath'][:3] == "id@":
            source_event = appflow_dataset.loc[appflow_dataset['original GUI event id'] == gui_event['id_or_xpath'][3:]]
        else: # id_or_xpath starts with xpath@
            source_event = appflow_dataset.loc[appflow_dataset['original GUI event xpath'] == gui_event['id_or_xpath'][6:]]
            # if gui_event['id_or_xpath'][6:].startswith('//'):
            #     print('gui_event xpath = ', gui_event['id_or_xpath'][6:])
            #     print('source_event = ', source_event)
        if source_event.shape[0] == 0:  # search returns nothing, meaning appflow doesn't have the results
            gui_event['case'] = "notFound"
            gui_event['id_or_xpath'] = "NONE"
        else:
            source_prediction = source_event.iloc[0]['prediction canonical id']
            source_correct = source_event.iloc[0]['correct canonical id'] # correct canonical is never NONE, otherwise can't locate the widget being predicted
            # print('source prediction =', source_prediction)
            if source_prediction == "NONE" or pd.isnull(source_prediction):
                gui_event['case'] = "missed"
                gui_event['id_or_xpath'] = "NONE"

            else: # when predicted widget is not none
                if source_prediction == source_correct:
                    gui_event['case'] = "correct"
                else:
                    gui_event['case'] = "incorrect"

                # transfer predicted canonical widget to app-specific widget in the target app
                # based on appflow's results
                target_event = appflow_dataset.loc[
                    (appflow_dataset['prediction canonical id'] == source_prediction) & (appflow_dataset['app'] == target_app)]
                if target_event.shape[0] == 0:  # search returns nothing, meaning no widgets are predicted as source_prediction in the target app
                    gui_event['case'] = "notFound"
                    gui_event['id_or_xpath'] = "NONE"
                else: # when the predicted canonical widget exist in the target app based on appflow's results
                    target_prediction = target_event.iloc[0]['prediction canonical id']
                    target_correct = target_event.iloc[0]['correct canonical id']
                    if pd.isnull(target_correct): # when target widget's canonical doesn't exist (shouldn't happen with appflow's processed results)
                        print('target correct is null!!! should fix appflow results :)')
                        # gui_event['case'] = "incorrect"
                        # gui_event['id_or_xpath'] = "NONE"
                    else:
                        if target_prediction != target_correct:
                            gui_event['case'] = "incorrect"
                        if pd.isnull(target_event.iloc[0]['original GUI event id']):
                            gui_event['id_or_xpath'] = "xpath@" + target_event.iloc[0]['original GUI event xpath']
                        else:
                            gui_event['id_or_xpath'] = "id@" + target_event.iloc[0]['original GUI event id']
    return test

if __name__ == "__main__":
    appflow_dataset = read_csv("prediction_widget_results_10apps_news.csv")
    test_case_dir = '/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/news/'
    mapping_results_dir = "/Users/yixue/Documents/Research/FrUITeR/Results/appflow/mapping_results_news/"
    app_names = [str.lower(os.path.splitext(os.path.basename(file))[0]) for file in glob.glob(test_case_dir + "*.csv")]
    app_names = {e: e for e in app_names}
    # app_list = ['home', 'aliexpress', 'googleshopping', 'groupon', 'app', '6pm', 'ebay', 'wish', 'etsy', '5miles', 'geek']
    count = 0
    for source_path in glob.glob(test_case_dir + "*.csv"):
        source_csv = read_csv(source_path, header=0)
        source_csv['event_array'] = source_csv['event_array'].apply(json.loads)

        for target_path in glob.glob(test_case_dir + "*.csv"):
            # if source_path != target_path: delete this because we also transfer the same source app to the target app
            count += 1
            target_csv = pickle.loads(pickle.dumps(source_csv))  # deep copy
            target_appname = app_names[str.lower(os.path.splitext(os.path.basename(target_path))[0])]
            target_csv['event_array'] = target_csv['event_array'].apply(appflow_map, args=(target_appname,))

            target_csv['event_array'] = target_csv['event_array'].apply(json.dumps)
            target_csv.to_csv(
                 mapping_results_dir + os.path.splitext(os.path.basename(source_path))[0] + "_" + os.path.basename(
                    target_path), index=False)
            print('processing #####  ', count, '/100')
            print('src = ', source_path, 'tgt = ', target_path)
