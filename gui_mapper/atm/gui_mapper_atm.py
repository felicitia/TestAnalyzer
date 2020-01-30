import csv
import os
import json
from lxml import etree

src_resource_id_idx = 0
src_class_idx = 1
src_bounds_idx = 2

tgt_resource_id_idx = 3
tgt_class_idx = 4
tgt_bounds_idx = 5

score_idx = 6


# merge raw scores read from input_dir and output src_tgt_score.csv so that each app pair's scores are merged together
def merge_scores(input_dir, output_dir):
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            src_app = file.split('_')[0]
            tgt_app = file.split('_')[1]
            # print (src_app, tgt_app)
            with open(os.path.join(input_dir, file), 'r') as csv_input:
                with open(os.path.join(output_dir, src_app + '_' + tgt_app + '_Scores.csv'), 'a') as csv_output:
                    writer = csv.writer(csv_output, lineterminator='\n')
                    reader = csv.reader(csv_input)
                    all = []
                    for row in reader:
                        all.append(row)
                    writer.writerows(all)


# check if the last line is 'done'
#     if done, then delete 'done'
#     if not, then print that file
# root_dir is the root directory of the raw similarity scores for each UI pair
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
                print(file, 'not done')


# read test case file and return all the relevant events (resource-ids) used in the test cases
# old method only for testSignIn() and testSignUp()
def get_events_from_tests_signin_signup(test_file):
    ids = set()  # resource-id set
    with open(test_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if 'testSignIn()' in row[0] or 'testSignUp()' in row[0]:
                event_array = json.loads(row[1])
                for event in event_array:
                    if 'id@' in event['id_or_xpath']:
                        ids.add(event['id_or_xpath'].split('id@')[1])
                    else:
                        print('no id found for event ', event)
    return ids


# read test case file and return all the id_or_xpath of the events
# duplicated id_or_xpath will be removed, e.g., same event in multiple test cases
def get_events_from_tests_all(test_file):
    ids = set()  # resource-id or xpath set, starting with id@ or xpath@
    with open(test_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            event_array = json.loads(row[1])
            for event in event_array:
                ids.add(event['id_or_xpath'])
    return ids


# old method to generate mapping only for resource-ids
def generate_mapping_id_only(src_app, tgt_app, src_ids):
    filename = src_app + '_' + tgt_app + '_Scores.csv'
    # mapping's structure is {src id -> [matching tgt id, similarity score]}
    mapping = {}
    with open(filename, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if row[src_resource_id_idx] in src_ids:
                print(row)
                current_score = float(row[score_idx])
                if row[src_resource_id_idx] in mapping:
                    max_score = float(mapping[row[src_resource_id_idx]][1])
                else:
                    max_score = 0

                if current_score > max_score:
                    max_score = current_score
                    mapping[row[src_resource_id_idx]] = [row[tgt_resource_id_idx], max_score]

    return mapping


# src_id_or_xpath: the id of the src element starting with id@
# will return the matching tgt element who has the highest score
def find_mapping_per_id(src_app, tgt_app, src_id_or_xpath):
    # mapping's structure is {src id_or_xpath -> [matching tgt id, matching tgt class, matching tgt bounds, similarity score]}
    mapping = {}
    score_file = '/Users/yixue/Documents/Research/FrUITeR/Results/ATM/merged_scores/' + src_app + '_' + tgt_app + '_Scores.csv'
    with open(score_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if row[src_resource_id_idx] == src_id_or_xpath.split('id@')[1]:
                print('row = ', row)
                current_score = float(row[score_idx])
                current_id_or_xpath = 'id@' + row[src_resource_id_idx]
                if current_id_or_xpath in mapping:
                    max_score = float(mapping[current_id_or_xpath][3])
                else:
                    max_score = 0

                if current_score > max_score:
                    max_score = current_score
                    mapping[current_id_or_xpath] = [row[tgt_resource_id_idx], row[tgt_class_idx], row[tgt_bounds_idx],
                                                    max_score]
    return mapping


# src_id_or_xpath: the id of the src element starting with xpath@
# will return the matching tgt element who has the highest score
def find_mapping_per_xpath(src_app, tgt_app, src_id_or_xpath):
    # mapping's structure is {src id_or_xpath -> [matching tgt id, matching tgt class, matching tgt bounds, similarity score]}
    mapping = {}
    src_node = find_node_by_xpath(src_id_or_xpath.split('xpath@')[1], src_app)
    if src_node is None:
        return mapping
    src_class = src_node.get('class')
    src_bounds = src_node.get('bounds')
    score_file = '/Users/yixue/Documents/Research/FrUITeR/Results/ATM/merged_scores/' + src_app + '_' + tgt_app + '_Scores.csv'
    with open(score_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            if row[src_class_idx] == src_class and row[src_bounds_idx] == src_bounds:
                print('row = ', row)
                current_score = float(row[score_idx])
                current_id_or_xpath = src_id_or_xpath
                if current_id_or_xpath in mapping:
                    max_score = float(mapping[current_id_or_xpath][3])
                else:
                    max_score = 0

                if current_score > max_score:
                    max_score = current_score
                    mapping[current_id_or_xpath] = [row[tgt_resource_id_idx], row[tgt_class_idx], row[tgt_bounds_idx],
                                                    max_score]
    return mapping


# will return the xml node based on the xpath and the .uix file
def find_node_by_xpath(xpath, app):
    directory = '/Users/yixue/Documents/Research/FrUITeR/Develop/UIAutomatorDumps/Shopping/' + \
                app + '/ForMapping/'
    print('find node for xpath', xpath, 'in app', app)
    for filename in os.listdir(directory):
        if filename.endswith(".uix"):
            # print('check xpath in ', os.path.join(directory, filename))
            tree = etree.parse(os.path.join(directory, filename))
            root = tree.getroot()
            if xpath.startswith('//'):  # relative xpath
                class_name = get_classname_from_xpath(xpath)
                attribute = get_attribute_from_xpath(xpath)
                # print('//node[@class="'+class_name+'"]['+attribute+']')
                nodes = root.xpath('//node[@class="' + class_name + '"][' + attribute + ']')
                if len(nodes) != 0:
                    print('current node is ', etree.tostring(nodes[0]))
                    return nodes[0]
            elif xpath.startswith('/hierarchy'):  # absolute xpath
                class_names = xpath.split('/')
                # print(class_names)
                current_node = root.xpath('/hierarchy')[0]
                no_matching = False
                for class_name in class_names:
                    if class_name == '' or class_name == 'hierarchy':
                        continue
                    # print('.//node[@class="' + class_name +'"]')
                    if '[' in class_name:  # multiple children with same class name
                        index = int(class_name[class_name.find("[") + 1:class_name.find("]")])
                        class_name = class_name.split('[')[0]
                        current_nodes = current_node.findall('./node[@class="' + class_name + '"]')
                        if current_nodes is None or index >= len(current_nodes):
                            no_matching = True
                            break
                        else:
                            current_node = current_nodes[index]
                    else:  # only one child with same class name
                        current_nodes = current_node.findall('./node[@class="' + class_name + '"]')
                        if current_nodes is None or len(current_nodes) == 0:
                            no_matching = True
                            break
                        else:
                            current_node = current_nodes[0]
                if not no_matching:
                    print('current node is ', etree.tostring(current_node))
                    return current_node
    print('current node is None')
    return None


def generate_mapping_id_or_xpath(src_app, tgt_app, src_id_or_xpath_list):
    # mapping's structure is {src id_or_xpath -> [matching tgt id, matching tgt class, matching tgt bounds, similarity score]}
    # regardless which test case the event belongs to in order to avoid duplicated mappings for efficiency reason
    mapping = {}
    for src_id_or_xpath in src_id_or_xpath_list:
        print('src id or xpath = ', src_id_or_xpath)
        if 'id@' in src_id_or_xpath:
            current_mapping = find_mapping_per_id(src_app, tgt_app, src_id_or_xpath)
            if current_mapping is not None:
                mapping.update(current_mapping)
        elif 'xpath@' in src_id_or_xpath:  # when src_id_or_xpath starts with 'xpath@'
            current_mapping = find_mapping_per_xpath(src_app, tgt_app, src_id_or_xpath)
            if current_mapping is not None:
                mapping.update(current_mapping)
        else:
            print('invalid src_id_or_xpath!')
    return mapping


def output_mapping(mapping, src_app, tgt_app):
    filename = '/Users/yixue/Documents/Research/FrUITeR/Results/ATM/mapping_results/' \
               + src_app + '_' + tgt_app + '_Mappings.csv'
    with open(filename, 'w') as csv_output:
        writer = csv.writer(csv_output, delimiter=',')
        for key in mapping:
            row = [key, mapping[key][0], mapping[key][1], mapping[key][2], mapping[key][3]]
            # print (row)
            writer.writerow(row)


def get_classname_from_xpath(xpath):
    return xpath.split('//')[1].split('[')[0]


def get_attribute_from_xpath(xpath):
    return xpath[xpath.find("[") + 1:xpath.find("]")]

# automatically output src_tgt_mappings for each src/tgt app pair based on the merged scores
# reading '/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV' is to get the whole app name list,
# can be substituted to a hard-coded array of the app names
def output_mapping_batch():
    app_list = os.listdir('/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/')
    count = 0
    for src_file in app_list:
        if not src_file.endswith('.csv'):
            continue
        src_app = src_file.split('.')[0]
        for tgt_file in app_list:
            if not tgt_file.endswith('.csv'):
                continue
            tgt_app = tgt_file.split('.')[0]
            src_id_or_xpath_list = get_events_from_tests_all(
                '/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/' + src_app + '.csv')
            mapping = generate_mapping_id_or_xpath(src_app, tgt_app, src_id_or_xpath_list)
            # print('mapping', mapping)
            output_mapping(mapping, src_app, tgt_app)
            count += 1
            print('finished##### ', count, '/100 ', src_app, tgt_app)

if __name__ == "__main__":
    #     check_if_done('/Users/yixue/Documents/Research/FrUITeR/Results/ATM/raw_scores', '.csv')

    #     merge_scores('/Users/yixue/Documents/Research/FrUITeR/Results/ATM/raw_scores',
    #     '/Users/yixue/Documents/Research/FrUITeR/Results/ATM/merged_scores')
    output_mapping_batch()
