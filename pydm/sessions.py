import os
import json
import inspect
import psutil
import subprocess
from qtpy.QtWidgets import QWidget, QMenu, QAction, QMainWindow, QFileDialog
from qtpy.QtGui import QIcon
from .main_window import PyDMMainWindow


class Session(QMainWindow):
    """
    Session adds a save and load sessions to the file section of main_window's top menu bar.
    also provides the logic for saving a selection of PyDM widgets in a json file and then loading previously saved
    sessions.

    Parameters
    ----------
    main_window_widget : QWidget

    ui_file : str, optional
        The file path to a PyDM display file (.ui, .py, or .adl).

    """
    def __init__(self, parent=None, ui_file=None):
        super(Session, self).__init__(parent)
        self.ui_file = ui_file

        self.button = []
        self.tool_bar_actions = ["Load", "Save"]
        self.tool_bar_methods = [self.load, self.save]

        for element in range(len(self.tool_bar_actions)):
            self.button.append(element)
            self.button[element] = QAction(self.tool_bar_actions[element], self)
            # self.button[element].setStatusTip("This is your button")
            self.button[element].triggered.connect(self.tool_bar_methods[element])

        # Flag to check if 'File' already exists in the menu bar.
        exist = False

        for name in parent.menuBar().actions():
            if name.text() == "File":  # Should be &File
                exist = True
                break

        if not exist:
            self.file_menu = QMenu("&File", self)
        else:
            self.file_menu = parent.menuBar().actions("&File")  # error here

        for menu_element in self.button:
            self.file_menu.addAction(menu_element)

        parent.menuBar().addMenu(self.file_menu)

    def load(self):
        """
        Given a JSON file, returns a python dictionary of the contents of the JSON.

        Parameters
        ----------
        """
        print("load")

        try:
            filename = QFileDialog.getOpenFileName()
        except valueError:
            return

        if filename is None:
            return

        with open(filename[0]) as file:
            json_data = json.load(file)

        print(type(json_data))

        for elements in json_data:
            stylesheet_path = elements[0]
            ui_file = elements[1]
            macros = elements[2]
            command_line_args = elements[3]

            self.make_main_window(stylesheet_path=stylesheet_path)
            # self.main_window.move()
            self.main_window.open(ui_file, macros, command_line_args)

    def save(self):
        """

        Parameters
        ----------

        """

        proc = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).stdout.readlines()
        print(type(proc[0]), proc[0])
        res = [i for i in proc if 'pydm' in i]
        print(res)
        # Get Generator object containing all running processes
        process_iterator = psutil.process_iter()

        # Iterate over Generator object to get
        # each process object contained by it
        '''
        for proc in psutil.process_iter(['pid', 'name', 'username']):
           print(proc.info)
        '''

        save_data_dict = {}
        filename = None

        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save PyQT Session", "", "JSON (*.json)")
        except valueError:
            return  # need error here?

        print(filename)
        if filename is None or filename == "":
            return  # need error here?

        with open(filename, "w") as file:
            json.dump(save_data_dict, file)

        print("save")
