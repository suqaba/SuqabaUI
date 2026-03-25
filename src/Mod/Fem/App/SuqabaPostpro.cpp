/***************************************************************************
*   Copyright (c) 2025 Suqaba <contact@suqaba.com>                         *
*                                                                          *
*   This file is part of the FreeCAD CAx development system.               *
*                                                                          *
*   This library is free software; you can redistribute it and/or          *
*   modify it under the terms of the GNU Library General Public            *
*   License as published by the Free Software Foundation; either           *
*   version 2 of the License, or (at your option) any later version.       *
*                                                                          *
*   This library  is distributed in the hope that it will be useful,       *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          * 
*   GNU Library General Public License for more details.                   *
*                                                                          *
*   You should have received a copy of the GNU Library General Public      *
*   License along with this library; see the file COPYING.LIB. If not,     *
*   write to the Free Software Foundation, Inc., 59 Temple Place,          *
*   Suite 330, Boston, MA  02111-1307, USA                                 *
*                                                                          *
***************************************************************************/

#include "PreCompiled.h"

#ifndef _PreComp_
//
#endif

#include "SuqabaPostpro.h"
#include <SuqabaPostproPy.h>


using namespace Fem;
using namespace App;

PROPERTY_SOURCE(Fem::SuqabaPostpro, App::DocumentObject)


int SuqabaPostpro::setPostproRequest(std::vector<bool> request)
{
  if (request.size() == postpro_request.size())
    {
      for (size_t i = 0; i < postpro_request.size(); ++i)
        postpro_request[i] = request[i];

      return 0;
    }
  else
    {
      return -1;
    }
}


int SuqabaPostpro::run()
{
  std::string input_fullpath = working_dir + "/" + case_name + ".zst";
  std::string    output_file = working_dir + "/" + case_name + ".vtu";
  
  std::cout << "Extracting results...\n" << std::endl;
  SuqabaMesh mesh;
  std::vector<std::unique_ptr<SuqabaField>> fields;
  SuqabaZstdRead(input_fullpath, mesh, fields);

  //
  vtkNew<vtkUnstructuredGrid> vtk_unstructured_grid;
  if (mesh.getSizeOrder() == 1)
    vtk_unstructured_grid = mesh.getVtk<1>();
  else if (mesh.getSizeOrder() == 2)
    vtk_unstructured_grid = mesh.getVtk<2>();

  //
  if (postpro_request[PostproQuantity::QUALORACLE])
    for (auto& field : fields)
      if (field->getName() == "Oracle")
        {
          field->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Local Constitutive Relation Error (CRE) done." << std::endl;
          break;
        }
  
  if (postpro_request[PostproQuantity::DISPLACEMENT])
    for (auto& field : fields)
      if (field->getName() == "Displacement")
        {
          field->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Displacement done." << std::endl;
          break;
        }
  
  if (postpro_request[PostproQuantity::STRAIN] ||
      postpro_request[PostproQuantity::VM_STRAIN] ||
      postpro_request[PostproQuantity::TRESCA_STRAIN])
    for (auto& field : fields)
      if (field->getName() == "Displacement")
        {
          std::unique_ptr<SuqabaField> field_eps = field->getFieldGradSym("Strain", "(mm/mm)");
          if (postpro_request[PostproQuantity::STRAIN])
            {
              field_eps->insertVtkField(vtk_unstructured_grid);
              std::cout << "Posprocessing Strain done." << std::endl;
            }
          fields.push_back(std::move(field_eps));
          break;
        }
  
  if (postpro_request[PostproQuantity::STRESS])
    for (auto& field : fields)
      if (field->getName() == "Stress")
        {
          field->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Stress done." << std::endl;
          break;
        }
  
  if (postpro_request[PostproQuantity::VM_STRAIN])
    for (auto& field : fields)
      if (field->getName() == "Strain")
        {
          auto field_vm = field->getFieldNorm(YieldCriterion::VonMises);
          field_vm->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Von-Mises Strain done." << std::endl;
        }
  
  if (postpro_request[PostproQuantity::VM_STRESS])
    for (auto& field : fields)
      if (field->getName() == "Stress")
        {
          auto field_vm = field->getFieldNorm(YieldCriterion::VonMises);
          field_vm->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Von-Mises Stress done." << std::endl;
        }
  
  if (postpro_request[PostproQuantity::TRESCA_STRAIN])
    for (auto& field : fields)
      if (field->getName() == "Strain")
        {
          auto field_vm = field->getFieldNorm(YieldCriterion::Tresca);
          field_vm->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Tresca Strain done." << std::endl;
        }

  if (postpro_request[PostproQuantity::TRESCA_STRESS])
    for (auto& field : fields)
      if (field->getName() == "Stress")
        {
          auto field_vm = field->getFieldNorm(YieldCriterion::Tresca);
          field_vm->insertVtkField(vtk_unstructured_grid);
          std::cout << "Posprocessing Tresca Stress done." << std::endl;
        }
  
  //
  vtkNew<vtkXMLUnstructuredGridWriter> vtk_xml; 
  vtk_xml->SetFileName(output_file.c_str());
  vtk_xml->SetInputData(vtk_unstructured_grid);
  vtk_xml->SetDataModeToBinary();
  vtk_xml->SetCompressorTypeToZLib();
  vtk_xml->SetCompressionLevel(5);

  vtk_xml->Write();
  std::cout << "\nPosprocessing done." << std::endl;
  return 0;
}


short SuqabaPostpro::mustExecute() const
{
  return 0;
}

PyObject* SuqabaPostpro::getPyObject()
{
  if (PythonObject.is(Py::_None()))
    {
      // ref counter is set to 1
      PythonObject = Py::Object(new SuqabaPostproPy(this), true);
    }
  return Py::new_reference_to(PythonObject);
}
