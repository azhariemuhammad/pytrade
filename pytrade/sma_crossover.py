from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Calendar Days Filter Sample'
    )

    parser.add_argument('--data', '-d',
                        default='FB',
                        help='Ticker to download from Yahoo')

    parser.add_argument('--fromdate', '-f',
                        default='2018-10-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', '-t',
                        default='2019-05-10',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the Simple Moving Average')

    parser.add_argument('--writer', '-w', action='store_true',
                        help='Add a writer to cerebro')

    parser.add_argument('--wrcsv', '-wc', action='store_true',
                        help='Enable CSV Output in the writer')

    parser.add_argument('--plot', '-p', action='store_true',
                        help='Plot the read data')

    parser.add_argument('--numfigs', '-n', default=1, type=int,
                        help='Plot using numfigs figures')

    parser.add_argument('--commperc', required=False, action='store',
                        type=float, default=0.002,
                        help=('Perc (abs) commision in each operation. '
                              '0.001 -> 0.1%%, 0.01 -> 1%%'))

    return parser.parse_args()

class SMACrossOver(bt.Strategy):

    params = (
        ('fast', 9),
        ('slow', 18),
        ('_movav', btind.MovAv.SMA)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print(txt, dt, '{:20,.2f}'.format(self.broker.getvalue()))

    def __init__(self):
        sma_fast = self.p._movav(period=self.p.fast)
        sma_slow = self.p._movav(period=self.p.slow)

        self.dataclose = self.datas[0].close
        self.buysig = btind.CrossOver(sma_fast, sma_slow)
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.order_number = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.order_number += 1
        self.log('OPERATION PROFIT, ORDER_NUMBER %.2f, GROSS %.2f, NET %.2f' %
                 (self.order_number, trade.pnl, trade.pnlcomm))

    def next(self):

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if self.position:
            if self.buysig < 0:
                self.order = self.sell()
            elif self.buysig > 0:
                self.order = self.buy()
        elif self.buysig > 0:
            self.order = self.buy()


if __name__ == '__main__':
    args = parse_args()

    cerebro = bt.Cerebro()
    cerebro.addstrategy(SMACrossOver)
    cerebro.addsizer(bt.sizers.SizerFix, stake=5000)
    comminfo = bt.commissions.CommInfo_Stocks_Perc(commission=args.commperc,
                                                   percabs=True)

    cerebro.broker.addcommissioninfo(comminfo)

    fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')
    datapath = './raw/KBLI.JK.csv'
    data = btfeeds.YahooFinanceData(
        dataname=datapath,
        fromdate=fromdate,
        todate=todate,
        reverse=False
    )
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000000.0)

    # Add a writer with CSV
    if args.writer:
        cerebro.addwriter(bt.WriterFile, csv=args.wrcsv)
    print('=======================')
    # Print out the starting conditions
    print('Starting Portfolio Value: {:20,.2f}'.format(cerebro.broker.getvalue()))

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: {:20,.2f}'.format(cerebro.broker.getvalue()))
