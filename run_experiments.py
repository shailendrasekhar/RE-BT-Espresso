# global imports
import argparse
import sys, os
import glob

# relative file paths
sim_folder = "DataSim"
experiments_folder = sim_folder + "/configs/experiments"
bt_pipeline_folder = "BehaviorTreeDev"
result_analysis_folder = "ResultAnalysis"

# local imports, uses hacky path additions
# sim imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', sim_folder))
import bt_sim

# pipeline imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', bt_pipeline_folder))
import run_pipeline
import json_manager
from json_manager import JsonManager

# result analysis imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.', result_analysis_folder))
import run_results

json_file_path = "config.json"
output_file_path = "output.log"
should_recolor = False

def parse_args():
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--config", required = False, help = "Name of experiment config json, without this flag it will recurse though all experiments")
	ap.add_argument("-r", "--recolor", required = False, action='store_true', help = "Run recoloring of all trees")
	args = vars(ap.parse_args())
	json_file_path = None
	if "config" in args and args["config"] != None:
		json_file_path = args["config"]
	should_recolor = "recolor" in args and args["recolor"] != None and args['recolor']

	return json_file_path, should_recolor
def main():
	"""Runs the simulator and full pipeline end to end
	'-c, --config' - [optional] Path to json config
	"""
	print("Start Experiments")
	global experiments_folder
	base_pipeline_config = "DataSim/configs/base_pipeline_config.json" # this should not be moved

	single_experiment_filename, should_recolor = parse_args()
	if single_experiment_filename:
		run_experiment(base_pipeline_config, experiments_folder + "/" + single_experiment_filename, should_recolor)
	else:
		run_all_experiments(base_pipeline_config, should_recolor)

def run_all_experiments(base_pipeline_config, should_recolor):
    for config_file in glob.glob(experiments_folder + "/*.json"):
       run_experiment(base_pipeline_config, config_file, should_recolor)

def run_experiment(base_pipeline_config, experiment_file, should_recolor):
	sim_data_output_path, sim_tree_name = bt_sim.run_sim(experiment_file)	
	pipeline_config_path = write_pipeline_config(base_pipeline_config, sim_data_output_path, sim_data_output_path + "output")
	bt_tree_filepath_list = run_pipeline.run_pipeline(pipeline_config_path, should_recolor, sim_data_output_path + "fmt.log")
	# TODO: decide which tree we care about, right now will be the tree with no pruning, rest are in the bt_tree_filepath_list
	run_results.run_result(bt_tree_filepath_list[0] , sim_data_output_path + sim_tree_name + ".dot") # generated tree, simulated tree
	

def write_pipeline_config(base_pipeline_config, sim_data_output_path, output_folder):
	jm = JsonManager(base_pipeline_config)
	jm.set_csv_path(sim_data_output_path)
	jm.set_output_path(output_folder)
	jm.set_normalized_path(output_folder)
	jm.set_upsampled_path(output_folder)
	jm.set_hot_encoded_path(output_folder)

	pipeline_config_path = sim_data_output_path + "pipeline_config.json"
	jm.write_out_json_to_file(pipeline_config_path)
	return pipeline_config_path

if __name__ == '__main__':
	main()
