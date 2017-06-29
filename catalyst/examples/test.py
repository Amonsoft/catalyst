#!/usr/bin/env python
#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

from catalyst.api import (
    order_target_percent,
    record,
    symbol,
    get_open_orders,
    set_commission,
    set_slippage,
    set_max_leverage,
    schedule_function,
    date_rules,
    time_rules,
    attach_pipeline,
    pipeline_output,
)

from catalyst.pipeline import Pipeline
from catalyst.pipeline.data import CryptoPricing
from catalyst.pipeline.factors.crypto import (
    VWAP,
    SimpleMovingAverage,
    MACDSignal,
)

from catalyst.finance.commission import PerDollar
from catalyst.finance.slippage import VolumeShareSlippage

TARGET_INVESTMENT_RATIO = 0.2
SHORT_WINDOW = 30
LONG_WINDOW = 100

def initialize(context):
    context.asset = symbol('USDT_BTC')
    context.i = 0
    context.macd_cur = None
    context.macd_last = None

    set_commission(PerDollar(cost=0.001))
    set_slippage(VolumeShareSlippage())
    set_max_leverage(1.0)

    attach_pipeline(make_pipeline(), 'my_pipeline')

    schedule_function(
        rebalance,
        date_rules.every_day(),
    )


def before_trading_start(context, data):
    context.pipeline_data = pipeline_output('my_pipeline')

def make_pipeline():
    return Pipeline(
        columns={
            'price': CryptoPricing.close.latest,
            'short_mavg': VWAP(window_length=SHORT_WINDOW),
            'long_mavg': VWAP(window_length=LONG_WINDOW),
            'macd': MACDSignal(
                fast_period=24,
                slow_period=52,
                signal_period=18,
            ),
        },
    )


def handle_data(context, data):
    pass

def rebalance(context, data):
    context.i += 1

    # get pipeline data for asset of interest
    pipeline_data = context.pipeline_data
    pipeline_data = pipeline_data[pipeline_data.index == context.asset].iloc[0]

    context.macd_last = context.macd_cur
    context.macd_cur = pipeline_data.macd

    # skip first LONG_WINDOW bars to fill windows
    if context.i < 2:
        return

    # retrieve long and short moving averages from pipeline
    short_mavg = pipeline_data.short_mavg
    long_mavg = pipeline_data.long_mavg
    price = pipeline_data.price

    # check that order has not already been placed
    open_orders = get_open_orders()
    if context.asset not in open_orders:
        # check that the asset of interest can currently be traded
        if data.can_trade(context.asset):
            if context.macd_cur < (0.98 * context.macd_last):
                order_target_percent(
                    context.asset,
                    TARGET_INVESTMENT_RATIO,
                    #limit_price=(2 * price),
                    #stop_price=(0.5 * price),
                )
            elif context.macd_cur > (1.02 * context.macd_last):
                order_target_percent(
                    context.asset,
                    0.0,
                    #limit_price=(2 * price),
                    #stop_price=(0.5 * price),
                )
                
            """
            # adjust portfolio based on moving averages
            if short_mavg > long_mavg:
                order_target_percent(
                    context.asset,
                    TARGET_INVESTMENT_RATIO,
                    #limit_price=(2 * price),
                    #stop_price=(0.5 * price),
                )
            elif short_mavg < long_mavg:
                order_target_percent(
                    context.asset,
                    0.0,
                    #limit_price=(2 * price),
                    #stop_price=(0.5 * price),
                )
            """

    record(
        USDT_BTC=price,
        cash=context.portfolio.cash,
        leverage=context.account.leverage,
        short_mavg=short_mavg,
        long_mavg=long_mavg,
    )
    


# Note: this function can be removed if running
# this algorithm on quantopian.com
def analyze(context=None, results=None):
    import matplotlib.pyplot as plt
    # Plot the portfolio and asset data.
    ax1 = plt.subplot(511)
    results[['portfolio_value']].plot(ax=ax1)
    ax1.set_ylabel('Portfolio value (USD)')

    ax2 = plt.subplot(512, sharex=ax1)
    ax2.set_ylabel('USDT_BTC (USD)')
    results[['USDT_BTC', 'short_mavg', 'long_mavg']].plot(ax=ax2)

    trans = results.ix[[t != [] for t in results.transactions]]
    amounts = [t[0]['amount'] for t in trans.transactions]
    print 'amounts:\n', amounts
    buys = trans.ix[
        [t[0]['amount'] > 0 for t in trans.transactions]
    ]
    sells = trans.ix[
        [t[0]['amount'] < 0 for t in trans.transactions]
    ]
    print 'buys:', buys.head()
    ax2.plot(
        buys.index, results.USDT_BTC[buys.index],
        '^',
        markersize=10,
        color='m',
    )
    ax2.plot(
        sells.index, results.USDT_BTC[sells.index],
        'v',
        markersize=10,
        color='k',
    )

    ax3 = plt.subplot(513, sharex=ax1)
    results[['leverage', 'alpha', 'beta']].plot(ax=ax3)
    ax3.set_ylabel('Leverage (USD)')

    ax4 = plt.subplot(514, sharex=ax1)
    results[['cash']].plot(ax=ax4)
    ax4.set_ylabel('Cash (USD)')

    results[[
        'treasury',
        'algorithm',
        'benchmark',
    ]] = results[[
        'treasury_period_return',
        'algorithm_period_return',
        'benchmark_period_return',
    ]]

    ax5 = plt.subplot(515, sharex=ax1)
    results[[
        'treasury',
        'algorithm',
        'benchmark',
    ]].plot(ax=ax5)
    ax5.set_ylabel('Dollars (USD)')

    plt.legend(loc=3)

    # Show the plot.
    plt.gcf().set_size_inches(18, 8)
    plt.show()


def _test_args():
    """Extra arguments to use when catalyst's automated tests run this example.
    """
    import pandas as pd

    return {
        'start': pd.Timestamp('2014-01-01', tz='utc'),
        'end': pd.Timestamp('2014-11-01', tz='utc'),
    }
