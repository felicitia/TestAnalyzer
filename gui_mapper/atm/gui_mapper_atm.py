import csv
import os

src_resource_id = 0
src_class = 1
src_bounds = 2

tgt_resource_id = 3
tgt_class = 4
tgt_bounds = 5

score = 6

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


if __name__ == "__main__":
    # check_if_done('/Users/felicitia/Documents/workspaces/Eclipse/ATMGuiMapper', '.csv')
    # merge_scores('/Users/felicitia/Documents/workspaces/Eclipse/ATMGuiMapper','gui_mapper/atm')