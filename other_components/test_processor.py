import csv
import json

test_id = 0
method = 1
transferred = 2
source_app = 3
target_app = 4
gui_mapper = 5
correct = 6
incorrect = 7
missed = 8
nonExist = 9
TP = 10
FP = 11
FN = 12
src_events = 24

def apply_test_processor(final_result, test_processor_result):
    with open(final_result, 'r') as csv_input:
        with open(test_processor_result, 'w') as csv_output:
            writer = csv.writer(csv_output, lineterminator='\n')
            reader = csv.reader(csv_input)

            all = []
            row = next(reader)
            all.append(row)

            for row in reader:
                new_row = []
                new_row.append(row[test_id])
                new_row.append(row[method])

                events = row[src_events]
                trans_index = get_transition_idx(events, row[source_app])
                transferred_events = json.loads(row[transferred])

                for i in sorted(trans_index, reverse=True):
                    del (transferred_events[i])
                new_row.append(transferred_events)

                new_row.append(row[source_app])
                new_row.append(row[target_app])
                new_row.append(row[gui_mapper])

                correct_array = [d for d in transferred_events if d['case'] == 'correct']
                incorrect_array = [d for d in transferred_events if d['case'] == 'incorrect']
                missed_array = [d for d in transferred_events if d['case'] == 'missed']
                nonExist_array = [d for d in transferred_events if d['case'] == 'nonExist']
                new_row.append(correct_array)
                new_row.append(incorrect_array)
                new_row.append(missed_array)
                new_row.append(nonExist_array)

                new_row.append('NA') # TP column
                new_row.append('NA') # FP column
                new_row.append('NA') # FN column

                new_row.append(len(correct_array))
                new_row.append(len(incorrect_array))
                new_row.append(len(missed_array))
                new_row.append(len(nonExist_array))

                new_row.append('NA')  # num_TP column
                new_row.append('NA')  # num_FP column
                new_row.append('NA')  # num_FN column

                precision_denominator = len(correct_array) + len(incorrect_array)
                if precision_denominator == 0:
                    new_row.append('NA')
                else:
                    new_row.append(len(correct_array) / precision_denominator)

                recall_denominator = len(correct_array) + len(missed_array)
                if recall_denominator == 0:
                    new_row.append('NA')
                else:
                    new_row.append(len(correct_array) / recall_denominator)

                new_row.append('NA') # effectiveness precision column
                new_row.append('NA') # effectiveness recall column

                new_row.append(row[src_events])

                all.append(new_row)

            writer.writerows(all)

def get_transition_idx(events, app_name):
    index = []
    event_array = json.loads(events)
    for i in range(len(event_array)):
        # print (event_array[i])
        id_or_xpath = event_array[i]['id_or_xpath']
        if id_or_xpath.startswith('id@'):
            header = 'id'
            identifier = id_or_xpath[3:len(id_or_xpath)]
        elif id_or_xpath.startswith('xpath@'):
            header = 'xpath'
            identifier = id_or_xpath[6:len(id_or_xpath)]
        with open("gui_mapper/ground_truth_mapping/GUI Mapping Ground Truth - " + app_name + ".csv", 'r') as csv_input:
            reader = csv.reader(csv_input)
            for row in reader:
                if header == 'id' and row[0] == identifier:
                    if(row[6] == 'transition'):
                        index.append(i)
                    break
                if header == 'xpath' and row[1] == identifier:
                    if(row[6] == 'transition'):
                        index.append(i)
                    break
    return index


if __name__ == "__main__":
    apply_test_processor('new_final_result.csv', 'test_processor_results.csv')
