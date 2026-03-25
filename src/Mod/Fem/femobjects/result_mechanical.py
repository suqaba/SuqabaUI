# ***************************************************************************
# *   Copyright (c) 2016 Qingfeng Xia <qingfeng.xia()eng.ox.ac.uk>          *
# *   Copyright (c) 2016 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "FreeCAD FEM result mechanical document object"
__author__ = "Qingfeng Xia, Bernd Hahnebach"
__url__ = "https://www.freecad.org"

## @package result_mechanical
#  \ingroup FEM
#  \brief mechanical result object

from . import base_fempythonobject


class ResultMechanical(base_fempythonobject.BaseFemPythonObject):
    """
    The Fem::ResultMechanical's Proxy python type, add result specific properties
    """

    Type = "Fem::ResultMechanical"

    def __init__(self, obj):
        super().__init__(obj)

        obj.addProperty(
            "App::PropertyString",
            "ResultType",
            "Base",
            "Type of the result",
            1,  # the 1 set the property to ReadOnly
        )
        obj.setPropertyStatus("ResultType", "LockDynamic")
        obj.ResultType = str(self.Type)


    def onDocumentRestored(self, obj):
        pass
