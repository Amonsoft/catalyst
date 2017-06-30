Catalyst
========

|version status|

Catalyst is an algorithmic trading library for crypto-assets written in Python.
It allows trading strategies to be easily expressed and backtested against historical data, providing analytics and insights regarding a particular strategy's performance.
Catalyst will be expanded to support live-trading of crypto-assets in the coming months.
Please visit `<enigma.co/catalyst>`_ to learn about Catalyst, or refer to the 
`whitepaper <http://www.enigma.co/enigma_catalyst.pdf>`_ for further technical details.

Interested in getting involved?
`Join our slack! <https://join.slack.com/enigmacatalyst/shared_invite/MTkzMjQ0MTg1NTczLTE0OTY3MjE3MDEtZGZmMTI5YzI3ZA>`_


Installation
============

At the moment, Catalyst has some fairly specific and strict depedency requirements.
We recommend the use of Python virtual environments if you wish to simplify the installation process, or otherwise isolate Catalyst's dependencies from your other projects.
If you don't have ``virtualenv`` installed, see our later section on Virtual Environments.

.. code-block:: bash

    $ virtualenv catalyst-venv
    $ source ./catalyst-venv/bin/activate
    $ pip install enigma-catalyst

**Note:** A successful installation will require several minutes in order to compile dependencies that expose C APIs.

Dependencies
------------

Catalyst's depedencies can be found in the ``etc/requirements.txt`` file.
If you need to install them outside of a typical ``pip install``, this is done using:

.. code-block:: bash

    $ pip install -r etc/requirements.txt

Though not required by Catalyst directly, our example algorithms use matplotlib to visually display backtest results.
If you wish to run any examples or use matplotlib during development, it can be installed using:

.. code-block:: bash

    $ pip install matplotlib

Virtual Environments
--------------------

Here we will provide a brief tutorial for installing ``virtualenv`` and its basic usage.
For more information regarding ``virtualenv``, please refer to this `virtualenv guide <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_.

The ``virtualenv`` command can be installed using:

.. code-block:: bash

    $ pip install virtualenv

To create a new virtual environment, choose a directory, e.g. ``/path/to/venv-dir``, where project-specific packages and files will be stored.  The environment is created by running:

.. code-block:: bash

    $ virtualenv /path/to/venv-dir

To enter an environment, run the ``bin/activate`` script located in ``/path/to/venv-dir`` using:

.. code-block:: bash

    $ source /path/to/venv-dir/bin/activate

Exiting an environment is accomplished using ``deactivate``, and removing it entirely is done by deleting ``/path/to/venv-dir``.

Using virtualenv & matplotlib on OS X
-------------------------------------

A note about using matplotlib in virtual enviroments on OS X: it may be necessary to add

.. code-block:: python

    backend : TkAgg

to your ``~/.matplotlib/matplotlibrc`` file, in order to override the default ``macosx`` backend for your system, which may not be accessible from inside the virtual environment.
This will allow Catalyst to open matplotlib charts from within a virtual environment, which is useful for displaying the performance of your backtests.  To learn more about matplotlib backends, please refer to the
`matplotlib backend documentation <https://matplotlib.org/faq/usage_faq.html#what-is-a-backend>`_.

Quickstart
==========

See our `getting started tutorial <http://www.zipline.io/#quickstart>`_.

The following code implements a simple buy and hodl algorithm.

.. code:: python

    import numpy as np
    
    from catalyst.api import (
        order_target_value,
        symbol,
        record,
        cancel_order,
        get_open_orders,
    )
    
    ASSET = 'USDT_BTC'
    
    TARGET_HODL_RATIO = 0.8
    RESERVE_RATIO = 1.0 - TARGET_HODL_RATIO

    def initialize(context):
        context.is_hodling = True
        context.asset = symbol(ASSET)

    def handle_data(context, data):
        cash = context.portfolio.cash
        target_hodl_value = TARGET_HODL_RATIO * context.portfolio.starting_cash
        reserve_value = RESERVE_RATIO * context.portfolio.starting_cash
        
        # Cancel any outstanding orders from the previous day
        orders = get_open_orders(context.asset) or []
        for order in orders:
            cancel_order(order)
        
        # Stop hodling after passing reserve threshold
        if cash <= reserve_value:
            context.is_hodling = False
        
        # Retrieve current price from pricing data
        price = data[context.asset].price
        
        # Check if still hodling and could afford another purchase
        if context.is_hodling and cash > price:
            order_target_value(
                context.asset,
                target_hodl_value,
                limit_price=1.1 * price,
                stop_price=0.9 * price,
            )
        
        # Record any state for later analysis
        record(
            price=price,
            cash=context.portfolio.cash,
            leverage=context.account.leverage,
        )


You can then run this algorithm using the Catalyst CLI. From the command
line, run:

.. code:: bash

    $ catalyst ingest
    $ catalyst run -f buy_and_hodl.py --start 2015-1-1 --end 2016-6-25 --captial-base 100000

This will download the crypto-asset price data from a poloniex bundle
curated by Enigma in the specified time range and stream it through
the algorithm and plot the resulting performance using matplotlib.

You can find other examples in the ``catalyst/examples`` directory.

Disclaimer
==========

Keep in mind that this project is still under active development, and is not recommended for production use in its current state.
We are deeply committed to improving the overall user experience, reliability, and feature-set offered by Catalyst.
If you have any suggestions, feedback, or general improvements regarding any of these topics, please let us know!

Hello World,

The Enigma Team

.. |version status| image:: https://img.shields.io/pypi/pyversions/catalyst-hf.svg
   :target: https://testpypi.python.org/pypi/catalyst-hf

.. _`Catalyst Install Documentation` : https://enigma.co/catalyst/install.html
