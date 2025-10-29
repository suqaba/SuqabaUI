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
  // dummy template below
  std::ofstream outfile(input_file + "/setpostprorequest.txt", std::ios::out);
  outfile << input_file << "\n\n";
  for (const auto & x : postpro_request)
    outfile << x << " ";

  outfile << "\n\n";

  if (postpro_request[PostproQuantity::QUALORACLE])
    {
      /* quality oracle postprocessing */
      outfile << "quality oracle\n";
    }

  if (postpro_request[PostproQuantity::DISPLACEMENT])
    {
      /* displacement postprocessing */
      outfile << "displacement\n";
    }
  
  if (postpro_request[PostproQuantity::STRESS])
    {
      /* stress postprocessing */
      outfile << "stress\n";
    }
  
  if (postpro_request[PostproQuantity::VM_STRESS])
    {
      /* stress postprocessing */
      outfile << "vm stress\n";
    }
  
  outfile << std::endl;  
  outfile.close();
  
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
