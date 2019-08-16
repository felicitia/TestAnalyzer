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
num_correct = 13
num_incorrect = 14
num_missed = 15
num_nonExist = 16
src_events = 24

def apply_test_synthesizer(final_result, test_synthesizer_results):
    with open(final_result, 'r') as csv_input:
        with open(test_synthesizer_results, 'w') as csv_output:
            writer = csv.writer(csv_output, lineterminator='\n')
            reader = csv.reader(csv_input)

            all = []
            row = next(reader)
            all.append(row)

            for row in reader:
                new_row = []
                new_row.append(row[test_id])
                new_row.append(row[method])

                events = row[transferred]
                new_row.append(add_transition(events, row[target_app]))

                new_row.append(row[source_app])
                new_row.append(row[target_app])
                new_row.append(row[gui_mapper])

                new_row.append(row[correct])
                new_row.append(row[incorrect])
                new_row.append(row[missed])
                new_row.append(row[nonExist])

                new_row.append('NA') # TP column
                new_row.append('NA') # FP column
                new_row.append('NA') # FN column

                new_row.append(row[num_correct])
                new_row.append(row[num_incorrect])
                new_row.append(row[num_missed])
                new_row.append(row[num_nonExist])

                new_row.append('NA')  # num_TP column
                new_row.append('NA')  # num_FP column
                new_row.append('NA')  # num_FN column

                new_row.append('NA')  # accuracy precision column
                new_row.append('NA')  # accuracy recall column

                new_row.append('NA') # effectiveness precision column
                new_row.append('NA') # effectiveness recall column

                all.append(new_row)

            writer.writerows(all)

def add_transition(events, app_name):
    new_transferred = []
    event_array = json.loads(events)
    if len(event_array) == 0:
        return new_transferred
    # print (len(event_array))
    for i in range(len(event_array) - 1):
        #add first event, then check whether transition event(s) need to be added before adding the second event
        new_transferred.append(event_array[i])
        # print (event_array[i])
        header = ''
        next_header = ''

        id_or_xpath = event_array[i]['id_or_xpath']
        if id_or_xpath.startswith('id@'):
            header = 'id'
            identifier = id_or_xpath[3:len(id_or_xpath)]
        elif id_or_xpath.startswith('xpath@'):
            header = 'xpath'
            identifier = id_or_xpath[6:len(id_or_xpath)]

        next_id_or_xpath = event_array[i + 1]['id_or_xpath']
        if next_id_or_xpath.startswith('id@'):
            next_header = 'id'
            next_identifier = next_id_or_xpath[3:len(id_or_xpath)]
        elif next_id_or_xpath.startswith('xpath@'):
            next_header = 'xpath'
            next_identifier = next_id_or_xpath[6:len(id_or_xpath)]

        with open("gui_mapper/ground_truth_mapping/GUI Mapping Ground Truth - " + app_name + ".csv", 'r') as csv_input:
            reader = csv.reader(csv_input)
            curAct = ''
            next_curAct = ''
            for row in reader:
                if header == 'id' and row[0] == identifier:
                    curAct = row[4]
                if header == 'xpath' and row[1] == identifier:
                    curAct = row[4]
                if next_header == 'id' and row[0] == next_identifier:
                    next_curAct = row[4]
                if next_header == 'xpath' and row[1] == next_identifier:
                    next_curAct = row[4]
            if curAct != '' and next_curAct != '' and curAct != next_curAct:
                new_transferred.append(find_transition(curAct, next_curAct, app_name))
    # print (event_array, len(event_array))
    new_transferred.append(event_array[len(event_array) - 1])
    return json.dumps(new_transferred)

# only find one transition if current and next match the ground truth
def find_transition(curAct, next_curAct, app_name):
    with open("gui_mapper/ground_truth_mapping/GUI Mapping Ground Truth - " + app_name + ".csv", 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            cur = row[4]
            next = row[5]
            if cur == curAct and next == next_curAct:
                event = {}
                event['id'] = row[0]
                event['xpath'] = row[1]
                return event


if __name__ == "__main__":
    apply_test_synthesizer('final_framework_results.csv', 'test_synthesizer_results.csv')
