import csv
import os

src_resource_id = 0
src_class = 1
src_bounds = 2

tgt_resource_id = 3
tgt_class = 4
tgt_bounds = 5

score = 6

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


if __name__ == "__main__":
    check_if_done('/Users/felicitia/Documents/workspaces/Eclipse/ATMGuiMapper', '.csv')