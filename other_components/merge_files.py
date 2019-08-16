import csv

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
                app_name = row[source_app]
                src_test = row[method]
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


if __name__ == "__main__":
    add_src('final_framework_results.csv', 'final_framework_results_with_src.csv')
    # get_src_events('ss', 'Etsy', '/Users/felicitia/Documents/workspaces/Eclipse/TestAnalyzer/src/test_csv')