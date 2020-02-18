# FrUITeR implementation

The source code for FrUITeR's implementation including different components (e.g., GUI Mapper, Test Processor); and Test Analyzer including ground truth mapping of GUI events to their canonical IDs.

* Static Test Analyzer is located at `src/TestAnalyzer.java`

* Perfect GUI Mapper is located at `gui_mapper/gui_mapper_perfect.py`

* AppFlow GUI Mapper is located at `gui_mapper/gui_mapper_fse.py`

* CraftDroid GUI Mapper is located at `gui_mapper/gui_mapper_craftdroid.py`

* Naive GUI Mapper is located at `gui_mapper/gui_mapper_random.py`

* Result Generator is located at `gui_mapper/result_generator.ipynb`

* Test Processor is located at `other_components/test_processor.py`

* Test Synthesizer is located at `other_components/test_synthesizer.py`

* Post-Synthesis Result Generator is located at `gui_mapper/effectiveness_recalculator.ipynb`

* Ground Truth Mapping is located at `gui_mapper/ground_truth_mapping/`

------
Instructions for getting final results of appflow, craftdroid, perfect, naive
1. For appflow, run appflow/gui_mapper_appflow.py first to get the mapping results (e.g., transferred tests). Similarly, run baseline/gui_mapper_naive.py and gui_mapper_perfect.py to get corresponding mapping results. 

For craftdroid, craftdroid/process_craftdroid_results.py helps with manually constructing craftdroid's raw mapping results of GUI elements (e.g., CraftDroid Transfer Results - Etsy-Geek.csv) based on the published results. With such results, run craftdroid/gui_mapper_craftdroid.py to get the mapping results in the same manner as the other gui mappers mentioned above.

2. After getting all the mapping results from step 1, run result_generator.ipynb to get the final results with all the calculated metrics. You need to run all the cells until `combined_csv.to_csv("framework_results.csv")` to output the final results to a csv file.

*process_final_results.py has functions to process the final result files, such as adding columns for #src_test, #trans_test, #gt_test, calculating the avg of Naive, merging all results together to a single file.
