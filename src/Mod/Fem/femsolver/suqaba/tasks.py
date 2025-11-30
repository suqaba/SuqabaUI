# ***************************************************************************
# *   Copyright (c) 2017 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "Suqaba solver tasks for FreeCAD FEM"
__author__ = "Clément Vella"
__SqbUrl__ = "https://www.suqaba.com"
__FcUrl__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import os
import sys
import subprocess
import zipfile
import requests
import pathlib
import json
import threading
from datetime import datetime
import websockets
import socket
import asyncio
from decouple import config

import FreeCAD
from PySide import QtCore

from . import writer
from .. import run
from .. import settings
from femtools import femutils
from femtools import membertools
from .network import ipv4_session


def authenticated_call(mode, endpoint, stream=None, file=None):
    settings = QtCore.QSettings(VHFITGR_MTZ, TII_MTZ)
    access_token = settings.value("access_token", "")

    if not access_token:
        return None
    else:
        if mode == "GET":
            call = ipv4_session.get
        elif mode == "POST":
            call = ipv4_session.post
        else:
            return None
        
        kwargs = {"headers": {"Authorization": f"Bearer {access_token}"}}

        if stream:
            kwargs["stream"] = True
        if file:
            kwargs["files"] = {"file": file}
        
        return call(endpoint, **kwargs)


def auth_success(response):
    counts = response.json()

    msg = (
        "    {} job(s) have been completed\n"
        "    {} job is being processed\n"
        "    {} job(s) are queued\n\n"
    ).format(counts.get("completed"), counts.get("processing"),
             counts.get("queued"))
    
    return msg


def solver_status(response):
    counts = response.json()
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    msg = ""

    if counts["processing"] == 0 and counts["queued"] == 0:
        msg += "{} No job is being processed or queued\n".format(ts)
    else:
        if counts.get("is_processed"):
            msg += "{} Job {:.8s} is being processed\n".format(ts, counts["is_processed"])
        
        if counts.get("next_queue"):
            msg += "{} The first pending job in the queue is at position: {} (ID: {:.8s})\n".format(ts,
                                                                                                    counts["next_queue"][1],
                                                                                                    counts["next_queue"][0])
    
    return msg


class Prepare(run.Prepare):
    def check_geometry(self):
        self.solid_count = -1
        if self.solver.GeometryType == "single body":
            bodies_list = []

            for obj in FreeCAD.ActiveDocument.Objects:
                if obj.isDerivedFrom("PartDesign::Body"):
                    bodies_list.append(obj)

            body_count = len(bodies_list)

            if body_count < 1:
                self.report.error("Make one Body object (geometry type is \"single body\")")
                self.fail()
            elif body_count > 1:
                self.report.error("When geometry type is \"single body\", the document must contain exactly one Body object")
                self.fail()
            else:
                body = bodies_list[0]
                if hasattr(body, "Shape"):
                    self.solid_count = len(body.Shape.Solids)

                    if self.solid_count < 1:
                        self.report.error("Add one 3D solid into body \"{}\"".format(body.Label))
                        self.fail()
                    elif self.solid_count > 1:
                        self.report.error("When geometry type is \"single body\", the Body object must contain exactly one 3D solid")
                        self.fail()
        
        elif self.solver.GeometryType == "compound body":
            bfrag_list = []

            for obj in FreeCAD.ActiveDocument.Objects:
                if obj.isDerivedFrom("Part::Feature"):
                    bfrag_list.append(obj)
            
            bfrag_count = len(bfrag_list)

            if bfrag_count < 1:
                self.report.error("Make one BooleanFragments object from an assembly (geometry type is \"compound body\")")
                self.fail()
            elif bfrag_count > 1:
                self.report.error("When geometry type is \"compound body\", the document must contain exactly one BooleanFragments object")
                self.fail()
            else:
                body = bfrag_list[0]
                if body.Name == "BooleanFragments":
                    if hasattr(body, "Shape"):
                        self.solid_count = len(body.Shape.Solids)

                        if self.solid_count < 1:
                            self.report.error("Have at least one 3D solid into compound body \"{}\"".format(body.Label))
                            self.fail()
                else:
                    self.report.error("When geometry type is \"compound body\", the document must contain exactly one BooleanFragments object")
                    self.fail()
    
    def check_material_selected(self):
        if self.solver.GeometryType == "single body":
            if self.check_material_single():
                mat = self.get_several_member("App::MaterialObjectPython")[0]["Object"]
                if not mat.Material:
                    self.report.error(f"No material was selected for {mat.Name}")
                    self.fail()
                if not mat.References:
                    self.report.error(f"No solid geometry reference was selected for {mat.Name}")
                    self.fail()
        elif self.solver.GeometryType == "compound body":
            mats = self.get_several_member("App::MaterialObjectPython")
            reference_list = []
            for mat in mats:
                mat_obj = mat["Object"]
                if not mat_obj.Material:
                    self.report.error(f"No material was selected for {mat_obj.Name}")
                    self.fail()
                
                if not mat_obj.References:
                    self.report.error(f"No solid geometry reference was selected for {mat_obj.Name}")
                    self.fail()
                else:
                    for ref_str in mat_obj.References[0][1]:
                        if ref_str in reference_list:
                            self.report.error(f"Solid {ref_str} was assigned more than one material")
                            self.fail()
                        else:
                            reference_list.append(ref_str)

            if self.solid_count != len(reference_list):
                self.report.error(f"Some solids of the assembly were not assigned a material")
                self.fail()
                    

    def check_dirichlet(self):
        blocks = self.get_several_member("Fem::ConstraintFixed")
        displs = self.get_several_member("Fem::ConstraintDisplacement")
        if len(blocks) + len(displs) < 1:
            self.report.error("Missing a Dirichlet boundary condition. At least one Dirichlet boundary condition is required.")
            self.fail()
    
    def check_target_error(self):
        if self.solver.ErrorTolerance < 2.5:
            self.solver.ErrorTolerance = 2.5
            msg = (
                "The minimum error tolerance (quality requirement) "
                "cannot be set below 2.5%."
            )
            self.report.warning(msg)

    def run(self):
        self.pushStatus("Checking analysis member...\n\n")
        self.check_geometry()
        self.check_material_exists()
        self.check_material_selected()
        self.check_dirichlet()
        self.check_target_error()
        
        if not self.failed:
            self.pushStatus("Preparing solver input...\n\n")
            w = writer.FemInputWriterSuqaba(self.pushStatus,
                                            self.analysis,
                                            self.solver,
                                            membertools.AnalysisMember(self.analysis),
                                            self.directory)
            path = w.write_solver_input()

            if path is not None:
                self.pushStatus("Writing solver input completed.\n")
            else:
                self.pushStatus("Writing solver input failed.\n")
                self.fail()


class Solve(run.Solve, QtCore.QObject):
    
    finished = QtCore.Signal(list)
    need_auth = QtCore.Signal()


    def __init__(self):
        run.Solve.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None

    @staticmethod
    def to_compress(ext):
        return ext in {".brep", ".step", ".geo", ".json"} 
    

    def compress_files(self, arx_name):
        log_string = "{} files were added to the job archive.\n"
        file_list  = []
        arx_path = os.path.join(self.directory, arx_name)

        with zipfile.ZipFile(arx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_sufx = pathlib.Path(file).suffix

                    if (os.path.isfile(file_path) and self.to_compress(file_sufx)):
                        zipf.write(file_path, arcname=file)
                        file_list.append(file)
            
            n_file = len(file_list)
            self.pushStatus(log_string.format(n_file))

            for i, file in enumerate(file_list):
                self.pushStatus("    {} {}\n".format(i + 1, file))
            self.pushStatus("\n")
        
        if n_file:
            return arx_path
        else:
            self.pushStatus("Your job cannot be submitted.\n")
            return None


    def run(self):
        name = pathlib.Path(self.solver.Document.FileName).stem
        arx_path = self.compress_files("{}.zip".format(name))
        
        if arx_path:
            with open(arx_path, "rb") as f:
                response = authenticated_call("POST", f"{LXKOXK_NKE}/upload/",
                                              file=f)

            if response and response.ok:
                self.job_id = response.json()["job_id"]
                self.pushStatus(f"Your job has successfully been submitted.\n    Job ID: {self.job_id[:8]}\n\n")
                
                response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
                msg = "Cluster status:\n"
                msg += auth_success(response)
                msg += solver_status(response)
                self.pushStatus(msg)
                
                response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
                if response and response.ok:
                    job_list = response.json()["jobs"]
                    self.finished.emit(job_list)
                else:
                    self.pushStatus(f"Fetching jobs failed: {response.status_code} {response.reason}\n")
                    self.finished.emit([])
            else:
                if response == None:
                    self.pushStatus("Please, authenticate yourself.\n")
                else:
                    self.pushStatus(f"Upload failed: {response.status_code} {response.reason}\n")
                
                self.need_auth.emit()


class Cancel(run.Cancel, QtCore.QObject):
    
    finished = QtCore.Signal(list)
    need_auth = QtCore.Signal()


    def __init__(self):
        run.Cancel.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None


    def run(self):
        if self.job_id:
            endpoint = f"{LXKOXK_NKE}/cancel/{self.job_id}/"
            response = authenticated_call("POST", endpoint)

            if response and response.ok:
                resp_json = response.json()
                self.pushStatus("{}\n\n".format(resp_json.get("message")))

                response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
                msg = "Cluster status:\n"
                msg += auth_success(response)
                msg += solver_status(response)
                self.pushStatus(msg)
                
                response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
                if response and response.ok:
                    job_list = response.json()["jobs"]
                    self.finished.emit(job_list)
                else:
                    self.pushStatus(f"Refreshing jobs failed: {response.status_code} {response.reason}\n")
                    self.finished.emit([])
            else:
                if response == None:
                    self.pushStatus("Please, authenticate yourself.\n")
                else:
                    self.pushStatus(f"Cancelling job may have failed: {response.status_code} {response.reason}\n")
                
                self.need_auth.emit()
        else:
            self.pushStatus("Please, fetch and select a job to cancel it.\n")


class Remove(run.Remove, QtCore.QObject):
    
    finished = QtCore.Signal(list)
    need_auth = QtCore.Signal()


    def __init__(self):
        run.Cancel.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None


    def run(self):
        if self.job_id:
            endpoint = f"{LXKOXK_NKE}/remove/{self.job_id}/"
            response = authenticated_call("POST", endpoint)

            if response and response.ok:
                resp_json = response.json()
                self.pushStatus("{}\n\n".format(resp_json.get("message")))

                response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
                msg = "Cluster status:\n"
                msg += auth_success(response)
                msg += solver_status(response)
                self.pushStatus(msg)
                
                response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
                if response and response.ok:
                    job_list = response.json()["jobs"]
                    self.finished.emit(job_list)
                else:
                    self.pushStatus(f"Refreshing jobs failed: {response.status_code} {response.reason}\n")
                    self.finished.emit([])
            else:
                if response == None:
                    self.pushStatus("Please, authenticate yourself.\n")
                else:
                    self.pushStatus(f"Cancelling job may have failed: {response.status_code} {response.reason}\n")
                
                self.need_auth.emit()
        else:
            self.pushStatus("Please, fetch and select a job to remove it.\n")


class Fetch(run.Fetch, QtCore.QObject):

    finished = QtCore.Signal(list)
    need_auth = QtCore.Signal()


    def __init__(self):
        run.Fetch.__init__(self)
        QtCore.QObject.__init__(self)


    def run(self):
        response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
        
        if response and response.ok:
            job_list = response.json()["jobs"]
            msg = "Fetch jobs report:\n\n"
            msg += auth_success(response)
            msg += solver_status(response)
            self.pushStatus(msg)
            self.finished.emit(job_list)
        else:
            if response == None:
                self.pushStatus("Please, authenticate yourself.\n")
            else:
                self.pushStatus(f"Fetching jobs failed: {response.status_code} {response.reason}\n")
            
            self.finished.emit([])
            self.need_auth.emit()


class Results(run.Results, QtCore.QObject):

    need_auth = QtCore.Signal()
    dl_status = QtCore.Signal(str)


    def __init__(self):
        run.Results.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None

    
    def run(self):
        if self.job_id:
            msg = f"Downloading Job {self.job_id[:8]}... This may take a little while.\nThank you for your patience.\n\n"
            self.pushStatus(msg)
            endpoint = f"{LXKOXK_NKE}/download/{self.job_id}/"
            response = authenticated_call("GET",
                                          endpoint,
                                          stream=True)
            
            if response and response.ok:
                res_filename = "job_result.zip"
                content_disposition = response.headers.get("Content-Disposition")
                total_size = int(response.headers.get("Content-Length", 1))
                
                if content_disposition:
                    res_filename = content_disposition.split("filename=\"")[-1][:-1]

                if res_filename in os.listdir(self.directory):
                    psx_path = pathlib.Path(res_filename)
                    n_occ = 0
                    for e in os.listdir(self.directory):
                        if psx_path.stem in pathlib.Path(e).stem:
                            n_occ += 1
                    
                    res_filename = "{}_{}{}".format(psx_path.stem, n_occ, psx_path.suffix)

                result_path = os.path.join(self.directory, res_filename)

                dl_size = 0
                with open(result_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            dl_size += len(chunk)
                            percent = 100. * dl_size / total_size
                            msg = msg.split("Downloaded")[0] + f"Downloaded {percent:.1f}%..."
                            self.dl_status.emit(msg)
                
                with zipfile.ZipFile(result_path, 'r') as zip_ref:
                    zip_ref.extractall(self.directory)
                
                os.remove(result_path)
                self.pushStatus(f"\n\nResult files downloaded successfully in {self.directory}/{res_filename[:-4]}\n")
            else:
                if response == None:
                    self.pushStatus("Please, authenticate yourself.\n")
                else:
                    json_res = response.json()
                    if json_res.get("not-ready") is not None:
                        not_ready_status = json_res.get("not-ready")
                        self.pushStatus(f"{not_ready_status}\n")
                    else:
                        self.pushStatus(f"Error downloading result: {response.status_code} {response.reason}\n")
                
                self.need_auth.emit()
        else:
            self.pushStatus("Please, fetch and select a job before pulling.\n")


class Postpro(run.Postpro, QtCore.QObject):

    ppro_status = QtCore.Signal(str)

    def __init__(self):
        run.Postpro.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None
        self.working_dir = None
        self.case_name = None
        self.postpro_request = None

    def _stream_worker_output(self):
        for line in iter(self.process.stdout.readline, ''):
            if "Suqaba" not in line:
                self.ppro_status.emit(line)

    def run(self):
        moddir = FreeCAD.getHomePath()
        bindir = os.path.join(moddir, "bin")
        cmd = os.path.join(bindir, "SuqabaUICmd")
        script_path = f"{moddir}Mod/Fem/femsolver/suqaba/postpro_worker.py"

        self.pushStatus(f"Postprocessing of job {self.job_id[:8]} has been initialized...\n")

        args = [cmd,
                script_path,
                self.working_dir,
                self.case_name,
                json.dumps(self.postpro_request)]

        kwargs = { "stdout": subprocess.PIPE,
                   "stderr": subprocess.STDOUT,
                   "text": True }

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        
        self.process = subprocess.Popen(args, **kwargs)
        threading.Thread(target=self._stream_worker_output, daemon=True).start()


class Livelog(run.Livelog, QtCore.QObject):

    log_received = QtCore.Signal(str)
    
    def __init__(self):
        run.Livelog.__init__(self)
        QtCore.QObject.__init__(self)

        self.job_id = None
        self.log_thread = None
        self.stop_event = threading.Event()
        self.loop = None
        self.ws = None

    def run(self):
        settings = QtCore.QSettings(VHFITGR_MTZ, TII_MTZ)
        self.access_token = settings.value("access_token", "")
        WS_URL = LXKOXK_NKE.replace("https", "wss").replace("http", "ws").replace("api", "ws/logs/?token=")
        WS_URL += self.access_token

        self.stop_event.clear() 

        async def stream_log():
            self.loop = asyncio.get_running_loop()
            async with websockets.connect(WS_URL, family=socket.AF_INET) as ws:
                self.ws = ws
                await ws.send(json.dumps({"job_id": self.job_id}))
                self.log_received.emit(f"Streaming log for job: {self.job_id[:8]}\n---")

                try:
                    async for message in ws:
                        if self.stop_event.is_set():
                            break
                        self.log_received.emit(message.strip("\n"))
                except websockets.ConnectionClosed as e:
                    self.log_received.emit(f"\nConnection closed: {e.code} {e.reason}")
                    
            self.ws = None
        
        def thread_target():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(stream_log())
            self.loop.close()

        self.log_thread = threading.Thread(target=thread_target,
                                           daemon=True)
        self.log_thread.start()
    
    def stop(self):
        self.stop_event.set()

        if self.ws and self.loop and self.loop.is_running():
           asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
        
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=2.0)


class AuthCheck(run.AuthCheck, QtCore.QObject):

    finished = QtCore.Signal(int)
    load_job = QtCore.Signal(list)

    def __init__(self):
        run.AuthCheck.__init__(self)
        QtCore.QObject.__init__(self)


    def run(self):
        response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
        if not response:
            msg = (
                "Please, authenticate yourself.\n\n"
                "If you don't have an account yet, please sign up at https://suqaba.com/signup"
            )
            self.pushStatus(msg)
            self.finished.emit(0)
        elif response.status_code == requests.codes.UNAUTHORIZED:
            msg = (
                "Please, authenticate yourself.\n\n"
                "If you don't have an account yet, please sign up at https://suqaba.com/signup"
            )
            self.pushStatus(msg)
            self.finished.emit(0)
        elif response.status_code == requests.codes.OK:
            msg = "You are authenticated.\n\n"
            msg += auth_success(response)
            msg += solver_status(response)
            self.pushStatus(msg)
            self.finished.emit(1)

            response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
            if response and response.ok:
                job_list = response.json()["jobs"]
                self.load_job.emit(job_list)
            else:
                self.pushStatus(f"Loading jobs failed: {response.status_code} {response.reason}\n")
                self.load_job.emit([])
        else:
            self.pushStatus(f"Unexpected response: {response.status_code} {response.reason}\n")
            self.finished.emit(0)


class Auth(run.Auth, QtCore.QObject):

    finished = QtCore.Signal(int)
    load_job = QtCore.Signal(list)

    def __init__(self):
        run.Auth.__init__(self)
        QtCore.QObject.__init__(self)
        self.email = None
        self.pswrd = None
    

    def run(self):
        response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
        
        if response and response.ok:
            settings = QtCore.QSettings(VHFITGR_MTZ, TII_MTZ)
            settings.remove("access_token")
            settings.remove("refresh_token")
            settings.clear()
            self.finished.emit(False)
        else:
            if not self.email or not self.pswrd:
                self.pushStatus("Email or password cannot be empty.\n")
                self.finished.emit(False)
            else:
                data     = {"email": self.email, "password": self.pswrd}
                response = requests.post(f"{LXKOXK_NKE}/token/",
                                         data=json.dumps(data),
                                         headers={"Content-Type": "application/json"})
                
                if response and response.ok:
                    tokens = response.json()
                    access_token = tokens.get("access")
                    refresh_token = tokens.get("refresh")

                    if access_token and refresh_token:
                        settings = QtCore.QSettings(VHFITGR_MTZ, TII_MTZ)
                        settings.setValue("access_token", access_token)
                        settings.setValue("refresh_token", refresh_token)

                        response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
                        msg = "You are authenticated.\n\n"
                        msg += auth_success(response)
                        msg += solver_status(response)
                        self.pushStatus(msg)
                        self.finished.emit(True)

                        response = authenticated_call("GET", f"{LXKOXK_NKE}/fetch/")
                        if response and response.ok:
                            job_list = response.json()["jobs"]
                            self.load_job.emit(job_list)
                        else:
                            self.pushStatus(f"Loading jobs failed: {response.status_code} {response.reason}\n")
                            self.load_job.emit([])
                    else:
                        self.pushStatus("Authentication failed (access not found).\n")
                        self.finished.emit(False)
                else:
                    if response == None:
                        self.pushStatus("Authentication failed.\n")
                    else:
                        self.pushStatus(f"Authentication failed: {response.status_code} {response.reason}\n")
                    
                    self.finished.emit(False)


VHFITGR_MTZ    = config("VHFITGR_MTZ")
TII_MTZ        = config("TII_MTZ")
LXKOXK_NKE     = config("LXKOXK_NKE")
KXJLM_BGMXKOTE = config("KXJLM_BGMXKOTE", cast=int)


##  @}
