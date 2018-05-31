import matplotlib
import time
import random
import numpy as np
from threading import Thread
from threading import Lock
import pingparsing
import subprocess
import matplotlib.pyplot as plt
from numpy import ones
import operator
import math
from statistics import stdev
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import sys

matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure

import tkinter as tk


#BACKGROUND_COLOR = '#8e8e8e';

#BACKGROUND_COLOR = '#636363';
#BACKGROUND_PLOT_COLOR = '#757575';
#FILL_COLOR = '#648182';
#PLOT_COLOR = '#00bac1';

BACKGROUND_COLOR = 		'#292929';
BACKGROUND_PLOT_COLOR = '#303030';
FILL_COLOR = 				'#264749';
PLOT_COLOR = 				'#00a4ad';

NUMBERS_COLOR = '#c6c6c6';
SPINE_COLOR = '#4f4f4f';


class GraphPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.configure(background=BACKGROUND_COLOR);
		
		self.__controller = controller
		self.__canvas = None;
		self.__mean_bar = None;
		self.__graph = None;
		self.__thread = None;
		self.setLock(Lock());
		self.setGuiLock(Lock());
		
		f = Figure(figsize=(5, 3), facecolor=BACKGROUND_COLOR);
		vfx = [19, 1];
		gs = matplotlib.gridspec.GridSpec(2, 1, height_ratios=vfx);
		
		graph = f.add_subplot(gs[0])
		mean_bar = f.add_subplot(gs[1]);
		
		graph.set_facecolor(BACKGROUND_PLOT_COLOR);
		mean_bar.set_facecolor(BACKGROUND_PLOT_COLOR);
		
		graph.spines['bottom'].set_color(SPINE_COLOR);
		graph.spines['top'].set_color(SPINE_COLOR);
		graph.spines['right'].set_color(SPINE_COLOR);
		graph.spines['left'].set_color(SPINE_COLOR);
		
		graph.yaxis.label.set_color(SPINE_COLOR);
		graph.xaxis.label.set_color(SPINE_COLOR);
		
		graph.tick_params(axis='x', colors=NUMBERS_COLOR);
		graph.tick_params(axis='y', colors=NUMBERS_COLOR);
		
		mean_bar.spines['bottom'].set_color(SPINE_COLOR);
		mean_bar.spines['top'].set_color(SPINE_COLOR);
		mean_bar.spines['right'].set_color(SPINE_COLOR);
		mean_bar.spines['left'].set_color(SPINE_COLOR);
		
		mean_bar.yaxis.label.set_color(SPINE_COLOR);
		mean_bar.xaxis.label.set_color(SPINE_COLOR);
		
		mean_bar.tick_params(axis='x', colors=NUMBERS_COLOR);
		mean_bar.tick_params(axis='y', colors=NUMBERS_COLOR);
		
		# a tk.DrawingArea
		canvas = FigureCanvasTkAgg(f, master=self);
		canvas.show();
		canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1);
		
		quit_button = tk.Button(master=self,
										text='Back',
										command=lambda: GraphPage.onClick(self),
										bg = BACKGROUND_COLOR,
										fg = 'white');
		
		quit_button.pack(side=tk.BOTTOM)
		
		self.__canvas = canvas;
		self.__graph = graph;
		self.__mean_bar = mean_bar;
		self.setClose(False);
		self.setGoBack(False);
		self.__iter = 0;
		
	def getCanvas(self):
		return self.__canvas;
	
	def getGraph(self):
		return self.__graph;
	
	def getMeanBar(self):
		return self.__mean_bar;
	
	def getController(self):
		return self.__controller;
	
	def getClose(self):
		with self.getLock():
			close = self.__close;
		
		return close;
	
	def setClose(self,close):
		with self.getLock():
			self.__close = close;
	
	def getLock(self):
		return self.__lock;
	
	def setLock(self,lock):
		self.__lock = lock;
	
	def getGuiLock(self):
		return self.__gui_lock;
	
	def setGuiLock(self, lock):
		self.__gui_lock = lock;
	
	def getGoBack(self):
		with self.getLock():
			go_back = self.__go_back;
		
		return go_back;
	
	def setGoBack(self, go_back):
		with self.getLock():
			self.__go_back = go_back;
	
	
	def tkraise(self):
		thread = Thread(target=GraphPage.graphRTT, args=(self,));
		self.__thread = thread;
		self.__thread.setDaemon(True);
		self.__thread.start();
		super(GraphPage, self).tkraise();
	
	@staticmethod
	def onClick(frame):
		frame.setGoBack(True);
		frame.getController().showFrame("StartPage");
	
	@staticmethod
	def onClosing(frame):
		frame.setClose(True);
	
	def stop(self):
		stop = ((self.getGoBack()) or (self.getClose()));
		self.__iter += 1;
		return stop;
	
	@staticmethod
	def graphRTT(frame):
		WINDOW_SIZE = 100;
		N_BINS = 100;
		nn = [];
		v_rtt = [];
		v_rtt_avg = [];
		v_rtt_avg_global = [];
		v_rtt_dev = [];
		v_lower_dev = [];
		v_upper_dev = [];
		v_lower_plot = [];
		v_upper_plot = [];
		n = 0;
		dr = 0.1;
		
		N_HOR = 1000;
		N_VER = 20;
		
		grad_colors = [(0.1875,0.1875,0.1875),
							(0, 164/256, 173/256)];
		
		grad_cm = matplotlib.colors.LinearSegmentedColormap.from_list(
			'grad',grad_colors,1000
		);
		
		graph = frame.getGraph();
		meanbar = frame.getMeanBar();
		canvas = frame.getCanvas();
		hostname = frame.getController().getHostname();
		
		frame.setGoBack(False);
		
		while (frame.stop()==False):
			received_response, rtt = GraphPage.ping(hostname);
			
			if(received_response):
				nn.append(n);
				v_rtt.append(rtt);
				
				n_rtt = n+1;
				window_index = n_rtt-WINDOW_SIZE if n_rtt>WINDOW_SIZE else 0;
				v_rtt_window = v_rtt[window_index:];
				
				actual_window_size = len(v_rtt_window);
				
				rtt_mov_avg = sum(v_rtt_window)/actual_window_size;
				
				if (window_index>0):
					v_rtt_avg.pop(0);
					v_rtt_dev.pop(0);
					v_lower_plot.pop(0);
					v_upper_plot.pop(0);
							
				v_rtt_avg.append(rtt_mov_avg);
				v_rtt_avg_global.append(rtt_mov_avg);
				
				#rtt_dev = sum(v_rtt_dev_local)/actual_window_size;
				#rtt_dev = 0.2*abs(rtt-rtt_mov_avg);
				
				rtt_dev = 0.4*rtt_mov_avg*(math.log10(1+(rtt/rtt_mov_avg)));
				v_rtt_dev.append(rtt_dev);
				
				rtt_dev_norm = rtt_dev - 0.9*min(v_rtt_dev);
				
				upper_plot = rtt_mov_avg + rtt_dev_norm;
				lower_plot = rtt_mov_avg - rtt_dev_norm;
				
				v_lower_plot.append(lower_plot);
				v_upper_plot.append(upper_plot);
				
				
				nn_cropped = nn[window_index:];
				
				rtt_avg_mov = sum(v_rtt_avg_global)/n_rtt;
				
				global_dev_mov = sum(map(abs,map(operator.sub,v_rtt_avg_global,rtt_avg_mov*ones(n+1))))/(n_rtt);
				
				if(global_dev_mov==0): global_dev_mov = 1;
				
				bin_min = np.floor(rtt_avg_mov - 4*global_dev_mov);
					
				if (bin_min<0): bin_min = 0;
					
				bin_max = np.ceil(rtt_avg_mov + 4*global_dev_mov);
				
				r_bins_hist = list(np.arange(bin_min,bin_max,dr));
				
				v_hist, x_bins = np.histogram(v_rtt_avg_global, r_bins_hist);
				
				v_hist = v_hist/(sum(v_hist));
				
				r_bins = list(r_bins_hist + (dr/2)*ones(len(r_bins_hist)));
				r_bins.pop();
				
				
				
				
				y_min = 0.75*min(v_rtt_avg);
				y_max = 1.25*max(v_rtt_avg);
				
				
				
				graph.clear();
				
				graph.fill_between(nn_cropped,v_lower_plot,v_upper_plot,color=FILL_COLOR);
				
				graph.plot(nn_cropped,v_rtt_avg,linewidth=2,color=PLOT_COLOR);
				graph.set_ylim([y_min, y_max]);
				
				graph.grid(linewidth=0.1,color='#FFFFFF');
				
				
				n += 1;
				
				if(n>2):
					p05 = float(np.percentile(v_rtt,1));
					p95 = float(np.percentile(v_rtt,95));
					
					xx = list(np.linspace(p05,p95,N_HOR));
					
					ux = sum(v_rtt)/(n_rtt);
					ox = float(stdev(v_rtt));
					
					meanbar.clear();
					
					cs = [];
					
					for i in range(0,N_HOR):
						x = xx[i];
						cv = abs(x-ux)/(ox);
						if (cv>1):
							cv=1;
						cv = 1-cv;
						cs.append(cv);
					
					z_bar = [];
					for j in range(0,N_VER):
						z_bar.append(cs);
					
					#meanbar.contour(X_BAR,Y_BAR,z_bar,200);
					
					x_min = float("{0:.2f}".format(p05));
					x_mean = float("{0:.2f}".format(ux));
					x_max = float("{0:.2f}".format(p95));
					
					str_min = "Perc. 1\n%.2f"%(x_min);
					str_mean  = "Mean\n%.2f"%(x_mean);
					str_max = "Perc. 95\n%.2f"%(x_max);
					
					x_ticks = [x_min, x_mean, x_max];
					str_ticks = [str_min,str_mean,str_max];
					plot_extent = [x_min,x_max,0,1];
					
					meanbar.imshow(z_bar, interpolation='nearest', cmap=grad_cm,aspect='auto',extent=plot_extent);
					meanbar.set_xticks(x_ticks);
					meanbar.set_xticklabels(str_ticks);
					meanbar.set_yticks([]);
				
				
				canvas.show();
		
	
	
	@staticmethod
	def ping(hostname):
		command = ['ping','-w','1','-n','1',hostname];
		ping_result = subprocess.run(command,stdout=subprocess.PIPE);
		ping_result_str = ping_result.stdout.decode('utf-8');
		
		rtt_stats = pingparsing.PingParsing().parse(ping_result_str);
		
		received_response = ((rtt_stats.rtt_avg is None)==False);
		
		if received_response:
			rtt = rtt_stats.rtt_avg;
		else:
			rtt = 0.0;
		
		return received_response, rtt;




