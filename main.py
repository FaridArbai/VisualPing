import tkinter as tk
from tkinter import ttk
from tkinter import font  as tkfont

from graphpage import GraphPage

FRAME_WIDTH		= 600;
FRAME_HEIGHT 	= 700;

BUTTON_HEIGHT = 50;
BUTTON_WIDTH = 150;

BACKGROUND_COLOR = "#292929";

BUTTON_COLOR = "#303030";
TEXT_COLOR = 	"#c6c6c6";


class GUI(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs);
		
		self.__frames = {};
		self.__hostname = None;
		
		self.minsize(width=FRAME_WIDTH, height=FRAME_HEIGHT);
		self.configure(background=BACKGROUND_COLOR);
		
		container = tk.Frame(self);
		container.pack(side="top", fill="both", expand=True);
		container.grid_rowconfigure(0, weight=1);
		container.grid_columnconfigure(0, weight=1);
		
		for page in (StartPage, GraphPage):
			page_name = page.__name__;
			frame = page(parent=container, controller=self);
			self.__frames[page_name] = frame;
			frame.grid(row=0, column=0, sticky="nsew");
		
		self.showFrame(StartPage.__name__);

	def showFrame(self, page_name):
		frame = self.__getFrame(page_name);
		frame.tkraise();
		
	def __getFrame(self, page_name):
		frames = self.__getFrames();
		frame = frames[page_name];
		return frame;
		
	def __getFrames(self):
		frames = self.__frames;
		return frames;
	
	def setHostname(self,hostname):
		self.__hostname = hostname;
	
	def getHostname(self):
		return self.__hostname;

class StartPage(tk.Frame):
	HOSTNAME_HEIGHT = 35;
	HOSTNAME_WIDTH = 150;
	
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		self.__controller = controller
		
		self.configure(background=BACKGROUND_COLOR);
		
		hostname_entry = tk.Entry(master = self,
										  justify = 'center',
										  bg = BUTTON_COLOR,
										  fg = TEXT_COLOR);
		
		hostname_entry.insert(0,'www.facebook.com');
		
		hostname_entry.place(relx = 0.5,
								 rely = 0.5,
								 height = StartPage.HOSTNAME_HEIGHT,
								 width = StartPage.HOSTNAME_WIDTH,
								 anchor = tk.CENTER);
		
		parent.style = ttk.Style();
		
		parent.style.configure("TButton", foreground='white');
		parent.style.configure("TButton", background=BACKGROUND_COLOR);
		
		graph_button = tk.Button(master=self,
										text="Visualize RTT",
										command=lambda: self.__startRTT(hostname_entry),
										bg = BUTTON_COLOR,
										fg = TEXT_COLOR);
		
		graph_button.place(relx = 0.5,
								 rely = 0.7,
								 height = BUTTON_HEIGHT,
								 width = BUTTON_WIDTH,
								 anchor = tk.CENTER);
		
		
	
	def __startRTT(self, hostname_entry):
		controller = self.__getController();
		hostname = hostname_entry.get();
		controller.setHostname(hostname);
		controller.showFrame(GraphPage.__name__);
	
	def __getController(self):
		return self.__controller;


if __name__ == "__main__":
	app = GUI()
	app.mainloop()