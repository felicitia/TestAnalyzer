import csv
import os
import json
import numpy
import copy
from lxml import etree

def levenshtein(seq1, seq2):
    # delete 'NONE' events in order to calculate levenshtein distance correctly
    events1 = copy.deepcopy(seq1)
    events2 = copy.deepcopy(seq2)
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


# simple cases
# only handle sign in and sign up cases, assuming resource-id always exist
def evaluate_atm_mapping_signin_signup(src_app, tgt_app):
    with open(os.path.join('/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/', src_app + '.csv'), 'r') as test_input:
        with open('final_results_atm.csv', 'a') as result_output:
            writer = csv.writer(result_output, lineterminator='\n')
            reader = csv.reader(test_input)
            for row in reader:
                src_test = []
                trans_test = []
                correct = []
                incorrect = []
                missed = []
                nonExist = []
                # only evaluate sign in and sign up
                if 'testSignIn()' in row[0] or 'testSignUp()' in row[0]:
                    event_array = json.loads(row[1])
                    for event in event_array:
                        if 'id@' in event['id_or_xpath']:
                            src_id = event['id_or_xpath'].split('id@')[1]
                            src_test.append(src_id)
                            src_can = find_canonical_for_src(src_id, src_app)
                            trans_id = get_trans_event(src_id, src_app, tgt_app)
                            trans_can = find_canonical_for_src(trans_id, tgt_app)
                            trans_test.append(trans_id)
                            if trans_can != 'NONE':
                                if src_can == trans_can:
                                    correct.append(src_id)
                                else:
                                    incorrect.append(src_id)
                            else:
                                if check_canonical(src_can, tgt_app):
                                    # missed case
                                    missed.append(src_id)
                                else:
                                    #nonExist case
                                    nonExist.append(src_id)
                        else:
                            src_test.append(event['id_or_xpath'])
                            print ('no id found for event ', event)

                    # calcuate TP, FP, FN by comparing transferred test with ground-truth test
                    method_name = str(row[0]).split(': ')[1]
                    gt_test = get_gt_test(tgt_app, method_name)
                    print ('method = ', row[0])
                    print ('gt test = ', gt_test)
                    print ('trans test = ', trans_test)
                    TP = set(trans_test) & set(gt_test)
                    FP = set(trans_test) - set(gt_test)
                    FN = set(gt_test) - set(trans_test)
                    # output the current test case's results to the file
                    current_result = []
                    current_result.append(row[0])
                    current_result.append(src_test)
                    current_result.append(trans_test)
                    current_result.append(gt_test)
                    current_result.append(src_app)
                    current_result.append(tgt_app)
                    current_result.append('atm')
                    current_result.append(correct)
                    current_result.append(incorrect)
                    current_result.append(missed)
                    current_result.append(nonExist)
                    current_result.append(TP)
                    current_result.append(FP)
                    current_result.append(FN)
                    current_result.append(len(correct))
                    current_result.append(len(incorrect))
                    current_result.append(len(missed))
                    current_result.append(len(nonExist))
                    if (len(correct) + len(incorrect)) == 0:
                        current_result.append('NA')
                    else:
                        current_result.append(len(correct)/(len(correct) + len(incorrect)))
                    if (len(correct) + len(missed)) == 0:
                        current_result.append('NA')
                    else:
                        current_result.append(len(correct) / (len(correct) + len(missed)))
                    current_result.append(levenshtein(trans_test, gt_test))
                    writer.writerow(current_result)

# trans_test is an array of trans_event where each event has keys 'id', 'class', 'bounds'
# gt_test is an array of 'id_or_xpath'
# TP = (trans_test) & (gt_test)
# TP is an array that contains 'id_or_xpath'
def calculate_TP(trans_test, gt_test, tgt_app):
    TP = []
    gt_test_new = convert_gt_test(gt_test, tgt_app)
    for gt_event in gt_test_new:
        if 'id' in gt_event.keys():
            idname = gt_event['id']
            for trans_event in trans_test:
                if idname == trans_event['id']:
                    TP.append(gt_event['id_or_xpath'])
                    break
        elif 'class' in gt_event.keys():
            class_name = gt_event['class']
            bounds = gt_event['bounds']
            for trans_event in trans_test:
                if class_name == trans_event['class'] and bounds == trans_event['bounds']:
                    TP.append(gt_event['id_or_xpath'])
                    break

# trans_test is an array of trans_event where each event has keys 'id', 'class', 'bounds'
# gt_test is an array of 'id_or_xpath'
# FP = (trans_test) - (gt_test)
# FP is an array that contains trans_event dictionary that has 'id', 'class', 'bounds'
def calculate_FP(trans_test, gt_test, tgt_app):
    FP = []
    gt_test_new = convert_gt_test(gt_test, tgt_app)
    for trans_event in trans_test:
        if find_same_transEvent_in_gtTest(trans_event, gt_test_new) is None: # when trans_event is not in the gt_test
            FP.append(trans_event)
    return FP

# trans_test is an array of trans_event where each event has keys 'id', 'class', 'bounds'
# gt_test is an array of 'id_or_xpath'
# FN = (gt_test) - (trans_test)
# FN is an array that contains 'id_or_xpath'
def calculate_FN(trans_test, gt_test, tgt_app):
    FN = []
    gt_test_new = convert_gt_test(gt_test, tgt_app)
    for gt_event in gt_test_new:
        if find_same_gtEvent_in_transTest(gt_event, trans_test) is None: # when gt_event is not in the trans_test
            FN.append(gt_event['id_or_xpath'])

# gt_event is from the processed test cases and has 'id', 'class', 'bounds', 'id_or_xpath'
# trans_test is an array of trans_event that has 'id', 'class', 'bounds' (based .uix file)
def find_same_gtEvent_in_transTest(gt_event, trans_test):
    if 'id' in gt_event.keys(): # gt_event is based on resource-id
        for trans_event in trans_test:
            if trans_event['id'] is not None and gt_event['id'] == trans_event['id']:
                return gt_event['id_or_xpath']
    else: # gt_event is based on xpath
        for trans_event in trans_test:
            if trans_event['class'] is not None and trans_event['bounds'] is not None:
                if trans_event['class'] == gt_event['class'] and trans_event['bounds'] == gt_event['bounds']:
                    return gt_event['id_or_xpath']
    return None

# trans_event is from .uix file and has 'id', 'class', 'bounds'
# gt_test_new is an array of gt_event that has 'id', 'class', 'bounds', 'id_or_xpath' (based on the processed test cases)
def find_same_transEvent_in_gtTest(trans_event, gt_test_new):
    if trans_event['id'] is not None:
        for gt_event in gt_test_new:
            if 'id' in gt_event.keys(): # gt_event is based on resource-id
                if gt_event['id'] == trans_event['id']:
                    return gt_event['id_or_xpath']
    if trans_event['class'] is not None and trans_event['bounds'] is not None:
        for gt_event in gt_test_new:
            if 'class' in gt_event.keys(): # gt_event is based on xpath
                if gt_event['class'] == trans_event['class'] and gt_event['bounds'] == trans_event['bounds']:
                    return gt_event['id_or_xpath']
    return None

# convert gt_test to the same format as trans_test + an additional key 'id_or_xpath'
def convert_gt_test(gt_test, tgt_app):
    gt_test_new = []  # same format as trans_test
    for id_or_xpath in gt_test:
        gt_event = {}
        gt_event['id_or_xpath'] = id_or_xpath
        if 'id@' in id_or_xpath:
            gt_event['id'] = id_or_xpath.split('id@')[1]
        elif 'xpath@' in id_or_xpath:
            xpath = id_or_xpath.split('xpath@')[1]
            node = find_node_by_xpath(xpath, tgt_app)
            gt_event['class'] = node.get('class')
            gt_event['bounds'] = node.get('bounds')
        else:
            print('invalid id or xpath', id_or_xpath)
        gt_test_new.append(gt_event)  # each gt_event only has either id or class & bounds
    return gt_test_new



def evaluate_atm_mapping(src_app, tgt_app):
    with open(os.path.join('/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/', src_app + '.csv'), 'r') as test_input:
        with open('/Users/yixue/Documents/Research/FrUITeR/Results/ATM/final_results_atm.csv', 'a') as result_output:
            writer = csv.writer(result_output, lineterminator='\n')
            reader = csv.reader(test_input)
            for row in reader:
                src_test = []
                trans_test = []
                correct = []
                incorrect = []
                missed = []
                nonExist = []
                event_array = json.loads(row[1]) #load the events of each test case
                for event in event_array:
                    if 'id@' in event['id_or_xpath'] or 'xpath@' in event['id_or_xpath']:
                        src_id_or_xpath = event['id_or_xpath']
                        # src_id = src_id_or_xpath.split('id@')[1]
                        src_test.append(src_id_or_xpath)
                        src_can = find_canonical_for_src(src_id_or_xpath, src_app)
                        trans_event = get_trans_event(src_id_or_xpath, src_app, tgt_app)
                        trans_can = find_canonical_for_tgt(trans_event, tgt_app)
                        trans_test.append(trans_event)
                        if trans_can != 'NONE':
                            if src_can == trans_can:
                                correct.append(src_id_or_xpath)
                            else:
                                incorrect.append(src_id_or_xpath)
                        else:
                            if check_canonical(src_can, tgt_app):
                                # missed case
                                missed.append(src_id_or_xpath)
                            else:
                                #nonExist case
                                nonExist.append(src_id_or_xpath)
                    else:
                        print('id_or_xpath field invalid for event', event)

                # calcuate TP, FP, FN by comparing transferred test with ground-truth test
                method_name = str(row[0]).split(': ')[1] # get method name of the test case
                gt_test = get_gt_test(tgt_app, method_name)
                print ('method = ', row[0])
                print ('gt test = ', gt_test)
                print ('trans test = ', trans_test)
                # TP is an array that contains 'id_or_xpath'
                TP = calculate_TP(trans_test, gt_test, tgt_app)
                # FP is an array that contains trans_event dictionary that has 'id', 'class', 'bounds'
                FP = calculate_FP(trans_test, gt_test, tgt_app)
                # FN is an array that contains 'id_or_xpath'
                FN = calculate_FN(trans_test, gt_test, tgt_app)
                # output the current test case's results to the file
                current_result = []
                current_result.append(row[0])
                current_result.append(src_test)
                current_result.append(trans_test)
                current_result.append(gt_test)
                current_result.append(src_app)
                current_result.append(tgt_app)
                current_result.append('atm')
                current_result.append(correct)
                current_result.append(incorrect)
                current_result.append(missed)
                current_result.append(nonExist)
                current_result.append(TP)
                current_result.append(FP)
                current_result.append(FN)
                current_result.append(len(correct))
                current_result.append(len(incorrect))
                current_result.append(len(missed))
                current_result.append(len(nonExist))
                if (len(correct) + len(incorrect)) == 0:
                    current_result.append('NA')
                else:
                    current_result.append(len(correct)/(len(correct) + len(incorrect)))
                if (len(correct) + len(missed)) == 0:
                    current_result.append('NA')
                else:
                    current_result.append(len(correct) / (len(correct) + len(missed)))
                current_result.append(levenshtein(trans_test, gt_test))
                writer.writerow(current_result)


# return ground truth test case's event array
# each element contains id_or_xpath starting with id@ or xpath@
def get_gt_test(tgt_app, method_name):
    gt_test = []
    with open(os.path.join('/Users/yixue/Documents/Research/FrUITeR/Develop/ProcessedTest_CSV/', tgt_app + '.csv'), 'r') as test_input:
        reader = csv.reader(test_input)
        for row in reader:
            if method_name in row[0]:
                json_array = json.loads(row[1])
                for event in json_array:
                    id_or_xpath = event['id_or_xpath']
                    gt_test.append(id_or_xpath)
                return gt_test

def check_canonical(canonical, app):
    with open('../ground_truth_mapping/GUI Mapping Ground Truth - ' + app + '.csv') as canonical_input:
        reader = csv.reader(canonical_input)
        for row in reader:
            if row[3] == canonical:
                return True
    return False

# get the id, class, bounds of the transferred event based on ATM's mapping results
def get_trans_event(src_id_or_xpath, src_app, tgt_app):
    print('getting transferred event for', src_id_or_xpath, 'in src app', src_app)
    trans_event = {} # trans_test's keys are: id_or_xpath, class, bounds
    filename = '/Users/yixue/Documents/Research/FrUITeR/Results/ATM/mapping_results/' \
               + src_app + '_' + tgt_app + '_Mappings.csv'
    with open(filename, 'r') as mapping_input:
        reader = csv.reader(mapping_input)
        for row in reader:
            if row[0] == src_id_or_xpath: # row[0] is src_id_or_xpath from the source app
                trans_event['id'] = row[1] # row[1] is the id of the transferred event in the target app
                trans_event['class'] = row[2] # row[2] is the class of the transferred event in the target app
                trans_event['bounds'] = row[3] # row[3] is the bounds of the transferred event in the target app
                print('transferred event: ', trans_event)
                return trans_event
    print('transferred event: ', trans_event)
    return trans_event

# find canonical for source app
# the id_or_xpath is always in the group truth map
def find_canonical_for_src(id_or_xpath, app):
    print('finding canonical for ', id_or_xpath)
    with open('../ground_truth_mapping/GUI Mapping Ground Truth - ' + app + '.csv') as canonical_input:
        reader = csv.reader(canonical_input)
        flag = ''
        if 'id@' in id_or_xpath:
            idname = id_or_xpath.split('id@')[1]
            flag = 'id'
        elif 'xpath@' in id_or_xpath:
            xpath = id_or_xpath.split('xpath@')[1]
            flag = 'xpath'
        else:
            print('invalid id or xpath in find_canonical!')
        for row in reader:
            if flag == 'id':
                if row[0] == idname: # row[0] is the id
                    print('canonical is ', row[3])
                    return row[3] # row[3] is the canonical element
            elif flag == 'xpath':
                if row[1] == xpath: # row[1] is the xpath
                    print('canonical is ', row[3])
                    return row[3] # row[3] is the canonical element
            else:
                print('invalid id or xpath in find_canonical!')
    print('canonical is NONE')
    return 'NONE'

# find canonical for target app based on trans_event whose keys are: id, class, bounds
# the transferred id may not exist in the ground truth map
def find_canonical_for_tgt(trans_event, app):
    print('finding canonical for ', trans_event)
    with open('../ground_truth_mapping/GUI Mapping Ground Truth - ' + app + '.csv') as canonical_input:
        reader = csv.reader(canonical_input)
        id_flag = False
        if trans_event['id'] is not None:
            id_flag = True
        for row in reader:
            if id_flag:
                if row[0] is not None and row[0] == trans_event['id']:
                    print('canonical is ', row[3])
                    return row[3]
            else:
                if row[1] is not None: # row[1] is xpath in the group truth map
                    xpath = row[1]
                    node = find_node_by_xpath(xpath)
                    if node is not None:
                        class_name = node.get('class')
                        bounds = node.get('bounds')
                        if class_name == trans_event['class'] and bounds == trans_event['bounds']:
                            return row[3]
    print('canonical is NONE')
    return 'NONE'

def get_classname_from_xpath(xpath):
    return xpath.split('//')[1].split('[')[0]


def get_attribute_from_xpath(xpath):
    return xpath[xpath.find("[") + 1:xpath.find("]")]


def find_node_by_xpath(xpath, app):
    directory = '/Users/yixue/Documents/Research/FrUITeR/Develop/UIAutomatorDumps/Shopping/' + \
                app + '/ForMapping/'
    for filename in os.listdir(directory):
        if filename.endswith(".uix"):
            print('check xpath in ', os.path.join(directory, filename))
            tree = etree.parse(os.path.join(directory, filename))
            root = tree.getroot()
            if xpath.startswith('//'):  # relative xpath
                class_name = get_classname_from_xpath(xpath)
                attribute = get_attribute_from_xpath(xpath)
                # print('//node[@class="'+class_name+'"]['+attribute+']')
                nodes = root.xpath('//node[@class="' + class_name + '"][' + attribute + ']')
                if len(nodes) != 0:
                    return nodes[0]
            elif xpath.startswith('/hierarchy'):  # absolute xpath
                class_names = xpath.split('/')
                # print(class_names)
                current_node = root.xpath('/hierarchy')[0]
                for class_name in class_names:
                    if class_name == '' or class_name == 'hierarchy':
                        continue
                    # print('.//node[@class="' + class_name +'"]')
                    if '[' in class_name:  # multiple children with same class name
                        index = int(class_name[class_name.find("[") + 1:class_name.find("]")])
                        class_name = class_name.split('[')[0]
                        current_nodes = current_node.findall('./node[@class="' + class_name + '"]')
                        if current_nodes is None or index >= len(current_nodes):
                            break
                        else:
                            current_node = current_nodes[index]
                    else:  # only one child with same class name
                        current_nodes = current_node.findall('./node[@class="' + class_name + '"]')
                        if current_nodes is None or len(current_nodes) == 0:
                            break
                        else:
                            current_node = current_nodes[0]
                return current_node
    return None


if __name__ == "__main__":
    # evaluate_atm_mapping_signin_signup(src_app, tgt_app)
    # result is in 'final_results_atm.csv' with the header 'method,src_events,transferred,gt_events,source,target,gui_mapper,correct,incorrect,missed,nonExist,TP,FP,FN,num_correct,num_incorrect,num_missed,num_nonExist,accuracy_precision,accuracy_recall,distance'
    # a = ['aa', 'bbb', 'ccc']
    # b = ['bb', 'aa', 'ccc']
    # print (levenshtein(b, a))