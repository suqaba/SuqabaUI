# ***************************************************************************
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

__title__ = "FreeCAD FEM command definitions"
__author__ = "Bernd Hahnebach"
__url__ = "https://www.freecad.org"

## @package commands
#  \ingroup FEM
#  \brief FreeCAD FEM command definitions

from PySide import QtCore
from PySide import QtGui

import FreeCAD
import FreeCADGui
from FreeCAD import Qt

from .manager import CommandManager
from femtools.femutils import expandParentObject
from femtools.femutils import is_of_type
from femsolver.settings import get_default_solver

# Python command definitions:
# for C++ command definitions see src/Mod/Fem/Command.cpp
# TODO, may be even more generic class creation
# with type() and identifier instead of class for
# the commands which add new document objects.
# see https://www.python-course.eu/python3_classes_and_type.php
# Translation:
# some information in the regard of translation can be found in forum post
# https://forum.freecad.org/viewtopic.php?f=18&t=62449&p=543845#p543593


class _Analysis(CommandManager):
    "The FEM_Analysis command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_Analysis", "Analysis container")
        self.accel = "S, A"
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_Analysis", "Creates an analysis container with default solver"
        )
        self.is_active = "with_document"

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create Analysis")
        FreeCADGui.addModule("FemGui")
        FreeCADGui.addModule("ObjectsFem")
        FreeCADGui.doCommand("ObjectsFem.makeAnalysis(FreeCAD.ActiveDocument, 'Analysis')")
        FreeCADGui.doCommand("FemGui.setActiveAnalysis(FreeCAD.ActiveDocument.ActiveObject)")
        FreeCAD.ActiveDocument.commitTransaction()
        if get_default_solver() != "None":
            FreeCAD.ActiveDocument.openTransaction("Create default solver")
            FreeCADGui.doCommand(
                f"ObjectsFem.makeSolver{get_default_solver()}(FreeCAD.ActiveDocument)"
            )
            FreeCADGui.doCommand(
                "FemGui.getActiveAnalysis().addObject(FreeCAD.ActiveDocument.ActiveObject)"
            )
            FreeCAD.ActiveDocument.commitTransaction()
            self.do_activated = "add_obj_on_gui_expand_noset_edit"
            # Fixme: expand analysis object in tree view to make added solver visible
            # expandParentObject() does not work because the Analysis is not yet a tree
            # in the tree view
        FreeCAD.ActiveDocument.recompute()


class _ClippingPlaneAdd(CommandManager):
    "The FEM_ClippingPlaneAdd command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ClippingPlaneAdd", "Clipping plane on face")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ClippingPlaneAdd", "Add a clipping plane on a selected face"
        )
        self.is_active = "with_document"

    def Activated(self):
        from pivy import coin
        from femtools.femutils import getBoundBoxOfAllDocumentShapes
        from femtools.femutils import getSelectedFace

        overallboundbox = getBoundBoxOfAllDocumentShapes(FreeCAD.ActiveDocument)
        # print(overallboundbox)
        if overallboundbox:
            min_bb_length = min(
                {
                    overallboundbox.XLength,
                    overallboundbox.YLength,
                    overallboundbox.ZLength,
                }
            )
        else:
            min_bb_length = 10.0  # default

        dbox = min_bb_length * 0.2

        aFace = getSelectedFace(FreeCADGui.Selection.getSelectionEx())
        if aFace:
            f_CoM = aFace.CenterOfMass
            f_uvCoM = aFace.Surface.parameter(f_CoM)  # u,v at CoM for normalAt calculation
            f_normal = aFace.normalAt(f_uvCoM[0], f_uvCoM[1])
        else:
            f_CoM = FreeCAD.Vector(0, 0, 0)
            f_normal = FreeCAD.Vector(0, 0, 1)

        coin_normal_vector = coin.SbVec3f(-f_normal.x, -f_normal.y, -f_normal.z)
        coin_bound_box = coin.SbBox3f(
            f_CoM.x - dbox,
            f_CoM.y - dbox,
            f_CoM.z - dbox * 0.15,
            f_CoM.x + dbox,
            f_CoM.y + dbox,
            f_CoM.z + dbox * 0.15,
        )
        clip_plane = coin.SoClipPlaneManip()
        clip_plane.setValue(coin_bound_box, coin_normal_vector, 1)
        FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().insertChild(clip_plane, 1)


class _ClippingPlaneRemoveAll(CommandManager):
    "The FEM_ClippingPlaneRemoveAll command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ClippingPlaneRemoveAll", "Remove all clipping planes"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ClippingPlaneRemoveAll", "Removes all clipping planes"
        )
        self.is_active = "with_document"

    def Activated(self):
        line1 = "for node in list(sg.getChildren()):\n"
        line2 = "    if isinstance(node, coin.SoClipPlane):\n"
        line3 = "        sg.removeChild(node)"
        FreeCADGui.doCommand("from pivy import coin")
        FreeCADGui.doCommand("sg = Gui.ActiveDocument.ActiveView.getSceneGraph()")
        FreeCADGui.doCommand("nodes = sg.getChildren()")
        FreeCADGui.doCommand(line1 + line2 + line3)


class _ConstantVacuumPermittivity(CommandManager):
    "The FEM_ConstantVacuumPermittivity command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "fem-solver-analysis-thermomechanical.svg"
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstantVacuumPermittivity", "Constant vacuum permittivity"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstantVacuumPermittivity",
            "Creates a FEM constant vacuum permittivity to overwrite standard value",
        )
        self.is_active = "with_document"
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_noset_edit"


class _ConstraintBodyHeatSource(CommandManager):
    "The FEM_ConstraintBodyHeatSource command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "FEM_ConstraintBodyHeatSource"
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintBodyHeatSource", "Body heat source")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintBodyHeatSource", "Creates a body heat source"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintCentrif(CommandManager):
    "The FEM_ConstraintCentrif command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintCentrif", "Centrifugal load")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintCentrif", "Creates a centrifugal load")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintCurrentDensity(CommandManager):
    "The FEM_ConstraintCurrentDensity command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "FEM_ConstraintCurrentDensity"
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintCurrentDensity", "Current density boundary condition"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintCurrentDensity",
            "Creates a current density boundary condition",
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintElectricChargeDensity(CommandManager):
    "The FEM_ConstraintElectricChargeDensity command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "FEM_ConstraintElectricChargeDensity"
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintElectricChargeDensity", "Electric charge density"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintElectricChargeDensity", "Creates a electric charge density"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintElectrostaticPotential(CommandManager):
    "The FEM_ConstraintElectrostaticPotential command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintElectrostaticPotential",
            "Electrostatic potential boundary condition",
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintElectrostaticPotential",
            "Creates an electrostatic potential boundary condition",
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintFlowVelocity(CommandManager):
    "The FEM_ConstraintFlowVelocity command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintFlowVelocity", "Flow velocity boundary condition"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintFlowVelocity", "Creates a flow velocity boundary condition"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintInitialFlowVelocity(CommandManager):
    "The FEM_ConstraintInitialFlowVelocity command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintInitialFlowVelocity", "Initial flow velocity condition"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintInitialFlowVelocity",
            "Creates initial flow velocity condition",
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintInitialPressure(CommandManager):
    "The FEM_ConstraintInitialPressure command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintInitialPressure", "Initial pressure condition"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintInitialPressure", "Creates an initial pressure condition"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintMagnetization(CommandManager):
    "The FEM_ConstraintMagnetization command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintMagnetization", "Magnetization boundary condition"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintMagnetization", "Creates a magnetization boundary condition"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintSectionPrint(CommandManager):
    "The FEM_ConstraintSectionPrint command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintSectionPrint", "Section print feature")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ConstraintSectionPrint", "Creates a section print feature"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ConstraintSelfWeight(CommandManager):
    "The FEM_ConstraintSelfWeight command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintSelfWeight", "Gravity load")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintSelfWeight", "Creates a gravity load")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_noset_edit"


class _ConstraintTie(CommandManager):
    "The FEM_ConstraintTie command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintTie", "Tie constraint")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_ConstraintTie", "Creates a tie constraint")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ElementFluid1D(CommandManager):
    "The FEM_ElementFluid1D command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ElementFluid1D", "Fluid section for 1D flow")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ElementFluid1D", "Creates a FEM fluid section for 1D flow"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ElementGeometry1D(CommandManager):
    "The Fem_ElementGeometry1D command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ElementGeometry1D", "Beam cross section")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ElementGeometry1D", "Creates a FEM beam cross section"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ElementGeometry2D(CommandManager):
    "The FEM_ElementGeometry2D command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ElementGeometry2D", "Shell plate thickness")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ElementGeometry2D", "Creates a FEM shell plate thickness"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _ElementRotation1D(CommandManager):
    "The Fem_ElementRotation1D command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ElementRotation1D", "Beam rotation")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_ElementRotation1D", "Creates a FEM beam rotation")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_noset_edit"


class _Examples(CommandManager):
    "The FEM_Examples command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "FemWorkbench"
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_Examples", "Open FEM examples")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_Examples", "Opens the FEM examples")
        self.is_active = "always"

    def Activated(self):
        FreeCADGui.addModule("femexamples.examplesgui")
        FreeCADGui.doCommand("femexamples.examplesgui.show_examplegui()")


class _MaterialEditor(CommandManager):
    "The FEM_MaterialEditor command definition"

    def __init__(self):
        super().__init__()
        self.pixmap = "Arch_Material_Group"
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MaterialEditor", "Material editor")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_MaterialEditor", "Opens the FreeCAD material editor"
        )
        self.is_active = "always"

    def Activated(self):
        FreeCADGui.addModule("MaterialEditor")
        FreeCADGui.doCommand("MaterialEditor.openEditor()")


class _MaterialFluid(CommandManager):
    "The FEM_MaterialFluid command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MaterialFluid", "Material for fluid")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MaterialFluid", "Creates a FEM material for fluid")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _MaterialReinforced(CommandManager):
    "The FEM_MaterialReinforced command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_MaterialReinforced", "Reinforced material (concrete)"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_MaterialReinforced",
            "Creates a material for reinforced matrix material such as concrete",
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _MaterialSolid(CommandManager):
    "The FEM_MaterialSolid command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MaterialSolid", "Material for solid")
        self.accel = "M, S"
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MaterialSolid", "Creates a FEM material for solid")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


class _FEMMesh2Mesh(CommandManager):
    "The FEM_FEMMesh2Mesh command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_FEMMesh2Mesh", "FEM mesh to mesh")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_FEMMesh2Mesh", "Converts the surface of a FEM mesh to a mesh"
        )
        self.is_active = "with_femmesh_andor_res"

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Create Mesh from FEMMesh")
        if self.selobj and not self.selobj2:  # no result object selected
            FreeCADGui.addModule("femmesh.femmesh2mesh")
            FreeCADGui.doCommand(
                "out_mesh = femmesh.femmesh2mesh.femmesh_2_mesh("
                "FreeCAD.ActiveDocument.{}.FemMesh)".format(self.selobj.Name)
            )
            FreeCADGui.addModule("Mesh")
            FreeCADGui.doCommand("Mesh.show(Mesh.Mesh(out_mesh))")
            FreeCADGui.doCommand(
                "FreeCAD.ActiveDocument." + self.selobj.Name + ".ViewObject.hide()"
            )
        if self.selobj and self.selobj2:
            femmesh = self.selobj
            res = self.selobj2
            FreeCADGui.addModule("femmesh.femmesh2mesh")
            FreeCADGui.doCommand(
                "out_mesh = femmesh.femmesh2mesh.femmesh_2_mesh("
                "FreeCAD.ActiveDocument.{}.FemMesh, FreeCAD.ActiveDocument.{})".format(
                    femmesh.Name, res.Name
                )
            )
            FreeCADGui.addModule("Mesh")
            FreeCADGui.doCommand("Mesh.show(Mesh.Mesh(out_mesh))")
            FreeCADGui.doCommand("FreeCAD.ActiveDocument." + femmesh.Name + ".ViewObject.hide()")
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCADGui.Selection.clearSelection()
        FreeCAD.ActiveDocument.recompute()


class _MeshBoundaryLayer(CommandManager):
    "The FEM_MeshBoundaryLayer command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshBoundaryLayer", "FEM mesh boundary layer")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_MeshBoundaryLayer", "Creates a FEM mesh boundary layer"
        )
        self.is_active = "with_gmsh_femmesh"
        self.do_activated = "add_obj_on_gui_selobj_set_edit"


class _MeshClear(CommandManager):
    "The FEM_MeshClear command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshClear", "Clear FEM mesh")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MeshClear", "Clears the Mesh of a FEM mesh object")
        self.is_active = "with_femmesh"

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Clear FEM mesh")
        FreeCADGui.addModule("Fem")
        FreeCADGui.doCommand(
            "FreeCAD.ActiveDocument." + self.selobj.Name + ".FemMesh = Fem.FemMesh()"
        )
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCADGui.Selection.clearSelection()
        FreeCAD.ActiveDocument.recompute()


class _MeshDisplayInfo(CommandManager):
    "The FEM_MeshDisplayInfo command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshDisplayInfo", "Display FEM mesh info")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MeshDisplayInfo", "Displays FEM mesh information")
        self.is_active = "with_femmesh"

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction("Display FEM mesh info")
        FreeCADGui.doCommand("print(FreeCAD.ActiveDocument." + self.selobj.Name + ".FemMesh)")
        FreeCADGui.addModule("PySide")
        FreeCADGui.doCommand(
            "mesh_info = str(FreeCAD.ActiveDocument." + self.selobj.Name + ".FemMesh)"
        )
        FreeCADGui.doCommand(
            "PySide.QtGui.QMessageBox.information(None, 'FEM Mesh Info', mesh_info)"
        )
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCADGui.Selection.clearSelection()
        FreeCAD.ActiveDocument.recompute()


class _MeshGmshFromShape(CommandManager):
    "The FEM_MeshGmshFromShape command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshGmshFromShape", "FEM mesh from shape by Gmsh")
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_MeshGmshFromShape", "Creates a FEM mesh from a shape by Gmsh mesher"
        )
        self.is_active = "with_part_feature"

    def Activated(self):
        # a mesh could be made with and without an analysis,
        # we're going to check not for an analysis in command manager module
        FreeCAD.ActiveDocument.openTransaction("Create FEM mesh by Gmsh")
        mesh_obj_name = "FEMMeshGmsh"
        # if requested by some people add Preference for this
        # mesh_obj_name = self.selobj.Name + "_Mesh"
        FreeCADGui.addModule("ObjectsFem")
        FreeCADGui.doCommand(
            "ObjectsFem.makeMeshGmsh(FreeCAD.ActiveDocument, '" + mesh_obj_name + "')"
        )
        FreeCADGui.doCommand(
            "FreeCAD.ActiveDocument.ActiveObject.Shape = FreeCAD.ActiveDocument.{}".format(
                self.selobj.Name
            )
        )
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.ActiveObject.ElementOrder = '2nd'")
        # SecondOrderLinear gives much better meshes in the regard of
        # nonpositive jacobians but on curved faces the constraint nodes
        # will no longer found thus standard will be False
        # https://forum.freecad.org/viewtopic.php?t=41738
        # https://forum.freecad.org/viewtopic.php?f=18&t=45260&start=20#p389494
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.ActiveObject.SecondOrderLinear = False")

        # Gmsh mesh object could be added without an active analysis
        # but if there is an active analysis move it in there
        import FemGui

        if FemGui.getActiveAnalysis():
            FreeCADGui.addModule("FemGui")
            FreeCADGui.doCommand(
                "FemGui.getActiveAnalysis().addObject(FreeCAD.ActiveDocument.ActiveObject)"
            )
        FreeCADGui.doCommand(
            "FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)"
        )
        FreeCADGui.Selection.clearSelection()


class _MeshGroup(CommandManager):
    "The FEM_MeshGroup command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshGroup", "FEM mesh group")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MeshGroup", "Creates a FEM mesh group")
        self.is_active = "with_gmsh_femmesh"
        self.do_activated = "add_obj_on_gui_selobj_set_edit"


class _MeshNetgenFromShape(CommandManager):
    "The FEM_MeshNetgenFromShape command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "FEM_MeshNetgenFromShape", "FEM mesh from shape by Netgen"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_MeshNetgenFromShape",
            "Creates a FEM mesh from a solid or face shape by Netgen internal mesher",
        )
        self.is_active = "with_part_feature"

    def Activated(self):
        # a mesh could be made with and without an analysis,
        # we're going to check not for an analysis in command manager module
        netgen_prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Fem/Netgen")
        FreeCAD.ActiveDocument.openTransaction("Create FEM mesh Netgen")
        mesh_obj_name = "FEMMeshNetgen"
        # if requested by some people add Preference for this
        # mesh_obj_name = sel[0].Name + "_Mesh"
        FreeCADGui.addModule("ObjectsFem")
        if netgen_prefs.GetBool("UseLegacyNetgen", 1):
            FreeCADGui.doCommand(
                "ObjectsFem.makeMeshNetgenLegacy(FreeCAD.ActiveDocument, '" + mesh_obj_name + "')"
            )
        else:
            FreeCADGui.doCommand(
                "ObjectsFem.makeMeshNetgen(FreeCAD.ActiveDocument, '" + mesh_obj_name + "')"
            )
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.ActiveObject.EndStep = 'OptimizeVolume'")

        FreeCADGui.doCommand(
            "FreeCAD.ActiveDocument.ActiveObject.Shape = FreeCAD.ActiveDocument.{}".format(
                self.selobj.Name
            )
        )
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.ActiveObject.Fineness = 'Moderate'")

        # Netgen mesh object could be added without an active analysis
        # but if there is an active analysis move it in there
        import FemGui

        if FemGui.getActiveAnalysis():
            FreeCADGui.addModule("FemGui")
            FreeCADGui.doCommand(
                "FemGui.getActiveAnalysis().addObject(FreeCAD.ActiveDocument.ActiveObject)"
            )
        FreeCADGui.doCommand(
            "FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)"
        )
        FreeCADGui.Selection.clearSelection()
        # a recompute immediately starts meshing when task panel is opened, this is not intended


class _MeshRegion(CommandManager):
    "The FEM_MeshRefinement command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_MeshRegion", "FEM mesh refinement")
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_MeshRegion", "Creates a FEM mesh refinement")
        self.is_active = "with_femmesh"
        self.do_activated = "add_obj_on_gui_selobj_set_edit"


class _ResultShow(CommandManager):
    "The FEM_ResultShow command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ResultShow", "Show result")
        self.accel = "R, S"
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ResultShow", "Shows and visualizes selected result data"
        )
        self.is_active = "with_selresult"

    def Activated(self):
        self.selobj.ViewObject.Document.setEdit(self.selobj.ViewObject, 0)


class _ResultsPurge(CommandManager):
    "The FEM_ResultsPurge command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_ResultsPurge", "Purge results")
        self.accel = "R, P"
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_ResultsPurge", "Purges all results from active analysis"
        )
        self.is_active = "with_analysis"

    def Activated(self):
        import femresult.resulttools as resulttools

        resulttools.purge_results(self.active_analysis)


    def __exit__(self, exc_type, exc_value, trace):
        FreeCADGui.doCommand(f"FemGui.getActiveAnalysis().addObject({self.cli_name})")
        FreeCAD.ActiveDocument.commitTransaction()
        # expand analysis object in tree view
        expandParentObject()
        FreeCAD.ActiveDocument.recompute()


class _SolverControl(CommandManager):
    "The FEM_SolverControl command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_SolverControl", "Solver job control")
        self.accel = "S, T"
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_SolverControl",
            "Changes solver attributes and runs the calculations for the selected solver",
        )
        self.is_active = "with_solver"

    def Activated(self):
        FreeCADGui.ActiveDocument.setEdit(self.selobj, 0)


class _SolverRun(CommandManager):
    "The FEM_SolverRun command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_SolverRun", "Run solver calculations")
        self.accel = "S, R"
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "FEM_SolverRun", "Runs the calculations for the selected solver"
        )
        self.is_active = "with_solver"
        self.tool = None

    def Activated(self):
        from femsolver.run import run_fem_solver

        run_fem_solver(self.selobj)
        FreeCADGui.Selection.clearSelection()
        FreeCAD.ActiveDocument.recompute()

    def _conn(self, tool):
        QtCore.QObject.connect(
            tool.process,
            QtCore.SIGNAL("finished(int, QProcess::ExitStatus)"),
            self._process_finished,
        )

    def _process_finished(self, code, status):
        if status == QtCore.QProcess.ExitStatus.NormalExit and code == 0:
            self.tool.update_properties()
            FreeCAD.ActiveDocument.recompute()
            QtGui.QApplication.restoreOverrideCursor()
        else:
            QtGui.QApplication.restoreOverrideCursor()
            FreeCAD.Console.PrintError("Process finished with errors. Result not updated\n")


class _SolverSuqaba(CommandManager):
    "The FEM_SolverSuqaba command definition"

    def __init__(self):
        super().__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP("FEM_SolverSuqaba", "Solver Suqaba")
        self.accel = "S, Q"
        self.tooltip = Qt.QT_TRANSLATE_NOOP("FEM_SolverSuqaba", "Creates a Suqaba FEM solver")
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_expand_noset_edit"

# the string in add command will be the page name on FreeCAD wiki
FreeCADGui.addCommand("FEM_Analysis", _Analysis())
FreeCADGui.addCommand("FEM_ClippingPlaneAdd", _ClippingPlaneAdd())
FreeCADGui.addCommand("FEM_ClippingPlaneRemoveAll", _ClippingPlaneRemoveAll())
FreeCADGui.addCommand("FEM_ConstantVacuumPermittivity", _ConstantVacuumPermittivity())
FreeCADGui.addCommand("FEM_ConstraintBodyHeatSource", _ConstraintBodyHeatSource())
FreeCADGui.addCommand("FEM_ConstraintCentrif", _ConstraintCentrif())
FreeCADGui.addCommand("FEM_ConstraintCurrentDensity", _ConstraintCurrentDensity())
FreeCADGui.addCommand("FEM_ConstraintElectricChargeDensity", _ConstraintElectricChargeDensity())
FreeCADGui.addCommand("FEM_ConstraintElectrostaticPotential", _ConstraintElectrostaticPotential())
FreeCADGui.addCommand("FEM_ConstraintFlowVelocity", _ConstraintFlowVelocity())
FreeCADGui.addCommand("FEM_ConstraintInitialFlowVelocity", _ConstraintInitialFlowVelocity())
FreeCADGui.addCommand("FEM_ConstraintInitialPressure", _ConstraintInitialPressure())
FreeCADGui.addCommand("FEM_ConstraintMagnetization", _ConstraintMagnetization())
FreeCADGui.addCommand("FEM_ConstraintSectionPrint", _ConstraintSectionPrint())
FreeCADGui.addCommand("FEM_ConstraintSelfWeight", _ConstraintSelfWeight())
FreeCADGui.addCommand("FEM_ConstraintTie", _ConstraintTie())
FreeCADGui.addCommand("FEM_ElementFluid1D", _ElementFluid1D())
FreeCADGui.addCommand("FEM_ElementGeometry1D", _ElementGeometry1D())
FreeCADGui.addCommand("FEM_ElementGeometry2D", _ElementGeometry2D())
FreeCADGui.addCommand("FEM_ElementRotation1D", _ElementRotation1D())
# FreeCADGui.addCommand("FEM_EquationDeformation", _EquationDeformation())
# FreeCADGui.addCommand("FEM_EquationElasticity", _EquationElasticity())
# FreeCADGui.addCommand("FEM_EquationElectricforce", _EquationElectricforce())
# FreeCADGui.addCommand("FEM_EquationElectrostatic", _EquationElectrostatic())
# FreeCADGui.addCommand("FEM_EquationFlow", _EquationFlow())
# FreeCADGui.addCommand("FEM_EquationFlux", _EquationFlux())
# FreeCADGui.addCommand("FEM_EquationHeat", _EquationHeat())
# FreeCADGui.addCommand("FEM_EquationMagnetodynamic", _EquationMagnetodynamic())
# FreeCADGui.addCommand("FEM_EquationMagnetodynamic2D", _EquationMagnetodynamic2D())
# FreeCADGui.addCommand("FEM_EquationStaticCurrent", _EquationStaticCurrent())
FreeCADGui.addCommand("FEM_Examples", _Examples())
FreeCADGui.addCommand("FEM_MaterialEditor", _MaterialEditor())
FreeCADGui.addCommand("FEM_MaterialFluid", _MaterialFluid())
# FreeCADGui.addCommand("FEM_MaterialMechanicalNonlinear", _MaterialMechanicalNonlinear())
FreeCADGui.addCommand("FEM_MaterialReinforced", _MaterialReinforced())
FreeCADGui.addCommand("FEM_MaterialSolid", _MaterialSolid())
FreeCADGui.addCommand("FEM_FEMMesh2Mesh", _FEMMesh2Mesh())
FreeCADGui.addCommand("FEM_MeshBoundaryLayer", _MeshBoundaryLayer())
FreeCADGui.addCommand("FEM_MeshClear", _MeshClear())
FreeCADGui.addCommand("FEM_MeshDisplayInfo", _MeshDisplayInfo())
FreeCADGui.addCommand("FEM_MeshGmshFromShape", _MeshGmshFromShape())
FreeCADGui.addCommand("FEM_MeshGroup", _MeshGroup())
FreeCADGui.addCommand("FEM_MeshNetgenFromShape", _MeshNetgenFromShape())
FreeCADGui.addCommand("FEM_MeshRegion", _MeshRegion())
FreeCADGui.addCommand("FEM_ResultShow", _ResultShow())
FreeCADGui.addCommand("FEM_ResultsPurge", _ResultsPurge())
FreeCADGui.addCommand("FEM_SolverControl", _SolverControl())
FreeCADGui.addCommand("FEM_SolverRun", _SolverRun())
FreeCADGui.addCommand("FEM_SolverSuqaba", _SolverSuqaba())
