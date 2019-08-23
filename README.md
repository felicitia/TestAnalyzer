# FrUITeR implementation

The source code for FrUITeR's implementation including different components (e.g., GUI Mapper, Test Processor); and Test Analyzer including ground truth mapping of GUI events to their canonical IDs.

* Static Test Analyzer is located `src/TestAnalyzer.java` and its result on the ground truth tests is located at `src/test_csv/`

* Perfect GUI Mapper is located at `gui_mapper/gui_mapper_perfect.py`

* AppFlow GUI Mapper is located at `gui_mapper/gui_mapper_fse.py`

* CraftDroid GUI Mapper is located at `gui_mapper/gui_mapper_craftdroid.py`

* Naive GUI Mapper is located at `gui_mapper/gui_mapper_random.py`

* Result Generator is located at `gui_mapper/result_generator.ipynb`

* Test Processor is located at `other_components/test_processor.py`

* Test Synthesizer is located at `other_components/test_synthesizer.py`

* Post-Synthesis Result Generator is located at `gui_mapper/effectiveness_recalculator.ipynb`

* Ground Truth Mapping is located at `gui_mapper/ground_truth_mapping/`
