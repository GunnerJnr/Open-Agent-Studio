from Qt import QtWidgets, QtGui
    
    

from PySide2.QtWidgets import (QWidget, QApplication, QGraphicsView,
QGridLayout, QMainWindow, QAction, QMenu, QVBoxLayout, QMenuBar, QFileDialog, QInputDialog)
from PySide2 import QtCore, QtWidgets, QtGui
import sys
from NodeGraphQt.constants import (
    NODE_SEL_BORDER_COLOR,
    VIEWER_BG_COLOR,
    VIEWER_NAV_BG_COLOR
)
from NodeGraphQt.widgets.viewer_nav import NodeNavigationWidget
from tkinter import filedialog as fd
from sneakysnek.recorder import Recorder
import math

import tkinter as tk

import imutils
import requests
import pyautogui
import json
from PIL import ImageTk, Image
from tkinter import ttk
from threading import Thread

from queue import Queue
record_tasks = Queue()

import numpy as np
import cv2
import mss
import sys

from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGHIDEventTap


import os.path





class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class NodeGraphWidget(QtWidgets.QTabWidget):
    def defExit(self):
        sys.exit()
    def saveCheat(self):
        name, save = QFileDialog.getSaveFileName(self, 'Save Cheat')
        file = open(name,'w')
        for item in self.history:
             file.write("%s\n" % (item))
        file.close()
        
    def mouseEvent(self,type, posx, posy):
        theEvent = CGEventCreateMouseEvent(
                    None, 
                    type, 
                    (posx,posy), 
                    kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, theEvent)

    def mousemove(self,posx,posy):
        self.mouseEvent(kCGEventMouseMoved, posx,posy)

    def mouseclick(self,posx,posy):
        # uncomment this line if you want to force the mouse 
        # to MOVE to the click location first (I found it was not necessary).
        #mouseEvent(kCGEventMouseMoved, posx,posy);
        self.mouseEvent(kCGEventLeftMouseDown, posx,posy)
        self.mouseEvent(kCGEventLeftMouseUp, posx,posy)
    def loopRecording(self):
        while True:
            self.runRecording() 
    def runRecording(self):
        if True:
      #  print history
            for index,y in enumerate(self.history):
                x = y
                if isinstance(x, str):
                     x = json.loads(y)
            #print(y)s
                
                for key, value in x.items()  :
                    if key == "image":
                        x["image"] = np.asarray(x["image"],dtype = "uint8")
                if x["type"] == "Move Mouse":
                    pyautogui.moveTo(x["x"], x["y"]) 
                if x["type"] == "Left Mouse Lift": 
                    pyautogui.mouseUp() 
                if x["type"] == "Left Mouse Click": 
                    img = pyautogui.screenshot(region=(x["x"]*2-self.half_small,x["y"]*2-self.half_small, self.size_small, self.size_small))
                    image =  cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                    print(x)
               # test = match(image, x["image"])
                    #cv2.imshow('test2',cv2.cvtColor(x["image"], cv2.COLOR_BGR2RGB))
                    #cv2.waitKey(1)
                    match_res = cv2.matchTemplate(cv2.cvtColor(x["image"], cv2.COLOR_BGR2RGB), image, cv2.TM_SQDIFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_res)
                    print(min_loc)
                    print(min_val)
                    if min_val < 0.01:
                        print("Success")
                        print(str(x["x"]) + "," + str(x["y"]))
                        #self.mouseclick(x["x"], x["y"])
                        pyautogui.mouseDown(x["x"], x["y"]) 
                        print("Finish click")
                    else:
                        img = pyautogui.screenshot()
                        image = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                        best_loc = None
                        best_val = 1000
                        best_scale = 1.0
                        print("FAILED")
                    	# loop over the scales of the image
                        for scale in np.linspace(0.5, 1.3, 25)[::-1]:
                            resized = cv2.resize(cv2.cvtColor(x["image"], cv2.COLOR_BGR2RGB), (int(x["image"].shape[1] * scale), int(x["image"].shape[0] * scale)), interpolation = cv2.INTER_AREA)

                            ##cv2.imshow('image',image)
                            #cv2.waitKey(1)
                            match_res = cv2.matchTemplate(image, resized,  cv2.TM_SQDIFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_res)
                            if min_val < best_val:
                                best_val = min_val
                                best_loc = min_loc
                                best_scale = scale
                            print(str(best_val) + ":" +str(best_scale))
                            print(best_loc)
                            
                        #cv2.rectangle(image, (best_loc[0], best_loc[1]), (best_loc[0] + 50, best_loc[1] + 50), (255,0,0), 2)
                        #cv2.imshow('resized',image)

                        #cv2.waitKey(1)
                    #print("SUPER MATCH")
                        if best_val  < .05:
                            #self.mouseclick(best_loc[0] + self.half_small*best_scale, best_loc[1] + self.half_small*best_scale)
                            print("SUPER MATCH" + str(best_val))
                            print(str(best_loc[0]) )
                            print(str(best_loc[1]) )

                            pyautogui.mouseDown(math.floor(best_loc[0]/2 + 25*best_scale/2), math.floor(best_loc[1]/2 + 25*best_scale/2))
                         #  offsetX = x["x"] - max_loc[0] + 25
                         #  offsetY = x["y"] - max_loc[1] + 25
                if x["type"] == "keypressup":
                    if "shift" in str(x["key"]).split("KEY_")[1].lower():
                        pyautogui.keyUp("shift")
                        self.shift_down = False
                if x["type"] == "keypress":
                    if True:
                        if "backspace" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.press('backspace')
                        elif "space" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.write(" ", interval=0.05) 
                        elif "period" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.write(".", interval=0.05) 
                        elif "slash" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.write("/", interval=0.05) 
                        elif "return" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.press('enter')
                        elif "shift" in str(x["key"]).split("KEY_")[1].lower():
                            pyautogui.keyDown("shift")
                            self.shift_down = True
                        else:
                            if self.shift_down:
                                pyautogui.write(str(x["key"]).split("KEY_")[1].upper(), interval=0.05) 
                            else:
                                pyautogui.write(str(x["key"]).split("KEY_")[1].lower(), interval=0.05)

    #button7location = pyautogui.locateOnScreen('tweet.png')asdfas asdfasdf    asdfasdf   
    #print(button7location)asdfassddss
    #button7point = pyautogui.center(button7location)asdfasdf
    
    #button7x, button7y = button7point
    #pyautogui.click(button7x, button7y)  # clicks the center of where the 7 button was found
    #pyautogui.click('tweet.png') # a shortcut version to click on the center of where the 7 button was found
    
    # Some blocking code in your main thread...

    def eventRecord(self, event):        
   # print(len(history))
        print(event)
        if "MOVE" in str(event.event):
            self.mouse_counter += 1
            if self.mouse_counter%6 == 0:
                self.history.append(json.dumps({"type":"Move Mouse", "x": int(event.x), "y": int(event.y)}, cls=NumpyEncoder))      
        if "CLICK" in str(event.event) and "DOWN" in str(event.direction):
            self.history.append(json.dumps({"type":"Left Mouse Click", "x": int(event.x), "y": int(event.y), "image": np.array(pyautogui.screenshot(region=(event.x*2 - 25 ,event.y*2 - 25, 50, 50)))}, cls=NumpyEncoder))  
        if "CLICK" in str(event.event) and "UP" in str(event.direction):
            self.history.append(json.dumps({"type":"Left Mouse Lift", "x": int(event.x), "y": int(event.y)}, cls=NumpyEncoder))  
    #    if stop == False:
        if "KeyboardEvent" in str(event.event) and "UP" in str(event.event):
            self.history.append(json.dumps({"type":"keypressup", "key": str(event.keyboard_key)}, cls=NumpyEncoder))  
        if "KeyboardEvent" in str(event.event) and "DOWN" in str(event.event):
            if "KEY_ESCAPE" in str(event.keyboard_key):
            #stopRecording()
            #reco
                
                print("STOP")
                self.stopAction.trigger()
            #record_tasks.put("stop")
            #redrawHistory() 
            #if "PRINT" in str(event.keyboard_key):
            #stopRecording()
            #reco
                #newWindow = tk.Toplevel(window)
    
                #newWindow.title("Edit Event" + n)
                #step = json.loads(history[int(n)])   
                #newWindow.geometry("1000x800")
                #img = pyautogui.screenshot()
                #image = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            
            #window.event_generate("<<stop>>", when="tail", state=123)
            #record_tasks.put("stop")
            #redrawHistory() 
            else:  
                self.history.append(json.dumps({"type":"keypress", "key": str(event.keyboard_key)}, cls=NumpyEncoder))  
      
    def openCheat(self):
        f,_ = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Cheat Files (*.cheat)")
        with open(f) as file:
            self.history = file.readlines()
            self.drawHistory(self.history)
    def stopRecording(self):
        if self.started:
            self.recorder.stop()
            self.drawHistory(self.history)
            self.showMaximized()
        self.started = False

    def playRecording(self):
        print("play")
        self.showMinimized()

        self.runRecording()   
    def newCheat(self):
        self.history = []
        self.drawHistory(self.history)
    
    def startRecording(self):
        if self.started == False:
            self.started = True
            self.showMinimized()
            self.counter = 0
            self.bnt = 0
            self.recorder = Recorder.record(self.eventRecord)
    def defineMenu(self):
        self.myQMenuBar = QMenuBar(self)
        exitMenu = self.myQMenuBar.addMenu('File')
        
          
        self.stopAction = QAction('Stop Recording (ESC)', self)  
        self.stopAction.triggered.connect(self.stopRecording)
        
        startAction = QAction('Schedule Recording', self)  
        startAction.triggered.connect(self.startRecording)
        
        
        saveAction = QAction('Save', self)  
        saveAction.triggered.connect(self.saveCheat)

        
        loopAction = QAction('Loop', self)  
        loopAction.triggered.connect(self.loopRecording)

        startAction = QAction('Start Recording', self)  
        startAction.triggered.connect(self.startRecording)

        

        
        playAction = QAction('Play', self)  
        playAction.triggered.connect(self.playRecording)

        openAction = QAction('Open', self)  
        openAction.triggered.connect(self.openCheat)



        exitMenu.addAction(openAction)
        exitMenu.addAction(playAction)
        exitMenu.addAction(loopAction)
        exitMenu.addAction(saveAction)
        exitMenu.addAction(startAction)

        exitMenu.addAction(self.stopAction)

        exitAction = QAction('Exit', self)  
        exitAction.triggered.connect(self.defExit)
 
        exitMenu.addAction(exitAction)
        self.myQMenuBar.show()
    
    def __init__(self,drawHistory, verified, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabBarAutoHide(True)
        self.verified = verified
        self.setWindowTitle('Cheat Layer')
        self.drawHistory = drawHistory
        self.mouse_counter = 0
        self.history = []
        self.half_small = 25
        self.shift_down = False
        self.started = False
        self.size_small = 50
        self.half = 25
        self.size = 50
        text_color = self.palette().text().color().toTuple()
        bg_color = QtGui.QColor(*VIEWER_BG_COLOR).darker(120).toTuple()
        style_dict = {
            'QWidget': {
                'background-color': 'rgb({0},{1},{2})'.format(*VIEWER_BG_COLOR),
            },
            'QTabWidget::pane': {
                'background': 'rgb({0},{1},{2})'.format(*VIEWER_BG_COLOR),
                'border': '0px',
                'border-top': '0px solid rgb({0},{1},{2})'.format(*bg_color),
            },
            'QTabBar::tab': {
                'background': 'rgb({0},{1},{2})'.format(*bg_color),
                'border': '0px solid black',
                'color': 'rgba({0},{1},{2},30)'.format(*text_color),
                'min-width': '10px',
                'padding': '10px 20px',
            },
            'QTabBar::tab:selected': {
                'color': 'rgb({0},{1},{2})'.format(*text_color),
                'background': 'rgb({0},{1},{2})'.format(*VIEWER_NAV_BG_COLOR),
                'border-top': '1px solid rgb({0},{1},{2})'
                              .format(*NODE_SEL_BORDER_COLOR),
            },
            'QTabBar::tab:hover': {
                'color': 'rgb({0},{1},{2})'.format(*text_color),
                'border-top': '1px solid rgb({0},{1},{2})'
                              .format(*NODE_SEL_BORDER_COLOR),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        self.setStyleSheet(stylesheet)

    def add_viewer(self, viewer, name, node_id):
        self.addTab(viewer, name)
        index = self.indexOf(viewer)
        self.setTabToolTip(index, node_id)
        self.setCurrentIndex(index)

    def remove_viewer(self, viewer):
        index = self.indexOf(viewer)
        self.removeTab(index)


class SubGraphWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, graph=None):
        super(SubGraphWidget, self).__init__(parent)
        self._graph = graph
        self._navigator = NodeNavigationWidget()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)
        self._layout.addWidget(self._navigator)

        self._viewer_widgets = {}
        self._viewer_current = None

    @property
    def navigator(self):
        return self._navigator

    def add_viewer(self, viewer, name, node_id):
        if viewer in self._viewer_widgets:
            return

        if self._viewer_current:
            self.hide_viewer(self._viewer_current)

        self._navigator.add_label_item(name, node_id)
        self._layout.addWidget(viewer)
        self._viewer_widgets[viewer] = node_id
        self._viewer_current = viewer
        self._viewer_current.show()

    def remove_viewer(self, viewer=None):
        if viewer is None and self._viewer_current:
            viewer = self._viewer_current
        node_id = self._viewer_widgets.pop(viewer)
        self._navigator.remove_label_item(node_id)
        self._layout.removeWidget(viewer)
        viewer.deleteLater()

    def hide_viewer(self, viewer):
        self._layout.removeWidget(viewer)
        viewer.hide()

    def show_viewer(self, viewer):
        if viewer == self._viewer_current:
            self._viewer_current.show()
            return
        if viewer in self._viewer_widgets:
            if self._viewer_current:
                self.hide_viewer(self._viewer_current)
            self._layout.addWidget(viewer)
            self._viewer_current = viewer
            self._viewer_current.show()