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
import pathlib
import warnings

from PySide import QtCore, QtGui, QtWidgets

import FreeCAD
import FreeCADGui as Gui

import femsolver.report
import femsolver.run


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
        self.form.logClicked.connect(self.livelog)
        self.form.fetchClicked.connect(self.fetch)
        self.form.pullClicked.connect(self.pull)
        self.form.cancelClicked.connect(self.cancel)
        self.form.removeClicked.connect(self.remove)
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
        self.machine.start()
    
    @QtCore.Slot()
    def livelog(self):
        self.machine._state = femsolver.run.LIVELOG
        self.machine.target = femsolver.run.LIVELOG
        selected_job = self.get_selected_job()

        if not selected_job:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please select a job first.")
            return

        self.machine.livelog.job_id = selected_job

        if hasattr(self, "log_window") and self.log_window is not None:
            try:
                self.machine.livelog.log_received.connect(self.log_window.append_log)
                self.machine.livelog.log_received.disconnect(self.log_window.append_log)
            except (TypeError, RuntimeError, RuntimeWarning):
                pass

            try:
                self.log_window.closed.connect(self.machine.livelog.stop)
                self.log_window.closed.disconnect(self.machine.livelog.stop)
            except (TypeError, RuntimeError, RuntimeWarning):
                pass
            
            self.machine.livelog.stop()
            try:
                self.log_window.close()
            except RuntimeError:
                pass
            self.log_window = None

        self.log_window = LogWindow(None)
        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()
        self.machine.livelog.log_received.connect(self.log_window.append_log)
        self.log_window.closed.connect(self.machine.livelog.stop)
        self.machine.livelog.need_auth.connect(self.form.enableAuth)
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
        if not selected_job:
            QtWidgets.QMessageBox.warning(None, "Warning", "Please select a job first.")
            return

        self.machine._state = femsolver.run.RESULTS
        self.machine.target = femsolver.run.RESULTS
        self.machine.results.job_id = selected_job

        for signal in [self.machine.results.dl_status,\
                       self.machine.results.dl_progress,\
                       self.machine.results.need_auth,\
                       self.machine.results.dl_finished]:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                try:
                    signal.disconnect()
                except (TypeError, RuntimeError):
                    pass

        self.download_dialog = DownloadDialog(None)
        self.download_dialog.show()
        self.download_dialog.raise_()
        self.download_dialog.activateWindow()

        # Connect signals
        self.machine.results.dl_status.connect(self.download_dialog.update_status)
        self.machine.results.dl_progress.connect(self.download_dialog.update_progress)
        self.machine.results.need_auth.connect(self.form.enableAuth)
        self.machine.results.need_auth.connect(self.download_dialog.on_finished)
        self.machine.results.dl_finished.connect(self.download_dialog.on_finished)
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
    def auth_check(self):
        self.machine._state = femsolver.run.AUTHCHK
        self.machine.target = femsolver.run.AUTHCHK
        self.machine.auth_check.finished.connect(self.form.checkIn)
        self.machine.auth_check.load_job.connect(self.form.createJobBoxes)
        self.machine.start()
    
    @QtCore.Slot()
    def auth(self):
        self.machine.auth.email = self.form.email_text.text().lower()
        self.machine.auth.pswrd = self.form.password_text.text()
        self.machine._state = femsolver.run.AUTH
        self.machine.target = femsolver.run.AUTH
        self.machine.auth.finished.connect(self.form.checkIn)
        self.machine.auth.load_job.connect(self.form.createJobBoxes)
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


class ControlWidget(QtGui.QWidget):

    writeClicked = QtCore.Signal()
    runClicked = QtCore.Signal()
    logClicked = QtCore.Signal()
    fetchClicked = QtCore.Signal()
    pullClicked = QtCore.Signal()
    cancelClicked = QtCore.Signal()
    removeClicked = QtCore.Signal()
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
        self._logBtt = QtGui.QPushButton("Live logs")
        prepro_layout.addWidget(self._writeBtt)
        prepro_layout.addWidget(self._runBtt)
        prepro_layout.addWidget(self._logBtt)
        self._writeBtt.clicked.connect(self.writeClicked)
        self._logBtt.clicked.connect(self.logClicked)

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
        self.job_scroll.setFixedHeight(200)

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

        jobCtrl_layout.addWidget(self.job_scroll)
        jobCtrl_layout.addLayout(btn_layout)
        self.job_controls.setLayout(jobCtrl_layout)
        
        # General logs
        self._statusEdt = QtGui.QPlainTextEdit()
        self._statusEdt.setReadOnly(True)
        self._statusEdt.setFixedHeight(150)
        status_lyt = QtGui.QVBoxLayout()
        status_lyt.addWidget(self._statusEdt)
        self.log_group = QtGui.QGroupBox("General logs")
        self.log_group.setLayout(status_lyt)

        # Main layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.auth_group)
        layout.addWidget(self._directoryGrp)
        layout.addWidget(self.prepro_group)
        layout.addWidget(self.log_group)
        layout.addWidget(self.job_controls)
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
            self._logBtt.setDisabled(True)
            self._fetchBtt.setDisabled(True)
            self._pullBtt.setDisabled(True)
            self._cancelBtt.setDisabled(True)
            self._removeBtt.setDisabled(True)
            self.auth_btt.setDisabled(True)
        else:
            self._runBtt.clicked.connect(self.abortClicked)
            self._runBtt.clicked.disconnect()
            self._runBtt.clicked.connect(self.runClicked)
            self._directoryGrp.setDisabled(False)
            self._runBtt.setDisabled(False)
            self._writeBtt.setDisabled(False)
            self._logBtt.setDisabled(False)
            self._fetchBtt.setDisabled(False)
            self._pullBtt.setDisabled(False)
            self._cancelBtt.setDisabled(False)
            self._removeBtt.setDisabled(False)
            self.auth_btt.setDisabled(False)
    
    def enableAuth(self):
        self.auth_btt.setText("Log in")
        self.auth_btt.setDisabled(False)
        self.email_text.setDisabled(False)
        self.email_text.show()
        self.password_text.setDisabled(False)
        self.password_text.show()
        self.auth_group.show()


class LogWindow(QtWidgets.QDialog):
    closed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.setWindowTitle("Live Job Logs")
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout()

        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setReadOnly(True)

        layout.addWidget(self.textbox)
        self.setLayout(layout)

    @QtCore.Slot(str)
    def append_log(self, message):
        self.textbox.append(message)
        self.textbox.moveCursor(QtGui.QTextCursor.End)
    
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
    
    def reject(self):
        self.closed.emit()
        self.close()
        super().reject()

class DownloadDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Job Download")
        self.setMinimumWidth(500)

        layout = QtWidgets.QVBoxLayout(self)

        self.label_text = ""
        self.status_label = QtWidgets.QTextEdit()
        self.status_label.setReadOnly(True)
        layout.addWidget(self.status_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
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
    
    @staticmethod
    def format_size(size_bytes):
        if size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.1f} MB"
        else:
            return f"{size_bytes / 1024**3:.1f} GB"

    @QtCore.Slot(int, int)
    def update_progress(self, dl_size, total_size):
        percent = int(100 * dl_size / total_size)
        self.progress_bar.setValue(percent)
        self.label_text = self.label_text.split("Downloaded")[0]
        self.label_text += f"Downloaded {self.format_size(dl_size)} / {self.format_size(total_size)}"
        self.status_label.setText(self.label_text)

    @QtCore.Slot(str)
    def update_status(self, msg):
        self.label_text += msg
        self.status_label.setText(self.label_text)

    @QtCore.Slot()
    def on_finished(self):
        self.close_btn.setEnabled(True)

##  @}
