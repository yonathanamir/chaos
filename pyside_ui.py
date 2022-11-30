import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np

from datetime import datetime

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import threading

from data_fetchers import DataFetcher, ScopeDataFetcher
from chaosv2 import analyze_am_signal, gen_bi_plot_data

import copy
import argparse



def init_args(args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--visa-address', type=str)
    parser.add_argument('--channels-to-sample', type=int, default=1)
    parser.add_argument('--target-fps', type=int, default=1)
    parser.add_argument('--test-mode', action='store_true')
    
    parser.add_argument('--color', type=str, default='k')
    parser.add_argument('--marker', type=str, default='.')
    parser.add_argument('--marker-size', type=int, default=1)
    parser.add_argument('--xlim', type=int, default=10500)
    parser.add_argument('--ylim', type=int, default=10)
    parser.add_argument('--dynamic-ylim', action='store_true')
    
    parser.add_argument('--window-size', type=int, default=2000)
    parser.add_argument('--limit', type=float, default=1.0)
    parser.add_argument('--offset', type=float, default=0)
    parser.add_argument('--stride', type=float, default=1.0)
    
    return parser.parse_args(args)


def add_random_noise(data):
    import random
    
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] += (0.5 - random.random())
    
    return data


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.args = init_args(sys.argv[1:])
        self.data_fetcher = DataFetcher()


        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)
        
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        try:
            print('hi!')
            # t1 = datetime.now()
            input_v, datas = self.data_fetcher.get_data()
            # t2 = datetime.now()
            
            datas = add_random_noise(copy.deepcopy(datas))

            analyzed = analyze_am_signal(input_v, datas, win_size=self.args.window_size, 
                                         limit=self.args.limit, offset=self.args.offset, 
                                         stride=self.args.stride, do_print=True)
            # t3 = datetime.now()
            
            for i, channel in enumerate(analyzed):
                data = gen_bi_plot_data(channel, do_print=True)
                
            self.xdata = data[:,0]
            self.ydata = data[:,1]
            
            
            # t4 = datetime.now()
            
            # self.canvas.draw()
            # self.canvas.flush_events()
            
            # t5 = datetime.now()
            # diff = t5 - t1
            # print(f'Step exec time: {diff}')
            # if diff < timedelta(seconds=args.target_fps):
            #     tosleep = diff.seconds
            #     print(f'Sleeping {tosleep} seconds...')
            #     time.sleep(tosleep)
            
            # print_time_table(t1, t2, t3, t4, t5)
        except Exception as ex:
            print(ex)
            # print('Error getting data, sleeping for 5 sec...')
            # time.sleep(5)
            # os.system('cls')

        
        
        # # Drop off the first y element, append a new one.
        # self.ydata = self.ydata[1:] + [random.randint(0, 10)]

        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.canvas.axes.scatter([], [], marker='.', color=self.args.color)
            self._plot_ref = plot_refs
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_offsets(np.c_[self.xdata,self.ydata])
            if self.args.dynamic_ylim:
                print('yo!')
                self.canvas.axes.set_ylim([0, np.max(data[:,1])*1.1])

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


app = QApplication(sys.argv)
w = MainWindow()
app.exec()
