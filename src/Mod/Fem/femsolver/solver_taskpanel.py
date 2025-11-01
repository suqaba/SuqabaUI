# ***************************************************************************
# *   Copyright (c) 2017 Markus Hovorka <m.hovorka@live.de>                 *
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

__title__ = "FreeCAD FEM solver job control task panel"
__author__ = "Markus Hovorka"
__url__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import os
import subprocess

from PySide import QtCore, QtGui, QtWidgets

import FreeCAD
import FreeCADGui as Gui

import femsolver.report
import femsolver.run

from decouple import config


_UPDATE_INTERVAL = 50
_REPORT_TITLE = "Run Report"
_REPORT_ERR = "Failed to run. Please try again after all of the following errors are resolved."


class ControlTaskPanel(QtCore.QObject):

    machineChanged = QtCore.Signal(object)
    machineStarted = QtCore.Signal(object)
    machineStopped = QtCore.Signal(object)
    machineStatusChanged = QtCore.Signal(str)
    # machineJobBoxChanged = QtCore.Signal(list)
    machineStatusCleared = QtCore.Signal()
    machineStateChanged = QtCore.Signal(float)

    def __init__(self, machine):
        super().__init__()
        self.form = ControlWidget()
        self._machine = None

        # Connect object to widget.
        self.form.writeClicked.connect(self.write)
        self.form.runClicked.connect(self.run)
        self.form.fetchClicked.connect(self.fetch)
        self.form.pullClicked.connect(self.pull)
        self.form.cancelClicked.connect(self.cancel)
        self.form.removeClicked.connect(self.remove)
        self.form.postproClicked.connect(self.postpro)
        self.form.authClicked.connect(self.auth)
        self.form.abortClicked.connect(self.abort)
        self.form.directoryChanged.connect(self.updateMachine)

        # Seems that the task panel does not get destroyed. Disconnect
        # as soon as the widget of the task panel gets destroyed.
        self.form.destroyed.connect(self._disconnectMachine)
        # self.form.destroyed.connect(
        #     lambda: self.machineStatusChanged.disconnect(
        #         self.form.appendStatus))

        # Connect all proxy signals.
        self.machineStarted.connect(self.form.updateState)
        self.machineStopped.connect(self._displayReport)
        self.machineStopped.connect(self.form.updateState)
        self.machineStatusChanged.connect(self.form.appendStatus)
        self.machineStatusCleared.connect(self.form.clearStatus)
        # self.machineJobBoxChanged.connect(self.form.createJobBoxes)
        self.machineStateChanged.connect(lambda: self.form.updateState(self.machine))

        # Set initial machine. Signal updates the widget.
        self.machineChanged.connect(self.updateWidget)
        self.form.destroyed.connect(lambda: self.machineChanged.disconnect(self.updateWidget))

        self.machine = machine

    @property
    def machine(self):
        return self._machine

    @machine.setter
    def machine(self, value):
        self._connectMachine(value)
        self._machine = value
        self.machineChanged.emit(value)

    @QtCore.Slot()
    def write(self):
        self.machine._state = femsolver.run.PREPARE
        self.machine.target = femsolver.run.PREPARE
        self.machine.start()

    @QtCore.Slot()
    def run(self):
        self.machine._state = femsolver.run.SOLVE
        self.machine.target = femsolver.run.SOLVE
        self.machine.solve.finished.connect(self.form.createJobBoxes)
        self.machine.solve.need_auth.connect(self.form.enableAuth)
        self.machine.auth_check.do_check = False
        self.machine.auth_check.slv_status.connect(self.form.solveStatus)
        self.machine.auth_check.slv_status.disconnect()
        self.machine.solve.slv_status.connect(self.form.solveStatus)
        self.machine.solve.slv_status.disconnect()
        self.machine.solve.slv_status.connect(self.form.solveStatus)
        self.machine.start()

    @QtCore.Slot()
    def fetch(self):
        self.machine._state = femsolver.run.FETCH
        self.machine.target = femsolver.run.FETCH
        self.machine.fetch.finished.connect(self.form.createJobBoxes)
        self.machine.fetch.need_auth.connect(self.form.enableAuth)
        self.machine.start()

    @QtCore.Slot()
    def pull(self):
        selected_job = self.get_selected_job()

        self.machine._state = femsolver.run.RESULTS
        self.machine.target = femsolver.run.RESULTS
        self.machine.results.job_id = selected_job
        self.machine.results.need_auth.connect(self.form.enableAuth)
        self.machine.start()
    
    @QtCore.Slot()
    def cancel(self):
        selected_job = self.get_selected_job()

        if selected_job:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setWindowTitle("Cancel Job")
            msg_box.setText(f"Are you sure you want to cancel job {selected_job[:8]}?")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.No)

        if selected_job == None or msg_box.exec() == QtWidgets.QMessageBox.Yes:
            self.machine._state = femsolver.run.CANCEL
            self.machine.target = femsolver.run.CANCEL
            self.machine.cancel.job_id = selected_job
            self.machine.cancel.finished.connect(self.form.createJobBoxes)
            self.machine.cancel.need_auth.connect(self.form.enableAuth)
            self.machine.start()
    
    @QtCore.Slot()
    def remove(self):
        selected_job = self.get_selected_job()

        if selected_job:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setWindowTitle("Remove Job")
            msg_box.setText(f"Are you sure you want to remove job {selected_job[:8]} from your cloud storage?")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.No)

        if selected_job == None or msg_box.exec() == QtWidgets.QMessageBox.Yes:
            self.machine._state = femsolver.run.REMOVE
            self.machine.target = femsolver.run.REMOVE
            self.machine.remove.job_id = selected_job
            self.machine.remove.finished.connect(self.form.createJobBoxes)
            self.machine.remove.need_auth.connect(self.form.enableAuth)
            self.machine.start()
    
    @QtCore.Slot()
    def postpro(self, mode):
        if mode == "view":
            paraview_path = FreeCAD.ParamGet("User parameter:BaseApp/Suqaba/ParaView").GetString("Path")
            if not paraview_path or not os.path.isfile(paraview_path):
                paraview_path, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                                        "Select ParaView Executable", 
                                                                        "",
                                                                        "Executable Files (*)")
                if not paraview_path:
                    QtWidgets.QMessageBox.information(None, "Info", "ParaView path not set. Operation cancelled.")
                    return
                FreeCAD.ParamGet("User parameter:BaseApp/Suqaba/ParaView").SetString("Path", paraview_path)
            
            result_path, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                                   "Select VTU File",
                                                                   "",
                                                                   "VTU Files (*.vtu);;All Files (*)")
            if not result_path:
                QtWidgets.QMessageBox.information(None, "Info", "Result file to view not set. Operation cancelled.")
                return
            
            try:
                abs_path = os.path.abspath(result_path)
                subprocess.Popen([paraview_path, abs_path])
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Error", f"Failed to launch ParaView:\n{str(e)}")
            
            return
            
        selected_job = self.get_selected_job()
        if not selected_job:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please select a job first.")
            return

        input_file = os.path.join(self.machine.directory,
                                f"result_{selected_job[:8]}")
        if not os.path.exists(input_file):
            QtWidgets.QMessageBox.warning(None, "Warning",
                                          f"Selected job '{selected_job}' was not found in {self.machine.directory}.")
            return

        self.machine._state = femsolver.run.POSTPRO
        self.machine.target = femsolver.run.POSTPRO
        self.machine.postpro.mode = mode
        self.machine.postpro.job_id = selected_job
        self.machine.postpro.input_file = input_file
        self.machine.postpro.postpro_request = self.get_selected_quantities()
        self.machine.postpro.need_auth.connect(self.form.enableAuth)
        self.machine.start()
        
    
    @QtCore.Slot()
    def auth_check(self):
        self.machine._state = femsolver.run.AUTHCHK
        self.machine.target = femsolver.run.AUTHCHK
        self.machine.auth_check.finished.connect(self.form.checkIn)
        self.machine.solve.do_check = False
        self.machine.solve.slv_status.connect(self.form.solveStatus)
        self.machine.solve.slv_status.disconnect()
        self.machine.auth_check.slv_status.connect(self.form.solveStatus)
        self.machine.auth_check.slv_status.disconnect()
        self.machine.auth_check.slv_status.connect(self.form.solveStatus)
        self.machine.start()
    
    @QtCore.Slot()
    def auth(self):
        self.machine.auth.email = self.form.email_text.text().lower()
        self.machine.auth.pswrd = self.form.password_text.text()
        self.machine._state = femsolver.run.AUTH
        self.machine.target = femsolver.run.AUTH
        self.machine.auth.finished.connect(self.form.checkIn)
        self.machine.start()

    @QtCore.Slot()
    def abort(self):
        self.machine.abort()

    @QtCore.Slot()
    def updateWidget(self):
        self.form.setDirectory(self.machine.directory)
        self.form.setStatus(self.machine.status)
        self.auth_check()
        self.form.updateState(self.machine)

    @QtCore.Slot()
    def updateMachine(self):
        if self.form.directory() != self.machine.directory:
            self.machine = femsolver.run.getMachine(self.machine.solver, self.form.directory())
    
    @QtCore.Slot(object)
    def _displayReport(self, machine):
        text = _REPORT_ERR if machine.failed else None
        femsolver.report.display(machine.report, _REPORT_TITLE, text)

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Close

    def reject(self):
        Gui.ActiveDocument.resetEdit()

    def _connectMachine(self, machine):
        self._disconnectMachine()
        machine.signalStatus.add(self._statusProxy)
        machine.signalStatusCleared.add(self._statusClearedProxy)
        machine.signalStarted.add(self._startedProxy)
        machine.signalStopped.add(self._stoppedProxy)
        machine.signalState.add(self._stateProxy)

    def _disconnectMachine(self):
        if self.machine is not None:
            self.machine.auth_check.do_check = False
            self.machine.solve.do_check = False
            self.machine.signalStatus.remove(self._statusProxy)
            self.machine.signalStatusCleared.add(self._statusClearedProxy)
            self.machine.signalStarted.remove(self._startedProxy)
            self.machine.signalStopped.remove(self._stoppedProxy)
            self.machine.signalState.remove(self._stateProxy)

    def _startedProxy(self):
        self.machineStarted.emit(self.machine)

    def _stoppedProxy(self):
        self.machineStopped.emit(self.machine)

    def _statusProxy(self, line):
        self.machineStatusChanged.emit(line)

    def _statusClearedProxy(self):
        self.machineStatusCleared.emit()

    def _stateProxy(self):
        state = self.machine.state
        self.machineStateChanged.emit(state)

    def get_selected_job(self):
        for box in self.form.job_group.buttons():
            if box.isChecked():
                return box.property("job_id")
        return None
    
    def get_selected_quantities(self):
        selection = []
        for box in self.form.postpro_group.buttons():
            selection.append(box.isChecked())
        return selection


class ControlWidget(QtGui.QWidget):

    writeClicked = QtCore.Signal()
    runClicked = QtCore.Signal()
    fetchClicked = QtCore.Signal()
    pullClicked = QtCore.Signal()
    cancelClicked = QtCore.Signal()
    removeClicked = QtCore.Signal()
    postproClicked = QtCore.Signal(str)
    authClicked = QtCore.Signal()
    abortClicked = QtCore.Signal()
    directoryChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()

    def _setupUi(self):
        self.setWindowTitle(self.tr("Solver Control"))
        
        # User authentication group box
        self.email_text = QtGui.QLineEdit()
        self.email_text.setPlaceholderText("Email")
        self.password_text = QtGui.QLineEdit()
        self.password_text.setPlaceholderText("Password")
        self.password_text.setEchoMode(QtGui.QLineEdit.Password)

        self.auth_btt = QtGui.QPushButton("Log in")
        self.auth_btt.clicked.connect(self.authClicked)
        self.password_text.returnPressed.connect(self.auth_btt.click)

        auth_lyt = QtGui.QVBoxLayout()
        auth_lyt.addWidget(self.email_text)
        auth_lyt.addWidget(self.password_text)
        auth_lyt.addWidget(self.auth_btt)

        self.auth_group = QtGui.QGroupBox()
        self.auth_group.setTitle("Authentication")
        self.auth_group.setLayout(auth_lyt)
        self.auth_group.hide()

        # Working directory group box
        self._directoryTxt = QtGui.QLineEdit()
        self._directoryTxt.editingFinished.connect(self.directoryChanged)
        directoryBtt = QtGui.QToolButton()
        directoryBtt.setText("...")
        directoryBtt.clicked.connect(self._selectDirectory)
        directoryLyt = QtGui.QHBoxLayout()
        directoryLyt.addWidget(self._directoryTxt)
        directoryLyt.addWidget(directoryBtt)
        self._directoryGrp = QtGui.QGroupBox()
        self._directoryGrp.setTitle(self.tr("Working directory"))
        self._directoryGrp.setLayout(directoryLyt)

        # Preprocessing group box
        self.prepro_group = QtGui.QGroupBox("Preprocessing")
        prepro_layout = QtGui.QHBoxLayout()

        self._writeBtt = QtGui.QPushButton(self.tr("Write"))
        self._runBtt = QtGui.QPushButton("Submit")
        prepro_layout.addWidget(self._writeBtt)
        prepro_layout.addWidget(self._runBtt)
        self._writeBtt.clicked.connect(self.writeClicked)

        self.prepro_group.setLayout(prepro_layout)

        # Job controls group box
        self.job_controls = QtGui.QGroupBox("Job Controls")

        self.job_container = QtGui.QWidget()
        self.job_layout = QtGui.QVBoxLayout(self.job_container)
        self.job_group = QtGui.QButtonGroup()

        self.job_scroll = QtGui.QScrollArea()
        self.job_scroll.setWidgetResizable(True)
        self.job_scroll.setWidget(self.job_container)
        self.job_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.job_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.job_scroll.setFixedHeight(100)

        # Job action buttons
        self._fetchBtt = QtGui.QPushButton("Refresh")
        self._pullBtt = QtGui.QPushButton("Download")
        self._cancelBtt = QtGui.QPushButton("Cancel")
        self._removeBtt = QtGui.QPushButton("Remove")

        self._fetchBtt.clicked.connect(self.fetchClicked)
        self._pullBtt.clicked.connect(self.pullClicked)
        self._cancelBtt.clicked.connect(self.cancelClicked)
        self._removeBtt.clicked.connect(self.removeClicked)

        jobCtrl_layout = QtGui.QVBoxLayout()

        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addWidget(self._fetchBtt)
        btn_layout.addWidget(self._pullBtt)
        btn_layout.addWidget(self._cancelBtt)
        btn_layout.addWidget(self._removeBtt)

        jobCtrl_layout.addLayout(btn_layout)
        jobCtrl_layout.addWidget(self.job_scroll)
        self.job_controls.setLayout(jobCtrl_layout)

        # Postprocessing group box
        self.postpro_groupbox = QtGui.QGroupBox("Postprocessing")
        self.postpro_layout = QtGui.QVBoxLayout(self.postpro_groupbox)
        self.postpro_group = QtGui.QButtonGroup()
        self.postpro_group.setExclusive(False)

        self.postpro_checkboxes = {}
        for label in femsolver.run.POSTPRO_QUANTITY.keys():
            checkbox = QtGui.QCheckBox(label)
            self.postpro_group.addButton(checkbox)
            self.postpro_layout.addWidget(checkbox)
            self.postpro_checkboxes[label] = checkbox

        # Postprocess buttons
        self._postproPreviewBtt = QtGui.QPushButton("Postpro (preview)")
        self._postproHighBtt = QtGui.QPushButton("Postpro (standard)")
        self._viewBtt = QtGui.QPushButton("View")

        self._postproPreviewBtt.clicked.connect(lambda: self.postproClicked.emit("preview"))
        self._postproHighBtt.clicked.connect(lambda: self.postproClicked.emit("high_fidelity"))
        self._viewBtt.clicked.connect(lambda: self.postproClicked.emit("view"))

        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self._postproPreviewBtt)
        button_layout.addWidget(self._postproHighBtt)
        button_layout.addWidget(self._viewBtt)

        self.postpro_layout.addLayout(button_layout)
        
        # Solver status log
        self._statusEdt = QtGui.QPlainTextEdit()
        self._statusEdt.setReadOnly(True)
        self._statusEdt.setMinimumHeight(250)
        self._statusEdt.setMaximumHeight(280)
        status_lyt = QtGui.QVBoxLayout()
        status_lyt.addWidget(self._statusEdt)
        self.log_group = QtGui.QGroupBox("General logs")
        self.log_group.setLayout(status_lyt)

        self.solverStatus = QtGui.QPlainTextEdit()
        self.solverStatus.setReadOnly(True)
        self.solverStatus.setMinimumHeight(70)
        self.solverStatus.setMaximumHeight(80)
        live_lyt = QtGui.QVBoxLayout()
        live_lyt.addWidget(self.solverStatus)
        self.live_group = QtGui.QGroupBox("Job live status")
        self.live_group.setLayout(live_lyt)

        # Main layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.auth_group)
        layout.addWidget(self._directoryGrp)
        layout.addWidget(self.prepro_group)
        layout.addWidget(self.log_group)
        layout.addWidget(self.live_group)
        layout.addWidget(self.job_controls)
        layout.addWidget(self.postpro_groupbox)
        self.setLayout(layout)

    @QtCore.Slot(str)
    def setStatus(self, text):
        if text is None:
            text = ""
        self._statusEdt.setPlainText(text)
        self._statusEdt.moveCursor(QtGui.QTextCursor.End)

    @QtCore.Slot(list)
    def createJobBoxes(self, jobs):
        while self.job_group.buttons():
            checkbox = self.job_group.buttons().pop()
            self.job_group.removeButton(checkbox)
            self.job_layout.removeWidget(checkbox)
            checkbox.deleteLater()
    
        self.job_group.setExclusive(False)
        
        n_jobs = len(jobs)
        for i, job in enumerate(jobs):
            checkbox = QtGui.QCheckBox("Job {} ({}, {}, ID: {:.8s})".format(n_jobs - i, *job))
            checkbox.setProperty("job_id", job[2])
            self.job_group.addButton(checkbox)
            self.job_layout.addWidget(checkbox)

        self.job_group.setExclusive(True)
    
    @QtCore.Slot(int)
    def checkIn(self, status):
        if status == 0:
            self.auth_btt.setText("Log in")
            self.auth_btt.setDisabled(False)
            self.email_text.setDisabled(False)
            self.email_text.show()
            self.password_text.setDisabled(False)
            self.password_text.show()
            self.auth_group.show() 
        else:
            self.email_text.setText("")
            self.password_text.setText("")
            self.email_text.setDisabled(True)
            self.email_text.hide()
            self.password_text.setDisabled(True)
            self.password_text.hide()
            self.auth_btt.setText("Log out")
            self.auth_group.hide()

    def status(self):
        return self._statusEdt.plainText()

    @QtCore.Slot(str)
    def appendStatus(self, line):
        self._statusEdt.moveCursor(QtGui.QTextCursor.End)
        self._statusEdt.insertPlainText(line)
        self._statusEdt.moveCursor(QtGui.QTextCursor.End)

    @QtCore.Slot(str)
    def clearStatus(self):
        self._statusEdt.setPlainText("")

    @QtCore.Slot(float)
    def setDirectory(self, directory):
        self._directoryTxt.setText(directory)

    def directory(self):
        return self._directoryTxt.text()

    @QtCore.Slot(int)
    def updateState(self, machine):
        self.setRunning(machine)

    @QtCore.Slot()
    def _selectDirectory(self):
        path = QtGui.QFileDialog.getExistingDirectory(self)
        self.setDirectory(path)
        self.directoryChanged.emit()

    def setRunning(self, machine):
        if machine.running:
            self._runBtt.clicked.connect(self.runClicked)
            self._runBtt.clicked.disconnect()
            self._runBtt.clicked.connect(self.abortClicked)
            self._directoryGrp.setDisabled(True)
            self._runBtt.setDisabled(True)
            self._writeBtt.setDisabled(True)
            self._fetchBtt.setDisabled(True)
            self._pullBtt.setDisabled(True)
            self._cancelBtt.setDisabled(True)
            self._removeBtt.setDisabled(True)
            self._postproPreviewBtt.setDisabled(True)
            self._postproHighBtt.setDisabled(True)
            self.auth_btt.setDisabled(True)
        else:
            self._runBtt.clicked.connect(self.abortClicked)
            self._runBtt.clicked.disconnect()
            self._runBtt.clicked.connect(self.runClicked)
            self._directoryGrp.setDisabled(False)
            self._runBtt.setDisabled(False)
            self._writeBtt.setDisabled(False)
            self._fetchBtt.setDisabled(False)
            self._pullBtt.setDisabled(False)
            self._cancelBtt.setDisabled(False)
            self._removeBtt.setDisabled(False)
            self._postproPreviewBtt.setDisabled(False)
            self._postproHighBtt.setDisabled(False)
            self.auth_btt.setDisabled(False)
    
    def enableAuth(self):
        self.auth_btt.setText("Log in")
        self.auth_btt.setDisabled(False)
        self.email_text.setDisabled(False)
        self.email_text.show()
        self.password_text.setDisabled(False)
        self.password_text.show()
    
    @QtCore.Slot(str)
    def solveStatus(self, status):
        self.solverStatus.setPlainText("")
        self.solverStatus.insertPlainText(status)


VHFITGR_MTZ    = config("VHFITGR_MTZ")
TII_MTZ        = config("TII_MTZ")
##  @}
