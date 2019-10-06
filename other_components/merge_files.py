import csv
import os
import json
import numpy
import copy

test_id_idx = 0
method_idx = 1
transferred_idx = 2
source_app_idx = 3
target_app_idx = 4
gui_mapper_idx = 5
correct_idx = 6
incorrect_idx = 7
missed_idx = 8
nonExist_idx = 9
TP_idx = 10
FP_idx = 11
FN_idx = 12

def add_src(final_result, new_final_result):
    with open(final_result, 'r') as csv_input:
        with open(new_final_result, 'w') as csv_output:
            writer = csv.writer(csv_output, lineterminator='\n')
            reader = csv.reader(csv_input)

            all = []
            row = next(reader)
            row.append('src_events')
            all.append(row)

            for row in reader:
                app_name = row[source_app_idx]
                src_test = row[method_idx]
                row.append(get_src_events(src_test, app_name, '/Users/felicitia/Documents/workspaces/Eclipse/TestAnalyzer/src/test_csv'))
                all.append(row)

            writer.writerows(all)


def get_src_events(src_test, app_name, dir):
    with open(dir + '/' + app_name + '.csv', 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if row[0] == src_test:
                return row[1]
        print ('no src_test found!')

# return ground truth test case's event array
def get_gt_test(tgt_app, method_name):
    gt_test = []
    # print ('in get gt test...', tgt_app, method_name)
    with open(os.path.join('../src/test_csv/', tgt_app + '.csv'), 'r') as test_input:
        reader = csv.reader(test_input)
        for row in reader:
            if method_name in row[0]:
                json_array = json.loads(row[1])
                # print ('json_array = ', json_array)
                for event in json_array:
                    id_or_xpath = event['id_or_xpath']
                    # print ('id_or_xpath = ', id_or_xpath)
                    if 'id@' in id_or_xpath:
                        gt_test.append(id_or_xpath.split('id@')[1])
                    else:
                        gt_test.append(id_or_xpath)
                # if len(gt_test):
                #     print ('tgt_app = ', tgt_app)
                #     print ('method name = ', method_name)
                return gt_test

def get_trans_test(row):
    trans_test = []
    json_array = json.loads(row[transferred_idx])
    for event in json_array:
        id_or_xpath = event['id_or_xpath']
        if 'id@' in id_or_xpath:
            trans_test.append(id_or_xpath.split('id@')[1])
        else:
            trans_test.append(id_or_xpath)
    return trans_test

def levenshtein(seq1, seq2):
    # delete 'NONE' events in order to calculate levenshtein distance correctly
    events1 = copy.deepcopy(seq1)
    events2 = copy.deepcopy(seq2)
    # print ('event1 = ', events1)
    # print ('event2 = ', events2)
    if events1 is None or events2 is None:
        print ('events1 = ', events1)
        print ('events2 = ', events2)
        return 'NA'
    for event in events1:
        if event == 'NONE':
            events1.remove(event)
    for event in events2:
        if event == 'NONE':
            events2.remove(event)

    size_x = len(events1) + 1
    size_y = len(events2) + 1
    matrix = numpy.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if events1[x-1] == events2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    # print (matrix)
    return (matrix[size_x - 1, size_y - 1])

def add_gt_and_distance(final_result, new_final_result):
    with open(final_result, 'r') as csv_input:
        with open(new_final_result, 'w') as csv_output:
            writer = csv.writer(csv_output, lineterminator='\n')
            reader = csv.reader(csv_input)

            all = []
            # add gt_test, distance to the header
            row = next(reader)
            row.append('gt_test')
            row.append('distance')
            all.append(row)

            for row in reader:
                tgt_app = row[target_app_idx]
                # print ('tgt_app = ', tgt_app)
                method_name = str(row[method_idx]).split(': ')[1]
                # print ('method_name = ', method_name)
                gt_test = get_gt_test(tgt_app, method_name)
                trans_test = get_trans_test(row)
                row.append(gt_test)
                # print ('trans_test = ', trans_test)
                # print ('gt_test = ', gt_test)
                distance = levenshtein(trans_test,gt_test)
                if distance == 'NA':
                    print ('tgt_app = ', tgt_app)
                    print ('method_name = ', method_name)
                row.append(distance)
                all.append(row)

            writer.writerows(all)


if __name__ == "__main__":
    # add_src('final_framework_results.csv', 'final_framework_results_with_src.csv')
    # get_src_events('ss', 'Etsy', '/Users/felicitia/Documents/workspaces/Eclipse/TestAnalyzer/src/test_csv')
    add_gt_and_distance('../final_framework_results_with_src.csv', '../final_results_with_src_gt_distance.csv')