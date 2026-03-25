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

__title__ = "Suqaba solver object for FreeCAD FEM"
__author__ = "Clément Vella"
__SqbUrl__ = "https://www.suqaba.com"
__FcUrl__ = "https://www.freecad.org"

## @package SolverSuqaba
#  \ingroup FEM

import glob
import os

import FreeCAD

from . import tasks
from .. import run
from .. import solverbase
from femtools import femutils

if FreeCAD.GuiUp:
    import FemGui

GEOMETRY_TYPES = ["single body", "compound body"]
ANALYSIS_TYPES = ["static linear elastic"] #, "steady-state thermal"]


def create(doc, name="SolverSuqaba"):
    return femutils.createObject(doc, name, Proxy, ViewProxy)


class Proxy(solverbase.Proxy):
    """The Fem::FemSolver's Proxy python type, add solver specific properties"""

    Type = "Fem::SolverSuqaba"

    def __init__(self, obj):
        super().__init__(obj)
        obj.Proxy = self

        if not hasattr(obj, "GeometryType"):
            obj.addProperty("App::PropertyEnumeration",
                            "GeometryType",
                            "Solver",
                            "Type of geometry")
            obj.GeometryType = GEOMETRY_TYPES
            obj.GeometryType = GEOMETRY_TYPES[0]

        if not hasattr(obj, "AnalysisType"):
            obj.addProperty("App::PropertyEnumeration",
                            "AnalysisType",
                            "Solver",
                            "Type of the analysis")
            obj.AnalysisType = ANALYSIS_TYPES
            obj.AnalysisType = ANALYSIS_TYPES[0]

        if not hasattr(obj, "ErrorTolerance"):
            obj.addProperty("App::PropertyFloatConstraint",
                            "ErrorTolerance",
                            "Solver",
                            "Error Tolerance (%)")
            obj.ErrorTolerance = 20.
        
        if not hasattr(obj, "HighOrderStress"):
            obj.addProperty("App::PropertyBool",
                            "HighOrderStress",
                            "Solver",
                            "Activate high order stress")
            obj.HighOrderStress = False
        
        if not hasattr(obj, "ExportToBdf"):
            obj.addProperty("App::PropertyBool",
                            "ExportToBdf",
                            "Export",
                            "Export to .bdf format")
            obj.ExportToBdf = False
    
    def createMachine(self, obj, directory, testmode=False):
        return run.Machine(
            solver=obj,
            directory=directory,
            prepare=tasks.Prepare(),
            solve=tasks.Solve(),
            fetch=tasks.Fetch(),
            results=tasks.Results(),
            livelog=tasks.Livelog(),
            auth_check=tasks.AuthCheck(),
            auth=tasks.Auth(),
            cancel=tasks.Cancel(),
            remove=tasks.Remove(),
            testmode=testmode,
        )

    def editSupported(self):
        return False

    def edit(self, directory):
        return

    def execute(self, obj):
        return


class ViewProxy(solverbase.ViewProxy):

    def getIcon(self):
        return ":/icons/FEM_SolverSuqaba.svg"


##  @}
