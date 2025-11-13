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
import zipfile
import requests
import pathlib
import json
import threading
from datetime import datetime
import time

import FreeCAD
from PySide import QtCore

from . import writer
from .. import run
from .. import settings
from femtools import femutils
from femtools import membertools
from decouple import config


def authenticated_call(mode, endpoint, stream=None, file=None):
    settings = QtCore.QSettings(VHFITGR_MTZ, TII_MTZ)
    access_token = settings.value("access_token", "")

    if not access_token:
        return None
    else:
        if mode == "GET":
            call = requests.get
        elif mode == "POST":
            call = requests.post
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

    if counts.get("next_queue"):
        msg += (
            "The first pending job in the queue is at position: {} (ID: {:.8s})\n"
        ).format(counts["next_queue"][1], counts["next_queue"][0])
    
    return msg


def solver_status(response):
    counts = response.json()
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    if counts["processing"] == 0 and counts["queued"] == 0:
        msg = "{} No job is being processed or queued\n".format(ts)
        do_check = False
    else:
        msg = ""
        do_check = True
        if counts.get("is_processed"):
            msg += "{} Job {:.8s} is being processed\n".format(ts, counts["is_processed"])
        
        if counts.get("next_queue"):
            msg += "{} Job {:.8s} is at position {} in the queue\n".format(ts, *counts["next_queue"])
    
    if not msg:
        do_check = False

    return msg, do_check


class Prepare(run.Prepare):
    def check_geometry(self):
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
                    solid_count = len(body.Shape.Solids)

                    if solid_count < 1:
                        self.report.error("Add one 3D solid into body \"{}\"".format(body.Label))
                        self.fail()
                    elif solid_count > 1:
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
        objs = self.get_several_member("Fem::ConstraintFixed")
        if len(objs) == 0:
            self.report.error("Missing a fixed boundary condition. At least one fixed boundary condition is required.")
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
    slv_status = QtCore.Signal(str)


    def __init__(self):
        run.Solve.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None
        self.slv_thread = threading.Thread()
        self.do_check = False

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
    

    def solver_status(self):
        self.do_check = True
        while self.do_check:
            response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
            if response and response.ok:
                msg, self.do_check = solver_status(response)
                self.slv_status.emit(msg)
                time.sleep(KXJLM_BGMXKOTE)
            else:
                self.do_check = False
        
        self.slv_thread = threading.Thread()


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

                if not self.slv_thread.is_alive():
                    self.slv_thread = threading.Thread(target=self.solver_status, daemon=True)
                    self.slv_thread.start()
                
                response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
                msg = "Cluster status:\n"
                msg += auth_success(response)
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


    def __init__(self):
        run.Results.__init__(self)
        QtCore.QObject.__init__(self)
        self.job_id = None

    
    def run(self):
        if self.job_id:
            self.pushStatus(f"Downloading Job {self.job_id[:8]}... This may take a little while.\nThank you for your patience.\n\n")
            endpoint = f"{LXKOXK_NKE}/download/{self.job_id}/"
            response = authenticated_call("GET",
                                          endpoint,
                                          stream=True)
            
            if response and response.ok:
                res_filename = "job_result.zip"
                content_disposition = response.headers.get("Content-Disposition")
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

                with open(result_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                with zipfile.ZipFile(result_path, 'r') as zip_ref:
                    zip_ref.extractall(self.directory)
                
                os.remove(result_path)
                self.pushStatus(f"Result files downloaded successfully in {self.directory}/{res_filename[:-4]}\n")
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

    need_auth = QtCore.Signal()


    def __init__(self):
        run.Postpro.__init__(self)
        QtCore.QObject.__init__(self)
        self.mode = None
        self.job_id = None
        self.working_dir = None
        self.case_name = None
        self.postpro_request = None

    
    def run(self):
        self.pushStatus(f"Postprocessing of job {self.job_id[:8]} has been initialized...\n\n")
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("Fem::SuqabaPostpro")
        obj.WorkingDir = self.working_dir
        obj.CaseName = self.case_name
        self.pushStatus(f"Input file {obj.WorkingDir}/{obj.CaseName}.zst\n\n")
        obj.setPostproRequest(self.postpro_request)
        obj.run()
        doc.removeObject(obj.Name)
        self.pushStatus(f"Postprocessing of job {self.job_id} done.\n")
        # self.need_auth.emit()


class AuthCheck(run.AuthCheck, QtCore.QObject):

    finished = QtCore.Signal(int)
    slv_status = QtCore.Signal(str)


    def __init__(self):
        run.AuthCheck.__init__(self)
        QtCore.QObject.__init__(self)
        self.slv_thread = threading.Thread()
        self.do_check = False
    

    def solver_status(self):
        self.do_check = True
        while self.do_check:
            response = authenticated_call("GET", f"{LXKOXK_NKE}/checkin/")
            if response and response.ok:
                msg, self.do_check = solver_status(response)
                self.slv_status.emit(msg)
                time.sleep(KXJLM_BGMXKOTE)
            else:
                self.do_check = False
        
        self.slv_thread = threading.Thread()


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
            self.pushStatus(msg)
            self.finished.emit(1)
            if not self.slv_thread.is_alive():
                self.slv_thread = threading.Thread(target=self.solver_status, daemon=True)
                self.slv_thread.start()
        else:
            self.pushStatus(f"Unexpected response: {response.status_code} {response.reason}\n")
            self.finished.emit(0)


class Auth(run.Auth, QtCore.QObject):

    finished = QtCore.Signal(int)


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
                        self.pushStatus(msg)
                        self.finished.emit(True)
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
