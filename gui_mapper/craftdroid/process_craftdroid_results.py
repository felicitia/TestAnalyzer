import pandas as pd
import json
import csv


if __name__ == "__main__":
    # generate raw mapping based on craftdroid's results
    src_app = 'a32'
    tgt_app = 'a31'
    test_case = 'b32'
    output = 'wish_geek.csv'
    src_test = pd.read_json('/Users/yixue/Documents/Research/FrUITeR/Develop/CraftDroid/code-release/test_repo/a3/'
                            + test_case +'/base/'+ src_app +'.json')
    row_count = src_test.shape[0]
    print('src test len = ', src_test.shape[0])

    transferred_test = pd.read_json('/Users/yixue/Documents/Research/FrUITeR/Develop/CraftDroid/code-release/test_repo/a3/'
                                    + test_case + '/generated/' + src_app + '-' + tgt_app + '-' + test_case + '.json')
    print('trans test len = ', transferred_test.shape[0])
    is_score = pd.notnull(transferred_test['score'])
    transferred_test_score = transferred_test[is_score]
    if row_count != transferred_test_score.shape[0]:
        print('score length not equal!!! trans test with score len = ', transferred_test_score.shape[0])

    with open(output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(row_count):
            row_to_write = []
            row_to_write.append(src_test.iloc[i]['resource-id'])
            row_to_write.append(transferred_test_score.iloc[i]['resource-id'])
            row_to_write.append(transferred_test_score.iloc[i]['score'])
            writer.writerow(row_to_write)