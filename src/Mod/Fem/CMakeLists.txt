
if(BUILD_FEM_VTK)
    add_definitions(-DFC_USE_VTK)
endif(BUILD_FEM_VTK)


# suppress warnings from smesh
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_COMPILER_IS_CLANGXX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-overloaded-virtual")
endif()


# ************************************************************************************************
# ****** sub directories**************************************************************************
# ************************************************************************************************

add_subdirectory(App)

if(BUILD_GUI)
    add_subdirectory(Gui)
endif(BUILD_GUI)



# ************************************************************************************************
# ****** Python non Gui packages and modules *****************************************************
# ************************************************************************************************

SET(FemBaseModules_SRCS
    coding_conventions.md
    Init.py
    InitGui.py
    ObjectsFem.py
    TestFemApp.py
    CreateLabels.py
)

SET(FemCommands_SRCS
    femcommands/__init__.py
    femcommands/commands.py
    femcommands/manager.py
)

SET(FemExamples_SRCS
    femexamples/__init__.py
    femexamples/boxanalysis_base.py
    femexamples/boxanalysis_static.py
    femexamples/boxanalysis_frequency.py
    femexamples/buckling_platebuckling.py
    femexamples/buckling_lateraltorsionalbuckling.py
    femexamples/ccx_buckling_flexuralbuckling.py
    femexamples/ccx_cantilever_base_edge.py
    femexamples/ccx_cantilever_base_face.py
    femexamples/ccx_cantilever_base_solid.py
    femexamples/ccx_cantilever_beam_circle.py
    femexamples/ccx_cantilever_beam_pipe.py
    femexamples/ccx_cantilever_beam_rect.py
    femexamples/ccx_cantilever_ele_hexa20.py
    femexamples/ccx_cantilever_ele_quad4.py
    femexamples/ccx_cantilever_ele_quad8.py
    femexamples/ccx_cantilever_ele_tetra4.py
    femexamples/ccx_cantilever_ele_tria3.py
    femexamples/ccx_cantilever_ele_tria6.py
    femexamples/ccx_cantilever_ele_seg2.py
    femexamples/ccx_cantilever_ele_seg3.py
    femexamples/ccx_cantilever_faceload.py
    femexamples/ccx_cantilever_nodeload.py
    femexamples/ccx_cantilever_prescribeddisplacement.py
    femexamples/ccx_rigid_body.py
    femexamples/constraint_centrif.py
    femexamples/constraint_contact_shell_shell.py
    femexamples/constraint_contact_solid_solid.py
    femexamples/constraint_section_print.py
    femexamples/constraint_selfweight_cantilever.py
    femexamples/constraint_tie.py
    femexamples/constraint_transform_beam_hinged.py
    femexamples/constraint_transform_torque.py
    femexamples/examplesgui.py
    femexamples/frequency_beamsimple.py
    femexamples/manager.py
    femexamples/material_multiple_bendingbeam_fiveboxes.py
    femexamples/material_multiple_bendingbeam_fivefaces.py
    femexamples/material_multiple_tensionrod_twoboxes.py
    femexamples/material_nl_platewithhole.py
    femexamples/rc_wall_2d.py
    femexamples/square_pipe_end_twisted_edgeforces.py
    femexamples/square_pipe_end_twisted_nodeforces.py
    femexamples/thermomech_bimetal.py
    femexamples/truss_3d_cs_circle_ele_seg2.py
    femexamples/truss_3d_cs_circle_ele_seg3.py
)


SET(FemExampleMeshes_SRCS
    femexamples/meshes/__init__.py
    femexamples/meshes/mesh_beamsimple_tetra10.py
    femexamples/meshes/mesh_boxanalysis_tetra10.py
    femexamples/meshes/mesh_boxes_2_vertikal_tetra10.py
    femexamples/meshes/mesh_buckling_ibeam_tria6.py
    femexamples/meshes/mesh_buckling_plate_tria6.py
    femexamples/meshes/mesh_canticcx_hexa20.py
    femexamples/meshes/mesh_canticcx_quad4.py
    femexamples/meshes/mesh_canticcx_quad8.py
    femexamples/meshes/mesh_canticcx_seg2.py
    femexamples/meshes/mesh_canticcx_seg3.py
    femexamples/meshes/mesh_canticcx_tetra10.py
    femexamples/meshes/mesh_canticcx_tria3.py
    femexamples/meshes/mesh_canticcx_tria6.py
    femexamples/meshes/mesh_capacitance_two_balls_tetra10.py
    femexamples/meshes/mesh_constraint_centrif_tetra10.py
    femexamples/meshes/mesh_constraint_tie_tetra10.py
    femexamples/meshes/mesh_contact_box_halfcylinder_tetra10.py
    femexamples/meshes/mesh_contact_tube_tube_tria3.py
    femexamples/meshes/mesh_eigenvalue_of_elastic_beam_tetra10.py
    femexamples/meshes/mesh_flexural_buckling.py
    femexamples/meshes/mesh_multibodybeam_tetra10.py
    femexamples/meshes/mesh_multibodybeam_tria6.py
    femexamples/meshes/mesh_platewithhole_tetra10.py
    femexamples/meshes/mesh_rc_wall_2d_tria6.py
    femexamples/meshes/mesh_section_print_tetra10.py
    femexamples/meshes/mesh_selfweight_cantilever_tetra10.py
    femexamples/meshes/mesh_square_pipe_end_twisted_tria6.py
    femexamples/meshes/mesh_thermomech_bimetal_tetra10.py
    femexamples/meshes/mesh_transform_beam_hinged_tetra10.py
    femexamples/meshes/mesh_transform_torque_tetra10.py
    femexamples/meshes/mesh_truss_crane_seg2.py
    femexamples/meshes/mesh_truss_crane_seg3.py
)

SET(FemInOut_SRCS
    feminout/__init__.py
    feminout/convert2TetGen.py
    feminout/exportNastranMesh.py
    feminout/importCcxDatResults.py
    feminout/importCcxFrdResults.py
    feminout/importInpMesh.py
    feminout/importPyMesh.py
    feminout/importToolsFem.py
    feminout/importVTKResults.py
    feminout/importYamlJsonMesh.py
)

SET(FemMesh_SRCS
    femmesh/__init__.py
    femmesh/femmesh2mesh.py
    femmesh/gmshtools.py
    femmesh/meshsetsgetter.py
    femmesh/meshtools.py
    femmesh/netgentools.py
)

SET(FemObjects_SRCS
    femobjects/__init__.py
    femobjects/base_femelement.py
    femobjects/base_femmeshelement.py
    femobjects/base_fempythonobject.py
    femobjects/constant_vacuumpermittivity.py
    femobjects/constraint_bodyheatsource.py
    femobjects/constraint_centrif.py
    femobjects/constraint_currentdensity.py
    femobjects/constraint_electricchargedensity.py
    femobjects/constraint_electrostaticpotential.py
    femobjects/constraint_flowvelocity.py
    femobjects/constraint_initialflowvelocity.py
    femobjects/constraint_initialpressure.py
    femobjects/constraint_magnetization.py
    femobjects/constraint_sectionprint.py
    femobjects/constraint_selfweight.py
    femobjects/constraint_tie.py
    femobjects/element_fluid1D.py
    femobjects/element_geometry1D.py
    femobjects/element_geometry2D.py
    femobjects/element_rotation1D.py
    femobjects/material_common.py
    femobjects/material_mechanicalnonlinear.py
    femobjects/material_reinforced.py
    femobjects/mesh_boundarylayer.py
    femobjects/mesh_gmsh.py
    femobjects/mesh_group.py
    femobjects/mesh_netgen.py
    femobjects/mesh_region.py
    femobjects/mesh_result.py
    femobjects/result_mechanical.py
    femobjects/solver_ccxtools.py
)

SET(FemResult_SRCS
    femresult/__init__.py
    femresult/resulttools.py
)

SET(FemSolver_SRCS
    femsolver/__init__.py
    femsolver/equationbase.py
    femsolver/report.py
    femsolver/reportdialog.py
    femsolver/run.py
    femsolver/settings.py
    femsolver/signal.py
    femsolver/solver_taskpanel.py
    femsolver/solverbase.py
    femsolver/task.py
    femsolver/writerbase.py
)

SET(FemSolverSuqaba_ENV .env)
SET(FemSolverSuqaba_SRCS
    femsolver/suqaba/__init__.py
    femsolver/suqaba/solver.py
    femsolver/suqaba/tasks.py
    femsolver/suqaba/writer.py
)

SET(FemTests_SRCS
    femtest/__init__.py
    femtest/test_commands.sh
    femtest/test_information.md
)

SET(FemTestsApp_SRCS
    femtest/app/__init__.py
    femtest/app/support_utils.py
    femtest/app/test_ccxtools.py
    femtest/app/test_common.py
    femtest/app/test_femimport.py
    femtest/app/test_material.py
    femtest/app/test_mesh.py
    femtest/app/test_object.py
    femtest/app/test_open.py
    femtest/app/test_result.py
)

SET(FemTestsFiles_SRCS
    femtest/data/__init__.py
)

SET(FemTestsMesh_SRCS
    femtest/data/mesh/__init__.py
    femtest/data/mesh/tetra10_mesh.inp
    femtest/data/mesh/tetra10_mesh.unv
    femtest/data/mesh/tetra10_mesh.vtk
    femtest/data/mesh/tetra10_mesh.yml
)

SET(FemTestsOpen_SRCS
    femtest/data/open/__init__.py
    femtest/data/open/all_objects_de9b3fb438.FCStd
)

SET(FemTools_SRCS
    femtools/__init__.py
    femtools/ccxtools.py
    femtools/checksanalysis.py
    femtools/constants.py
    femtools/errors.py
    femtools/femutils.py
    femtools/geomtools.py
    femtools/membertools.py
    femtools/migrate_app.py
    femtools/tokrules.py
)

SET(FemAllScripts
    ${FemBaseModules_SRCS}
    ${FemCommands_SRCS}
    ${FemExamples_SRCS}
    ${FemExampleMeshes_SRCS}
    ${FemInOut_SRCS}
    ${FemMesh_SRCS}
    ${FemObjects_SRCS}
    ${FemResult_SRCS}
    ${FemSolver_SRCS}
    ${FemTests_SRCS}
    ${FemTestsApp_SRCS}
    ${FemTestsFiles_SRCS}
    ${FemTestsCcx_SRCS}
    ${FemTestsMesh_SRCS}
    ${FemTestsOpen_SRCS}
    ${FemTools_SRCS}
    ${FemSolverSuqaba_ENV}
    ${FemSolverSuqaba_SRCS}
)


ADD_CUSTOM_TARGET(FemScriptsTarget ALL
    SOURCES ${FemAllScripts}
)
fc_copy_sources(FemScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Fem" ${FemAllScripts})


# install directories for Python packages (for make install)
INSTALL(FILES ${FemBaseModules_SRCS} DESTINATION Mod/Fem)
INSTALL(FILES ${FemCommands_SRCS} DESTINATION Mod/Fem/femcommands)
INSTALL(FILES ${FemExamples_SRCS} DESTINATION Mod/Fem/femexamples)
INSTALL(FILES ${FemExampleMeshes_SRCS} DESTINATION Mod/Fem/femexamples/meshes)
INSTALL(FILES ${FemInOut_SRCS} DESTINATION Mod/Fem/feminout)
INSTALL(FILES ${FemMesh_SRCS} DESTINATION Mod/Fem/femmesh)
INSTALL(FILES ${FemObjects_SRCS} DESTINATION Mod/Fem/femobjects)
INSTALL(FILES ${FemResult_SRCS} DESTINATION Mod/Fem/femresult)
INSTALL(FILES ${FemSolver_SRCS} DESTINATION Mod/Fem/femsolver)
INSTALL(FILES ${FemTests_SRCS} DESTINATION Mod/Fem/femtest)
INSTALL(FILES ${FemTestsApp_SRCS} DESTINATION Mod/Fem/femtest/app)
INSTALL(FILES ${FemTestsFiles_SRCS} DESTINATION Mod/Fem/femtest/data)
INSTALL(FILES ${FemTestsMesh_SRCS} DESTINATION Mod/Fem/femtest/data/mesh)
INSTALL(FILES ${FemTestsOpen_SRCS} DESTINATION Mod/Fem/femtest/data/open)
INSTALL(FILES ${FemTools_SRCS} DESTINATION Mod/Fem/femtools)
INSTALL(FILES ${FemSolverSuqaba_ENV} DESTINATION Mod/Fem/)
INSTALL(FILES ${FemSolverSuqaba_SRCS} DESTINATION Mod/Fem/femsolver/suqaba)



# ************************************************************************************************
# ****** Python Gui packages and modules *********************************************************
# ************************************************************************************************

SET(FemGuiBaseModules_SRCS
    TestFemGui.py
)

SET(FemGuiObjects_SRCS
    femguiobjects/__init__.py
    femguiobjects/readme.md
)

SET(FemGuiTaskPanels_SRCS
    femtaskpanels/__init__.py
    femtaskpanels/base_femtaskpanel.py
    femtaskpanels/base_femlogtaskpanel.py
    femtaskpanels/task_constraint_bodyheatsource.py
    femtaskpanels/task_constraint_centrif.py
    femtaskpanels/task_constraint_currentdensity.py
    femtaskpanels/task_constraint_electricchargedensity.py
    femtaskpanels/task_constraint_electrostaticpotential.py
    femtaskpanels/task_constraint_flowvelocity.py
    femtaskpanels/task_constraint_initialflowvelocity.py
    femtaskpanels/task_constraint_initialpressure.py
    femtaskpanels/task_constraint_magnetization.py
    femtaskpanels/task_constraint_sectionprint.py
    femtaskpanels/task_constraint_tie.py
    femtaskpanels/task_element_fluid1D.py
    femtaskpanels/task_element_geometry1D.py
    femtaskpanels/task_element_geometry2D.py
    femtaskpanels/task_element_rotation1D.py
    femtaskpanels/task_material_common.py
    femtaskpanels/task_material_reinforced.py
    femtaskpanels/task_mesh_boundarylayer.py
    femtaskpanels/task_mesh_gmsh.py
    femtaskpanels/task_mesh_group.py
    femtaskpanels/task_mesh_region.py
    femtaskpanels/task_mesh_netgen.py
    femtaskpanels/task_result_mechanical.py
    femtaskpanels/task_solver_ccxtools.py
)

SET(FemGuiTests_SRCS
    femtest/gui/__init__.py
    femtest/gui/test_open.py
)

SET(FemGuiUtils_SRCS
    femguiutils/__init__.py
    femguiutils/disambiguate_solid_selection.py
    femguiutils/migrate_gui.py
    femguiutils/selection_widgets.py
)

SET(FemGuiViewProvider_SRCS
    femviewprovider/__init__.py
    femviewprovider/view_base_femconstraint.py
    femviewprovider/view_base_femelement.py
    femviewprovider/view_base_femmaterial.py
    femviewprovider/view_base_femmeshelement.py
    femviewprovider/view_base_femobject.py
    femviewprovider/view_constant_vacuumpermittivity.py
    femviewprovider/view_constraint_bodyheatsource.py
    femviewprovider/view_constraint_centrif.py
    femviewprovider/view_constraint_currentdensity.py
    femviewprovider/view_constraint_electricchargedensity.py
    femviewprovider/view_constraint_electrostaticpotential.py
    femviewprovider/view_constraint_flowvelocity.py
    femviewprovider/view_constraint_initialflowvelocity.py
    femviewprovider/view_constraint_initialpressure.py
    femviewprovider/view_constraint_magnetization.py
    femviewprovider/view_constraint_sectionprint.py
    femviewprovider/view_constraint_selfweight.py
    femviewprovider/view_constraint_tie.py
    femviewprovider/view_element_fluid1D.py
    femviewprovider/view_element_geometry1D.py
    femviewprovider/view_element_geometry2D.py
    femviewprovider/view_element_rotation1D.py
    femviewprovider/view_material_common.py
    femviewprovider/view_material_mechanicalnonlinear.py
    femviewprovider/view_material_reinforced.py
    femviewprovider/view_mesh_boundarylayer.py
    femviewprovider/view_mesh_gmsh.py
    femviewprovider/view_mesh_group.py
    femviewprovider/view_mesh_netgen.py
    femviewprovider/view_mesh_region.py
    femviewprovider/view_mesh_result.py
    femviewprovider/view_result_mechanical.py
    femviewprovider/view_solver_ccxtools.py
)

SET(FemGuiPreferencePages_SRCS
    fempreferencepages/__init__.py
    fempreferencepages/dlg_settings_netgen.py
)

SET(FemAllGuiScripts
    ${FemGuiBaseModules_SRCS}
    ${FemGuiObjects_SRCS}
    ${FemGuiTaskPanels_SRCS}
    ${FemGuiTests_SRCS}
    ${FemGuiUtils_SRCS}
    ${FemGuiViewProvider_SRCS}
    ${FemGuiPreferencePages_SRCS}
)

if(BUILD_GUI)
    ADD_CUSTOM_TARGET(FemGuiScriptsTarget ALL
        SOURCES ${FemAllGuiScripts}
    )
    fc_copy_sources(FemGuiScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Fem" ${FemAllGuiScripts})


    # install directories for Python packages (for make install)
    INSTALL(FILES ${FemGuiBaseModules_SRCS} DESTINATION Mod/Fem/)
    INSTALL(FILES ${FemGuiObjects_SRCS} DESTINATION Mod/Fem/femguiobjects/)
    INSTALL(FILES ${FemGuiTaskPanels_SRCS} DESTINATION Mod/Fem/femtaskpanels/)
    INSTALL(FILES ${FemGuiTests_SRCS} DESTINATION Mod/Fem/femtest/gui/)
    INSTALL(FILES ${FemGuiUtils_SRCS} DESTINATION Mod/Fem/femguiutils/)
    INSTALL(FILES ${FemGuiViewProvider_SRCS} DESTINATION Mod/Fem/femviewprovider/)
    INSTALL(FILES ${FemGuiPreferencePages_SRCS} DESTINATION Mod/Fem/fempreferencepages/)
endif(BUILD_GUI)
