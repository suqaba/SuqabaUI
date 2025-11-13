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
  
  SuqabaMesh mesh;
  std::vector<std::unique_ptr<SuqabaField>> fields;
  SuqabaZstdRead(input_fullpath, mesh, fields);

  vtkNew<vtkUnstructuredGrid> vtk_unstructured_grid = mesh.getVtk();
  
  if (postpro_request[PostproQuantity::QUALORACLE])
    for (auto& field : fields)
      if (field->getName() == "Oracle")
        {
          field->insertVtkField(vtk_unstructured_grid);
          break;
        }

  if (postpro_request[PostproQuantity::DISPLACEMENT])
    for (auto& field : fields)
      if (field->getName() == "Displacement")
        {
          field->insertVtkField(vtk_unstructured_grid);
          break;
        }
  
  if (postpro_request[PostproQuantity::STRAIN])
    {
      // todo
    }

  if (postpro_request[PostproQuantity::STRESS])
    for (auto& field : fields)
      if (field->getName() == "Stress")
        {
          field->insertVtkField(vtk_unstructured_grid);
          break;
        }
  
  if (postpro_request[PostproQuantity::VM_STRAIN])
  {
    // todo
  }
  
  if (postpro_request[PostproQuantity::VM_STRESS])
    for (auto& field : fields)
      if (auto *field_tensor = dynamic_cast<SuqabaFieldTensor*>(field.get()))
        if (field_tensor->getName() == "Stress")
          {
            auto field_vm = field_tensor->getFieldNormVM();
            field_vm->insertVtkField(vtk_unstructured_grid);
          }
  
  if (postpro_request[PostproQuantity::TRESCA_STRAIN])
  {
    // todo
  }

  if (postpro_request[PostproQuantity::TRESCA_STRESS])
  {
    // todo
  }
  
  /*Strain
  for (auto& field : fields)    
    if (auto *field_vector = dynamic_cast<SuqabaFieldVectorH1*>(field.get()))
      if (field_vector->getName() == "Displacement")
        {
          auto field_tensor = field_vector->getFieldGradSym("Strain");
          field_tensor->insertVtkField(vtk_unstructured_grid);
          auto field_vm = field_tensor->getFieldNormVM();
          field_vm->insertVtkField(vtk_unstructured_grid);
        }
  */
  
  vtkNew<vtkXMLUnstructuredGridWriter> vtk_xml; 
  vtk_xml->SetFileName(output_file.c_str());
  vtk_xml->SetInputData(vtk_unstructured_grid);
  vtk_xml->SetDataModeToBinary();
  vtk_xml->SetCompressorTypeToZLib();
  vtk_xml->SetCompressionLevel(5);

  vtk_xml->Write();
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
