#!/usr/bin/env python3
import argparse
from os import path

from logger_tt import logger

# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_debug"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_debug"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_update_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_update_test_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA100_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USA30_66M"
# STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USD30_1.2B_part_2"
STUDY_DIRECTORY_DEFAULT = "/home/ruben/PycharmProjects/mini_Genie/Studies/Study_mmt_USD100_1.2B"


# STUDY_DIRECTORY_DEFAULT = False
OVERFITTING_BOOL_DEFAULT = True
FILTERS_BOOL_DEFAULT = False
ANALYSIS_BOOL_DEFAULT = False
ACTIONS_PATH_DEFAULT = False
# todo need to move to inputs not defined here in run function, or pass to args the location of settings/requirements dictionary
SETTINGS = dict(
    Leverage=1,  # todo right now used to filter out less and more
    Init_cash=1_000_000,  # todo automatic
    Trade_size=100_000,  # todo automatic
    min_strats_per_batch=1,
    N_STEP_INCREASE=1
)
REQUIREMENTS = dict(
    Min_total_trades=200,
    Profit_factor=1.0,
    #
    Expectancy=0.01,
    Daily_drawdown=0.05,
    Total_drawdown=0.1,
    Profit_for_month=0.1,
    Total_Win_Rate=0.03
)
ACTIONS = dict(
    Filters=dict(
        actions=None
    )
)


class run_time_handler:
    """


    Args:
         ():
         ():

    Attributes:
         ():
         ():

    Note:

    """

    def __init__(self, run_function):
        """Constructor for run_time_handler"""
        #
        parser = argparse.ArgumentParser(description="Help for mini-Genie Trader")
        general_group = parser.add_argument_group(description="Basic Usage")
        expand_study_group = parser.add_argument_group(description="Expand Study Usage")
        #
        general_group.add_argument("-s", help="Path to Study Folder", dest="study_dir",
                                   action='store',
                                   default=STUDY_DIRECTORY_DEFAULT)
        general_group.add_argument("-o", help="Runs overfitting module", dest="overfitting_bool",
                                   action='store_true',
                                   default=OVERFITTING_BOOL_DEFAULT)
        general_group.add_argument("-f", help="Runs filters module", dest="filters_bool",
                                   action='store_true',
                                   default=FILTERS_BOOL_DEFAULT)
        general_group.add_argument("-actions_path", help="Path to commands used to run using action API",
                                   dest="actions_path", action='store',
                                   default=ACTIONS_PATH_DEFAULT)
        general_group.add_argument("-a", help="Runs analysis module", dest="analysis_bool",
                                   action='store_true',
                                   default=ANALYSIS_BOOL_DEFAULT)

        self.parser = parser
        self.parser.set_defaults(func=run_function)
        self.args = self.parser.parse_args()
        #
        if not self.args.study_dir:
            logger.error(f'No study dir passed')
            exit()
        #
        if not any([vars(self.args)[i] for i in vars(self.args) if i not in ['func', 'study_dir']]):
            if path.exists(self.args.study_dir):
                logger.info(f'Found directory {self.args.study_dir}')
            logger.warning("No action requested, exiting ...")
            parser.print_help()
            exit()
        else:
            # todo Load Settings and Requirements (Runtime parameters)
            self.args.settings = SETTINGS
            self.args.requirements = REQUIREMENTS
            from Utilities.utils import fetch_pf_files_paths
            self.args.pickle_files_paths = fetch_pf_files_paths(self.args.study_dir)
            if self.args.actions_path and path.exists(self.args.actions_path):
                # todo Load Actions/Commands (Runtime parameters)
                self.args.actions = ACTIONS
            else:
                self.args.actions = None

    @staticmethod
    def load_module_from_path(filename, object_name=None):

        module_path = filename.rsplit('.', 1)[0]
        module = module_path.replace("/", ".")

        from importlib import import_module
        mod = import_module(module)

        ###
        # import importlib.util
        # import sys
        # from os import path
        # #
        # logger.info(f"Loading Run_Time_Settings from file {filename}")
        # module_name = path.basename(module_path)
        # #
        # spec = importlib.util.spec_from_file_location(module_name, filename)
        # mod = importlib.util.module_from_spec(spec)
        # sys.modules[module_name] = mod
        # spec.loader.exec_module(mod)
        ###

        if object_name is not None:
            met = getattr(mod, object_name)
            return met
        else:
            return mod

    def call_run_function(self):
        self.args.func(self.args)
