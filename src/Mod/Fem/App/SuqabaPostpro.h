/***************************************************************************
 *   Copyright (c) 2025 Clément Vella <cvella@suqaba.com>                  *
 *                      Hugo Ginestet <hgins@suqaba.com>                   *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/


#ifndef Fem_SuqabaPostpro_H
#define Fem_SuqabaPostpro_H

#include "PreCompiled.h"
#include <App/FeaturePython.h>
#include <App/PropertyFile.h>
#include <Mod/Fem/FemGlobal.h>
#include <App/DocumentObjectPy.h>
#include <App/FeaturePythonPyImp.h>

#include "SuqabaCommon.hpp"
#include "SuqabaProtos.hpp"

namespace Fem
{

class FemExport SuqabaPostpro : public App::DocumentObject
{

PROPERTY_HEADER(Fem::SuqabaPostpro);

public:
    enum PostproQuantity {
        QUALORACLE = 0,
        DISPLACEMENT,
        STRAIN,
        STRESS,
        VM_STRAIN,
        VM_STRESS,
        TRESCA_STRAIN,
        TRESCA_STRESS,
        N_QUANTITY
    };

    SuqabaPostpro() : postpro_request(N_QUANTITY, false) {}
    ~SuqabaPostpro() = default;

    std::string getWorkingDir() const { return working_dir; }
    void setWorkingDir(std::string path) { working_dir = path; }
    
    std::string getCaseName() const { return case_name; }
    void setCaseName(std::string name) { case_name = name; }

    const std::vector<bool>& getPostproRequest() { return postpro_request; }
    int setPostproRequest(std::vector<bool> request);

    int run();

    short mustExecute() const override;
    PyObject* getPyObject() override;

private:
    std::string working_dir = "none";
    std::string case_name  = "none";
    std::vector<bool> postpro_request;
};

}  // namespace Fem

#endif  // Fem_SuqabaPostpro_H
