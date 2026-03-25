# ***************************************************************************
# *   Copyright (c) 2015 Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk>          *
# *   Copyright (c) 2016 Bernd Hahnebach <bernd@bimstatik.org>              *
# *   Copyright (c) 2024 PMcB                                               *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "FreeCAD result mechanical task panel"
__author__ = "Qingfeng Xia, Bernd Hahnebach"
__url__ = "https://www.freecad.org"

## @package view_result_mechanical
#  \ingroup FEM
#  \brief task panel for mechanical ResultObjectPython

import CreateLabels
import inspect, sys, os
import subprocess
import json
import threading

try:
    import matplotlib

    matplotlib.use("Qt5Agg")
except Exception:
    print("Failed to set matplotlib backend to Qt5Agg")

from PySide import QtWidgets
from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QApplication

import FreeCAD
import FreeCADGui

import femresult.resulttools as resulttools

translate = FreeCAD.Qt.translate

POSTPRO_QUANTITY = { "local_cre"   : 0,
                     "displacement": 1,
                     "strain"      : 2,
                     "stress"      : 3,
                     "vm_strain"   : 4,
                     "vm_stress"   : 5,
                     "ts_strain"   : 6,
                     "ts_stress"   : 7 }

class _TaskPanel:
    """
    The task panel for the post-processing
    """

    def __init__(self, obj):
        self.is_valid = False
        self.result_obj = obj

        doc = FreeCAD.ActiveDocument
        if not doc.FileName:
            QtWidgets.QMessageBox.information(None,
                                              "Info",
                                              "The result module is unavailable because "
                                              "this document has not been saved yet.")
            return
        
        # results available for postprocessing
        self.wdir = os.path.splitext(doc.FileName)[0]
        if not os.path.isdir(self.wdir):
            QtWidgets.QMessageBox.information(None,
                                              "Info",
                                              f"Directory not found: {self.wdir}\n"
                                              "No result file is available for "
                                              "postprocessing.")
            return
        
        result_files = []
        result_folders = [f for f in os.listdir(self.wdir) if f.startswith("result_")]
        for folder in result_folders:
            folder_path = os.path.join(self.wdir, folder)
            zst_files = [f for f in os.listdir(folder_path) if f.endswith(".zst")]
            for file in zst_files:
                result_files.append(os.path.join(folder_path, file))
        
        if len(result_files) < 1:
            QtWidgets.QMessageBox.information(None,
                                              "Info",
                                              "No result file is available for postprocessing.\n"
                                              "Please download a result file from the solver module.")
        
        self.is_valid = True

        ui_path = FreeCAD.getHomePath() + "Mod/Fem/Resources/ui/"
        self.result_widget = FreeCADGui.PySideUic.loadUi(ui_path + "ResultShow.ui")
        # self.info_widget = FreeCADGui.PySideUic.loadUi(ui_path + "ResultHints.ui")
        self.form = [self.result_widget] #, self.info_widget]

        self.fem_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fem/General")
        self.restore_result_settings_in_dialog = self.fem_prefs.GetBool("RestoreResultDialog", True)
        
        self.job_group = QtGui.QButtonGroup(self.result_widget)
        self.job_container = self.result_widget.findChild(QtGui.QWidget, "job_container")
        self.job_layout = self.job_container.layout()
        self.create_job_boxes(result_files)

        # Connect Signals and Slots
        QtCore.QObject.connect(self.result_widget.cb_local_cre,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "local_cre"),)
        QtCore.QObject.connect(self.result_widget.cb_displacement,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "displacement"),)
        QtCore.QObject.connect(self.result_widget.cb_strain,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "strain"),)
        QtCore.QObject.connect(self.result_widget.cb_stress,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "stress"),)
        QtCore.QObject.connect(self.result_widget.cb_vm_strain,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "vm_strain"),)
        QtCore.QObject.connect(self.result_widget.cb_vm_stress,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "vm_stress"),)
        QtCore.QObject.connect(self.result_widget.cb_ts_strain,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "ts_strain"),)
        QtCore.QObject.connect(self.result_widget.cb_ts_stress,
                               QtCore.SIGNAL("toggled(bool)"),
                               lambda state: self.update_request(state, "ts_stress"),)
        
        self.result_widget.postprocess.clicked.connect(self.postprocess)
        self.result_widget.visualize.clicked.connect(self.visualize)

        # Keeping this logic for potential future use
        # (e.g., restoring result settings)
        if self.restore_result_settings_in_dialog:
            self.restore_result_dialog()
        else:
            self.restore_initial_result_dialog()
    
    def create_job_boxes(self, result_files):
        while self.job_group.buttons():
            checkbox = self.job_group.buttons().pop()
            self.job_group.removeButton(checkbox)
            self.job_layout.removeWidget(checkbox)
            checkbox.deleteLater()

        self.job_group.setExclusive(False)

        for file in result_files:
            job_id = file.split("result_")[1].split("/")[0]
            relpath = f"result_{file.split("result_")[1]}"
            checkbox = QtGui.QCheckBox("Job ID: {} (file: {})".format(job_id, relpath))
            checkbox.setProperty("path", file)
            self.job_group.addButton(checkbox)
            self.job_layout.addWidget(checkbox)

        self.job_group.setExclusive(True)
    
    def get_selected_job(self):
        for box in self.job_group.buttons():
            if box.isChecked():
                return box.property("path")
        return None

    def restore_result_dialog(self):
        self.restore_initial_result_dialog()

    def restore_initial_result_dialog(self):
        FreeCAD.FEM_dialog = { "request": 8 * [False] }

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Close

    def get_result_stats(self, type_name):
        return resulttools.get_stats(self.result_obj, type_name)

    def update_request(self, state, quantity):
        FreeCAD.FEM_dialog["request"][POSTPRO_QUANTITY[quantity]] = state

    def postprocess(self):
        selected_job = self.get_selected_job()
        if not selected_job:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please select a result file.")
            return

        if not os.path.exists(selected_job):
            QtWidgets.QMessageBox.warning(None, "Warning",
                                          f"The result file {selected_job} was not found.")
            return
        
        moddir = FreeCAD.getHomePath()
        bindir = os.path.join(moddir, "bin")
        cmd = os.path.join(bindir, "SuqabaUICmd")
        script_path = f"{moddir}Mod/Fem/femsolver/suqaba/postpro_worker.py"

        args = [cmd,
                script_path,
                os.path.dirname(selected_job),
                os.path.basename(selected_job).removesuffix(".zst"),
                json.dumps(FreeCAD.FEM_dialog["request"])]

        kwargs = { "stdout": subprocess.PIPE,
                   "stderr": subprocess.STDOUT,
                   "text": True }

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        
        self.process = subprocess.Popen(args, **kwargs)
        dialog = ProgressDialog(self.process)
        dialog.exec_()
    
    def visualize(self):
        paraview_path = FreeCAD.ParamGet("User parameter:BaseApp/Suqaba/ParaView").GetString("Path")
        if not paraview_path or not os.path.isfile(paraview_path):
            QtWidgets.QMessageBox.information(None,
                                              "Info",
                                              "Please browse to the ParaView installation folder and "
                                              "select the ParaView executable file (e.g., 'paraview' "
                                              "or 'paraview.exe').")
            paraview_path, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                                     "Select ParaView Executable", 
                                                                     "",
                                                                     "Executable Files (*)")
            if not paraview_path:
                QtWidgets.QMessageBox.information(None,
                                                  "Info",
                                                  "ParaView path not set. Operation cancelled.")
                return
            
            FreeCAD.ParamGet("User parameter:BaseApp/Suqaba/ParaView").SetString("Path", paraview_path)
        
        result_path, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                               "Select VTU File",
                                                               self.wdir,
                                                               "VTU Files (*.vtu);;All Files (*)")
        if not result_path:
            QtWidgets.QMessageBox.information(None,
                                              "Info",
                                              "Result file to view not set. Operation cancelled.")
            return
        
        try:
            abs_path = os.path.abspath(result_path)
            subprocess.Popen([paraview_path, abs_path])
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Failed to launch ParaView:\n{str(e)}")

    def reject(self):
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()


class WorkerThread(QtCore.QThread):
    line_received = QtCore.Signal(str)
    progress_updated = QtCore.Signal(int)
    finished = QtCore.Signal()

    def __init__(self, process):
        super().__init__()
        self.process = process
        requests = FreeCAD.FEM_dialog["request"]
        self.total_steps = sum(1 for v in requests if v) + 3
        self.current_step = 0

    def run(self):
        for line in iter(self.process.stdout.readline, ''):
            if "Suqaba" not in line:
                self.line_received.emit(line.strip())
                self.progress_updated.emit(min(self.current_step, self.total_steps))
                self.current_step += 1
        self.finished.emit()


class ProgressDialog(QtWidgets.QDialog):

    def __init__(self, process, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Postprocessing")
        self.setMinimumWidth(500)

        layout = QtWidgets.QVBoxLayout(self)
        self.worker = WorkerThread(process)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, self.worker.total_steps)
        layout.addWidget(self.progress_bar)

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setEnabled(False)
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.accept)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.worker.line_received.connect(self.append_line)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def append_line(self, line):
        self.log.append(line)

    def on_finished(self):
        self.progress_bar.setValue(self.worker.total_steps)
        self.close_btn.setEnabled(True)

    def closeEvent(self, event):
        self.worker.quit()
        self.worker.wait()
        super().closeEvent(event)

    def reject(self):
        self.worker.quit()
        self.worker.wait()
        super().reject()
