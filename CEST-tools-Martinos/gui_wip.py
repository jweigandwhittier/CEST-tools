#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 17:40:13 2023

@author: jonah
"""
import os
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import ttk

class Ui(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.load_button = tk.Button(self, text = "Load Data", height=6, width=12)

        self.correction_button = tk.Button(self, text = "B0 Correction", height=6, width=12)

        self.roi_label = tk.Label(self, text = "ROI Selection", height=3, width=12)
        self.roi_button_1 = tk.Button(self, text = "Manual", height=3, width=6)
        self.roi_button_2 = tk.Button(self, text = "AI", height=3, width=6)

        self.fit_label = tk.Label(self, text = "Lorentzian Fitting", height=3, width=12)
        self.fit_button_1 = tk.Button(self, text = "2-Step", height=3, width=6)
        self.fit_button_2 = tk.Button(self, text = "AI", height=3, width=6)

        self.calc_button = tk.Button(self, text = "Calculate Concentrations", height=6, width=18)

        self.load_button.grid(row=0, column=0, columnspan=2, pady=5)
        self.correction_button.grid(row=1, column=0, columnspan=2, pady=5)
        self.roi_label.grid(row=2, column=0, columnspan=2, pady=(5,0))
        self.roi_button_1.grid(row=3, column=0)
        self.roi_button_2.grid(row=3, column=1)
        self.fit_label.grid(row=4, column=0, columnspan=2, pady=(5,0))
        self.fit_button_1.grid(row=5, column=0)
        self.fit_button_2.grid(row=5, column=1)
        self.calc_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.grid(padx=10, pady=10, sticky=tk.NSEW)
        
class Images(tk.Frame,):
    def __init__(self, parent, name, data):
        tk.Label(self, text=name)
        
        f = Figure(figsize=(5,5))
        a = f.add_subplot(111)
        a.imshow(data)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        path = os.getcwd()
        icon = tk.Image('photo', file=path+'/resources/icons/icon.png')
        
        self.title("Jonah's CEST Tools")        
        self.geometry("220x625")
        self.iconphoto(True, icon)
        self.resizable(False,False)
        
if __name__ == "__main__":
    app = App()
    Ui(app)
    app.mainloop
