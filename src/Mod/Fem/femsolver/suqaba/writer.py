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

__title__ = "Suqaba writer object for FreeCAD FEM"
__author__ = "Clément Vella"
__SqbUrl__ = "https://www.suqaba.com"
__FcUrl__ = "https://www.freecad.org"

## \addtogroup FEM
#  @{

import time
import re
import pathlib
from os.path import join

import FreeCAD
import Part

from .. import writerbase

    
class FemInputWriterSuqaba(writerbase.FemInputWriter):
    def __init__(self, task_print, analysis_obj, solver_obj, member, dir_name=None):
        writerbase.FemInputWriter.__init__(self,
                                           analysis_obj,
                                           solver_obj,
                                           None, # mesh is None
                                           member,
                                           dir_name)
        self.print = task_print
        self.basename = pathlib.Path(solver_obj.Document.FileName).stem
        self.phgrname = ""
        self.partname = ""
        self.geoname  = "{}.geo".format(self.basename)
        self.jsonname = "{}.json".format(self.basename)
        self.json_string = ""
        self.geo_type = solver_obj.GeometryType
        self.ansis_type = solver_obj.AnalysisType

        self.solid_tags = []


    def write_solver_input(self):
        timestart = time.process_time()
        self.print("Input filename: {}\n".format(self.jsonname))
        self.print("Writing Suqaba input files to: {}\n".format(self.dir_name))
        
        self.export_body_to_brep()

        self.json_string += "{\n"        
        self.write_suqaba_parameters()
        self.write_suqaba_volume_load()
        self.write_suqaba_materials()
        self.write_suqaba_dirichlet()
        self.write_suqaba_neumann()
        self.json_string += "}\n\n"

        with open("{}/{}".format(self.dir_name, self.jsonname), "w") as f:
            f.write(self.json_string)

        timeend = round((time.process_time() - timestart), 2)
        self.print("Writing time input file: {} seconds\n\n".format(timeend))
        
        return self.dir_name
    

    def export_body_to_brep(self):
        if self.geo_type == "single body":
            body = FreeCAD.ActiveDocument.findObjects("PartDesign::Body")[0]
        elif self.geo_type == "compound body":
            body = None
            for obj in FreeCAD.ActiveDocument.Objects:
                if obj.isDerivedFrom("Part::Feature"):
                    if "BooleanFragments" in obj.Name:
                        body = obj
        
        self.phgrname = body.Label
        self.partname = "{}.brep".format(self.basename)
        body.Shape.exportBrep("{}/{}".format(self.dir_name, self.partname))
    

    def write_suqaba_materials(self):
        self.solid_dict = {}

        for mat in self.member.mats_linear:
            mat_obj = mat["Object"]

            young_mod   = FreeCAD.Units.Quantity(mat_obj.Material["YoungsModulus"]).getValueAs("MPa")
            poisson_rat = float(mat_obj.Material["PoissonRatio"])
            density     = FreeCAD.Units.Quantity(mat_obj.Material["Density"]).getValueAs("1000kg/mm^3")

            for ref in mat_obj.References[0][1]:
                if ref in self.centri_load_expr.keys():
                    ref_str = (
                        "        {{\n"
                        "           \"name\"   : \"{PHGR_NAME}\",\n"
                        "           \"young_modulus\": {YOUNG_MOD},\n"
                        "           \"poisson_ratio\": {POISSON_RAT},\n"
                        "           \"density\": {RHO},\n"
                        "           \"load_fx\": {{\n"
                        "                \"x\": \"{RHO} * ({FX} + {CX})\",\n"
                        "                \"y\": \"{RHO} * ({FY} + {CY})\",\n"
                        "                \"z\": \"{RHO} * ({FZ} + {CZ})\"\n"
                        "           }},\n"
                        "           \"tag\": {TAG}\n"
                        "        }}"
                    ).format(PHGR_NAME=ref,
                             TAG=self.get_tag(ref),
                             YOUNG_MOD=young_mod,
                             POISSON_RAT=poisson_rat,
                             RHO=density,
                             FX=self.gravity_force[0],
                             FY=self.gravity_force[1],
                             FZ=self.gravity_force[2],
                             CX=self.centri_load_expr[ref][0],
                             CY=self.centri_load_expr[ref][1],
                             CZ=self.centri_load_expr[ref][2])
                else:
                    ref_str = (
                        "        {{\n"
                        "           \"name\"   : \"{PHGR_NAME}\",\n"
                        "           \"young_modulus\": {YOUNG_MOD},\n"
                        "           \"poisson_ratio\": {POISSON_RAT},\n"
                        "           \"density\": {RHO},\n"
                        "           \"load_fx\": {{\n"
                        "                \"x\": \"{RHO} * {FX}\",\n"
                        "                \"y\": \"{RHO} * {FY}\",\n"
                        "                \"z\": \"{RHO} * {FZ}\"\n"
                        "           }},\n"
                        "           \"tag\": {TAG}\n"
                        "        }}"
                    ).format(PHGR_NAME=ref,
                             TAG=self.get_tag(ref),
                             YOUNG_MOD=young_mod,
                             POISSON_RAT=poisson_rat,
                             RHO=density,
                             FX=self.gravity_force[0],
                             FY=self.gravity_force[1],
                             FZ=self.gravity_force[2])

                self.solid_dict[ref] = ref_str

        key_fx = lambda x: int(x.split("\"tag\": ")[-1].split("\n")[0])
        sorted_phgr3d = sorted(self.solid_dict.values(), key=key_fx)
        separator = ",\n"
        self.json_string += "    \"PHYSICAL_GROUPS_3D\": [\n"
        self.json_string += separator.join(sorted_phgr3d)
        self.json_string += "\n    ],\n"


    def write_suqaba_dirichlet(self):
        blocks = self.member.cons_fixed
        displs = self.member.cons_displacement
        roller = self.member.cons_roller
        self.displ_dict = {}

        self.json_string += "    \"DIRICHLET\": [\n"
        separator = ",\n"
        displ_inputs = []

        if blocks:
            for block in blocks:
                block_obj = block["Object"]
                label     = block_obj.Label

                self.displ_dict[label] = []

                for obj in block_obj.References:
                    for entity in obj[1]:
                        face_tag = self.get_tag(entity)
                        self.displ_dict[label].append(face_tag)
                
                displ_inputs.append((
                        "        {{\n"
                        "            \"name\"   : \"{LABEL}\",\n"
                        "            \"load_fx\": {{\n"
                        "                \"x\": \"{UX}\",\n"
                        "                \"y\": \"{UY}\",\n"
                        "                \"z\": \"{UZ}\"\n"
                        "            }},\n"
                        "            \"tags\": [{TAGS}]\n"
                        "        }}"
                    ).format(LABEL=label,
                             UX="0.0",
                             UY="0.0",
                             UZ="0.0",
                             TAGS=", ".join(map(lambda t: str(t), self.displ_dict[label]))))
        
        if displs:
            for displ in displs:
                displ_obj = displ["Object"]
                label     = displ_obj.Label
                ux        = "0.0"
                uy        = "0.0"
                uz        = "0.0"

                self.displ_dict[label] = []

                if displ_obj.hasXFormula:
                    ux = displ_obj.xDisplacementFormula
                else:
                    ux = FreeCAD.Units.Quantity(displ_obj.xDisplacement).getValueAs("mm")

                if displ_obj.hasYFormula:
                    uy = displ_obj.yDisplacementFormula
                else:
                    uy = FreeCAD.Units.Quantity(displ_obj.yDisplacement).getValueAs("mm")

                if displ_obj.hasZFormula:
                    uz = displ_obj.zDisplacementFormula
                else:
                    uz = FreeCAD.Units.Quantity(displ_obj.zDisplacement).getValueAs("mm")

                for obj in displ_obj.References:
                    for entity in obj[1]:
                        face_tag = self.get_tag(entity)
                        self.displ_dict[label].append(face_tag)
                
                displ_inputs.append((
                        "        {{\n"
                        "            \"name\"   : \"{LABEL}\",\n"
                        "            \"load_fx\": {{\n"
                        "                \"x\": \"{UX}\",\n"
                        "                \"y\": \"{UY}\",\n"
                        "                \"z\": \"{UZ}\"\n"
                        "            }},\n"
                        "            \"tags\": [{TAGS}]\n"
                        "        }}"
                    ).format(LABEL=label,
                             UX=f"{ux}",
                             UY=f"{uy}",
                             UZ=f"{uz}",
                             TAGS=", ".join(map(lambda t: str(t), self.displ_dict[label]))))
            
        self.json_string += separator.join(displ_inputs)
        self.json_string += "\n    ],\n"

        if roller:
            self.json_string += "    \"ROLLER\": [\n"
            displ_inputs = []
            
            for roll in roller:
                roll_obj = roll["Object"]
                label = roll_obj.Label

                self.displ_dict[label] = []

                for obj in roll_obj.References:
                    for entity in obj[1]:
                        face_tag = self.get_tag(entity)
                        self.displ_dict[label].append(face_tag)
                
                displ_inputs.append((
                        "        {{\n"
                        "            \"name\"   : \"{LABEL}\",\n"
                        "            \"load_fx\": {{\n"
                        "                \"x\": \"{UX}\",\n"
                        "                \"y\": \"{UY}\",\n"
                        "                \"z\": \"{UZ}\"\n"
                        "            }},\n"
                        "            \"tags\": [{TAGS}]\n"
                        "        }}"
                    ).format(LABEL=label,
                             UX="0.0",
                             UY="0.0",
                             UZ="0.0",
                             TAGS=", ".join(map(lambda t: str(t), self.displ_dict[label]))))

            self.json_string += separator.join(displ_inputs)
            self.json_string += "\n    ],\n"
        
    
    def write_suqaba_neumann(self):
        separator = ",\n"
        self.neum_dict = {}
        neum_inputs = []

        forces = self.member.cons_force
        if forces:                
            for force in forces:
                force_obj     = force["Object"]
                direction_vec = force_obj.DirectionVector
                force_mag     = force_obj.Force.getValueAs("N")
                label         = force_obj.Label
                area          = 0.

                self.neum_dict[label] = []

                for obj in force_obj.References:
                    for entity in obj[1]:
                        face_tag = self.get_tag(entity)
                        self.neum_dict[label].append(face_tag)
                        area += obj[0].Shape.Faces[int(face_tag) - 1].Area # abstraktcv: mm^2

                neum_inputs.append((
                        "        {{\n"
                        "            \"name\"   : \"{LABEL}\",\n"
                        "            \"load_fx\": {{\n"
                        "                \"x\": \"{FX}\",\n"
                        "                \"y\": \"{FY}\",\n"
                        "                \"z\": \"{FZ}\"\n"
                        "            }},\n"
                        "            \"tags\": [{TAGS}]\n"
                        "        }}"
                    ).format(LABEL=label,
                             FX=direction_vec.x * force_mag / area,
                             FY=direction_vec.y * force_mag / area,
                             FZ=direction_vec.z * force_mag / area,
                             TAGS=", ".join(map(lambda t: str(t), self.neum_dict[label]))))

        pressures = self.member.cons_pressure
        if pressures:
            for pressure in pressures:
                pressure_obj = pressure["Object"]
                label        = pressure_obj.Label
                if pressure_obj.Reversed:
                    pressure_mag = - pressure_obj.Pressure.getValueAs("MPa")
                else:
                    pressure_mag = pressure_obj.Pressure.getValueAs("MPa")

                self.neum_dict[label] = []

                for obj in pressure_obj.References:
                    for entity in obj[1]:
                        face_tag = self.get_tag(entity)
                        self.neum_dict[label].append(face_tag)

                neum_inputs.append((
                        "        {{\n"
                        "            \"name\"   : \"{LABEL}\",\n"
                        "            \"load_fx\": {{\n"
                        "                \"p\": \"{P}\"\n"
                        "            }},\n"
                        "            \"tags\": [{TAGS}]\n"
                        "        }}"
                    ).format(LABEL=label,
                             P=pressure_mag,
                             TAGS=", ".join(map(lambda t: str(t), self.neum_dict[label]))))
        
        self.json_string += "{}{}{}".format("    \"NEUMANN\": [\n",
                                            separator.join(neum_inputs),
                                            "\n    ]\n")
    

    def write_suqaba_volume_load(self):
        selfweight_force = self.member.cons_selfweight

        self.gravity_force = [0., 0., 0.]
        if selfweight_force:
            force_obj = selfweight_force[0]["Object"]
            gravity_c = FreeCAD.Units.Quantity(force_obj.GravityAcceleration).getValueAs("mm/s^2")
            gravity_v = force_obj.GravityDirection
            
            for i in range(3):
                self.gravity_force[i] = gravity_c * gravity_v[i]

        self.centri_load_expr = {}
        forces = self.member.cons_centrif

        if forces:
            for obj in forces:
                force_obj = obj["Object"]

                if force_obj.References:
                    omega = FreeCAD.Units.Quantity(force_obj.RotationFrequency).getValueAs("0.5/pi/s")
                    part = force_obj.RotationAxis[0][0]
                    edge_ref = force_obj.RotationAxis[0][1][0]
                    edge = part.Shape.getElement(edge_ref)
                    p1 = edge.Vertexes[0].Point
                    p2 = edge.Vertexes[1].Point
                    w = p2 - p1
                    w.normalize()
                    w *= omega
                    for ref in force_obj.References[0][1]:                    
                        list_expr_x = []
                        magx = w[1]**2 + w[2]**2
                        magy = -w[0] * w[1]
                        magz = -w[0] * w[2]

                        if abs(magx) > 1.e-9:
                            list_expr_x.append(f"{magx} * (x - {p1.x})")
                        if abs(magy) > 1.e-9:
                            list_expr_x.append(f"{magy} * (y - {p1.y})")
                        if abs(magz) > 1.e-9:
                            list_expr_x.append(f"{magz} * (z - {p1.z})")
                        
                        expr_x = " + ".join(list_expr_x) if list_expr_x else "0.0"
                        expr_x = expr_x.replace("- -", "+ ")
                        expr_x = expr_x.replace("+ -", "- ")

                        list_expr_y = []
                        magx = -w[0] * w[1]
                        magy = w[0]**2 + w[2]**2
                        magz = -w[1] * w[2]

                        if abs(magx) > 1.e-9:
                            list_expr_y.append(f"{magx} * (x - {p1.x})")
                        if abs(magy) > 1.e-9:
                            list_expr_y.append(f"{magy} * (y - {p1.y})")
                        if abs(magz) > 1.e-9:
                            list_expr_y.append(f"{magz} * (z - {p1.z})")
                        
                        expr_y = " + ".join(list_expr_y) if list_expr_y else "0.0"
                        expr_y = expr_y.replace("- -", "+ ")
                        expr_y = expr_y.replace("+ -", "- ")

                        list_expr_z = []
                        magx = -w[0] * w[2]
                        magy = -w[1] * w[2]
                        magz = w[0]**2 + w[1]**2

                        if abs(magx) > 1.e-9:
                            list_expr_z.append(f"{magx} * (x - {p1.x})")
                        if abs(magy) > 1.e-9:
                            list_expr_z.append(f"{magy} * (y - {p1.y})")
                        if abs(magz) > 1.e-9:
                            list_expr_z.append(f"{magz} * (z - {p1.z})")
                        
                        expr_z = " + ".join(list_expr_z) if list_expr_z else "0.0"
                        expr_z = expr_z.replace("- -", "+ ")
                        expr_z = expr_z.replace("+ -", "- ")

                        self.centri_load_expr[ref] = [expr_x, expr_y, expr_z]


    def write_suqaba_parameters(self):
        self.json_string += (
            "    \"OMP\"       : 4,\n"
            "    \"ERROR\"     : {ERR},\n"
            # "    \"HO_STRESS\" : {HOS},\n"
            "    \"REFI_STEPS\": 7,\n"
            "    \"JOBNAME\"   : \"{JOBNAME}\",\n"
            "    \"EXPORT_BDF\": {EXPORT_BDF},\n"
            "    \"EXPORT_INP\": {EXPORT_INP},\n"
        ).format(ERR=self.solver_obj.ErrorTolerance / 100,
                #  HOS="true" if self.solver_obj.HighOrderStress else "false",
                 JOBNAME=self.basename,
                 EXPORT_BDF="true" if self.solver_obj.ExportToBdf else "false",
                 EXPORT_INP="true" if self.solver_obj.ExportToInp else "false")

    @staticmethod
    def get_tag(label):
        match = re.search(r'\d+', label)
        return match.group()

##  @}
