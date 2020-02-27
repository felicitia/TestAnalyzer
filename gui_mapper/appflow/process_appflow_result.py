import csv
import os


def get_canonical_list():
    canonical_set = set()
    with open('../ground_truth_mapping/news/canonical_news.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            canonical_set.add(row[0])
    return canonical_set

def get_appflow_canonical_set():
    canonical_set = set()
    with open('prediction_widget_results_10apps_news.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        count = 0
        for row in reader:
            count += 1
            canonical_set.add(row[3])
            canonical_set.add(row[4])
    return canonical_set

def get_appset_from_result(filename):
    app_set_from_result = set()
    with open(filename, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            app_set_from_result.add(row[0])
    return app_set_from_result

def get_appset_from_training():
    app_set_from_training = set()
    for file in os.listdir('/Users/yixue/Documents/Research/FrUITeR/Develop/AppFlow/appflow-master/guis-shopping'):
        if file.endswith('.xml'):
            # print(file)
            app_set_from_training.add(file.split('_')[0])
    return app_set_from_training

def delete_useless_appflow_results(old_result_file, new_result_file):
    news_applist = ['smartnews', 'cnn', 'reuters', 'bbc', 'newsrep', 'buzzfeed', 'fox', 'guardian', 'usatoday', 'abc']
    with open(old_result_file, 'r') as inp, open(new_result_file, 'w') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            # delete all the rows where the correctly predicted results are not NONE
            if row[4] != "NONE" and row[0] in news_applist:
                writer.writerow(row)

def get_app_names():
    apps = set()
    with open('prediction_widget_results_10apps_news.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        count = 0
        for row in reader:
            count += 1
            apps.add(row[0])
    return apps


def check_row8_none():
    with open('prediction_widget_results_10apps_shopping.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        count = 0
        for row in reader:
            count += 1
            if (row[5] != '' or row[6] != '') and row[8] == '':
                print(count)

if __name__ == "__main__":
    # our_canonical = get_canonical_list()
    # appflow_canonical = get_appflow_canonical_set()
    # diff_set =  (appflow_canonical - our_canonical)
    # for canonical in diff_set:
    #     print (canonical)
    with open('prediction_widget_results_10apps_news.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        count = 0
        for row in reader:
            count += 1
            if row[7] != '' and (row[5] == '' and row[6] == ''):
                print(count)

