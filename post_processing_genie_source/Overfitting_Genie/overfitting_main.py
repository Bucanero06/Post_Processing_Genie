#!/usr/bin/env python3

import warnings

# import pandas as pd
import matplotlib
import numpy as np
import pandas as pd
import ray
from logger_tt import setup_logging, logger

from Overfitting_Genie.CSCV import CSCV
from post_processing_genie_main_ import load_pf_file

matplotlib.use('TkAgg')
warnings.filterwarnings(
    'ignore',
    category=ResourceWarning,
    message='ResourceWarning: unclosed'
)


def test_overfitting():
    nstrategy = 10
    nreturns = 120
    returns_test = pd.DataFrame({'s' + str(i): np.random.normal(0, 0.02, size=nstrategy) for i in range(nreturns)})
    #
    returns = returns_test.__deepcopy__()
    returns['s1'] += 0.02
    cscv = CSCV()
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)
    assert results['pbo_test'] == 0
    #
    returns = returns_test.__deepcopy__()
    cscv = CSCV()
    cscv.add_daily_returns(returns)
    results = cscv.estimate_overfitting(plot=True)
    assert results['pbo_test'] > 0


class Overfitting_Genie:

    def __init__(self, pickle_files_paths, cscv_nbins=10,
                 cscv_objective=lambda r: r.mean() / (r.std() + 0.0000001) * (365 ** 0.5),
                 plot_bool=False):
        logger.info(f'Running Overfitting Module')

        self.pickle_files_paths = pickle_files_paths
        self.cscv_nbins = cscv_nbins
        self.cscv_objective = cscv_objective
        self.plot_bool = plot_bool

    # 0.1349206349206349
    # 0.24206349206349206
    @staticmethod
    @ray.remote
    def get_pfs_returns_for_cscv(pf_index, pickle_path):
        print(f"\nPF #{pf_index + 1}")

        pf_minutes = load_pf_file(pickle_path)
        pf_daily = pf_minutes.resample('1d')
        returns = pf_daily.get_returns(chunked=True)
        #
        mask = returns.keys()
        #
        # mask = returns.keys()[(returns.fillna(0.0).sum() != 0)]
        # returns = returns[mask]
        if not returns.empty:
            # description = returns.describe()
            # p25 = description.loc["25%"]
            # p50 = description.loc["50%"]
            # p75 = description.loc["75%"]
            # mask = returns.keys()[((p25 != 0) & (p50 != 0) & (p75 != 0))]
            # returns = returns[mask]
            if not returns.empty:
                return returns

    def cscv(self):
        cscv_result = 0
        Returns = []
        self.pickle_files_paths = self.pickle_files_paths[:100]
        logger.info(f"\nTotal PFs {len(self.pickle_files_paths)}")

        # for pf_index, pickle_path in enumerate(self.pickle_files_paths):
        #     logger.info(f"\nPF #{pf_index + 1} of  {len(self.pickle_files_paths)}")
        #
        #     pf_minutes = load_pf_file(pickle_path)
        #     pf_daily = pf_minutes.resample('1d')
        #     returns = pf_daily.get_returns(chunked=True)
        #     #
        #     mask = returns.keys()
        #     #
        #     # mask = returns.keys()[(returns.fillna(0.0).sum() != 0)]
        #     # returns = returns[mask]
        #     if not returns.empty:
        #         # description = returns.describe()
        #         # p25 = description.loc["25%"]
        #         # p50 = description.loc["50%"]
        #         # p75 = description.loc["75%"]
        #         # mask = returns.keys()[((p25 != 0) & (p50 != 0) & (p75 != 0))]
        #         # returns = returns[mask]
        #         if not returns.empty:
        #             Returns.append(returns)
        Returns = ray.get([self.get_pfs_returns_for_cscv.remote(pf_index, pf_path) for pf_index, pf_path in
                           enumerate(self.pickle_files_paths)])

        Returns = pd.concat(Returns, axis=1)
        print(f'{Returns = }')

        cscv = CSCV()

        cscv.add_daily_returns(Returns)
        print(f'{cscv = }')
        exit()
        result = cscv.estimate_overfitting(plot=self.plot_bool)
        print(f'{result["pbo_test"] = }')
        # print(result["dom_df"].head())
        exit()

        return cscv_result


if __name__ == "__main__":
    setup_logging(full_context=1)
    logger.info("Running Test on Overfitting Main")
    test_overfitting()
