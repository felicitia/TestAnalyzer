import csv
import os
import json

src_resource_id_idx = 0
src_class_idx = 1
src_bounds_idx = 2

tgt_resource_id_idx = 3
tgt_class_idx = 4
tgt_bounds_idx = 5

score_idx = 6

# merge scores read from input_dir and output src_tgt_score.csv
def merge_scores(input_dir, output_dir):
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            src_app = file.split('_')[0]
            tgt_app = file.split('_')[1]
            # print (src_app, tgt_app)
            with open(os.path.join(input_dir, file), 'r') as csv_input:
                with open(os.path.join(output_dir, src_app+'_'+tgt_app+'_Scores.csv'), 'a') as csv_output:
                    writer = csv.writer(csv_output, lineterminator='\n')
                    reader = csv.reader(csv_input)
                    all = []
                    for row in reader:
                        all.append(row)
                    writer.writerows(all)

# check if the last line is 'done'
#     if done, then delete 'done'
#     if not, then print that file
def check_if_done(root_dir, extension):
    for file in os.listdir(root_dir):
        if file.endswith(extension):
            done = False
            lines = []
            with open(os.path.join(root_dir, file), 'r') as csv_input:
                reader = csv.reader(csv_input)
                for row in reader:
                    lines.append(row)
                    if row[0] == 'done':
                        done = True
            if done:
                lines = lines[:-1]
                with open(os.path.join(root_dir, file), 'w') as csv_output:
                    writer = csv.writer(csv_output, delimiter=',')
                    writer.writerows(lines)
            else:
                print (file, 'not done')


# read test case file and return all the relevant events (resource-ids) used in the test cases
# only for testSignIn() and testSignUp()
def get_events_from_tests(test_file):
    ids = set() # resource-id set
    with open(test_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if 'testSignIn()' in row[0] or 'testSignUp()' in row[0]:
                event_array = json.loads(row[1])
                for event in event_array:
                    if 'id@' in event['id_or_xpath']:
                        ids.add(event['id_or_xpath'].split('id@')[1])
                    else:
                        print ('no id found for event ', event)
    return ids

def generate_mapping(src_app, tgt_app, src_ids):
    filename = src_app + '_' + tgt_app + '_Scores.csv'
    # mapping's structure is {src id -> [matching tgt id, similarity score]}
    mapping = {}
    with open(filename, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if row[src_resource_id_idx] in src_ids:
                print (row)
                current_score = float(row[score_idx])
                if row[src_resource_id_idx] in mapping:
                    max_score = float(mapping[row[src_resource_id_idx]][1])
                else:
                    max_score = 0

                if current_score > max_score:
                    max_score = current_score
                    mapping[row[src_resource_id_idx]] = [row[tgt_resource_id_idx], max_score]

    return mapping

def output_mapping(mapping, src_app, tgt_app):
    filename = src_app + '_' + tgt_app + '_Mappings.csv'
    with open(filename, 'w') as csv_output:
        writer = csv.writer(csv_output, delimiter=',')
        for key in mapping:
            row = [key, mapping[key][0], mapping[key][1]]
            # print (row)
            writer.writerow(row)

if __name__ == "__main__":
    # check_if_done('/Users/felicitia/Documents/workspaces/Eclipse/ATMGuiMapper', '.csv')
    # merge_scores('/Users/felicitia/Documents/workspaces/Eclipse/ATMGuiMapper','gui_mapper/atm')

    src_app = 'Etsy'
    tgt_app = 'Wish'
    src_ids = get_events_from_tests('/Users/felicitia/Documents/workspaces/Eclipse/TestAnalyzer/src/test_csv/'+src_app+'.csv')
    mapping = generate_mapping(src_app, tgt_app, src_ids)
    output_mapping(mapping, src_app, tgt_app)
