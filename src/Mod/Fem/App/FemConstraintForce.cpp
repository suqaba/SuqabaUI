/***************************************************************************
 *   Copyright (c) 2015 FreeCAD Developers                                 *
 *   Authors: Michael Hindley <hindlemp@eskom.co.za>                       *
 *            Ruan Olwagen <olwager@eskom.co.za>                           *
 *            Oswald van Ginkel <vginkeo@eskom.co.za>                      *
 *   Based on Force constraint by Jan Rheinländer                          *
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

#include "PreCompiled.h"

#include "FemConstraintForce.h"


using namespace Fem;

PROPERTY_SOURCE(Fem::ConstraintForce, Fem::Constraint)

ConstraintForce::ConstraintForce()
{
    // x Force
    ADD_PROPERTY_TYPE(xFree,
                      (true),
                      "ConstraintForce",
                      App::Prop_None,
                      "Use free Surface Load in X direction");
    ADD_PROPERTY_TYPE(xForce,
                      (0.0),
                      "ConstraintForce",
                      App::Prop_None,
                      "Surface Load in local X direction");
    ADD_PROPERTY_TYPE(hasXFormula,
                      (false),
                      "ConstraintForce",
                      App::Prop_None,
                      "Surface Load in X direction as a formula");
    ADD_PROPERTY_TYPE(xForceFormula,
                      (""),
                      "ConstraintForce",
                      App::Prop_None,
                      "Formula for Surface Load in X direction");

    // y Force
    ADD_PROPERTY_TYPE(yFree,
                      (true),
                      "ConstraintForce",
                      App::Prop_None,
                      "Use free Surface Load in Y direction");
    ADD_PROPERTY_TYPE(yForce,
                      (0.0),
                      "ConstraintForce",
                      App::Prop_None,
                      "Surface Load in local Y direction");
    ADD_PROPERTY_TYPE(hasYFormula,
                      (false),
                      "ConstraintForce",
                      App::Prop_None,
                      "Define Surface Load in Y direction as a formula");
    ADD_PROPERTY_TYPE(yForceFormula,
                      (""),
                      "ConstraintForce",
                      App::Prop_None,
                      "Formula for Surface Load in Y direction");

    // z Force
    ADD_PROPERTY_TYPE(zFree,
                      (true),
                      "ConstraintForce",
                      App::Prop_None,
                      "Use free Surface Load in Z direction");
    ADD_PROPERTY_TYPE(zForce,
                      (0.0),
                      "ConstraintForce",
                      App::Prop_None,
                      "Surface Load in local Z direction");
    ADD_PROPERTY_TYPE(hasZFormula,
                      (false),
                      "ConstraintForce",
                      App::Prop_None,
                      "Define Surface Load in Z direction as a formula");
    ADD_PROPERTY_TYPE(zForceFormula,
                      (""),
                      "ConstraintForce",
                      App::Prop_None,
                      "Formula for Surface Load in Z direction");
}

App::DocumentObjectExecReturn* ConstraintForce::execute()
{
    return Constraint::execute();
}

const char* ConstraintForce::getViewProviderName() const
{
    return "FemGui::ViewProviderFemConstraintForce";
}

void ConstraintForce::handleChangedPropertyType(Base::XMLReader& reader, const char* TypeName, App::Property* prop)
{
    // properties _Displacement had App::PropertyFloat and were changed to App::PropertyPressure
    if (prop == &xForce && strcmp(TypeName, "App::PropertyFloat") == 0) {
        App::PropertyFloat xForceProperty;
        // restore the PropertyFloat to be able to set its value
        xForceProperty.Restore(reader);
        xForce.setValue(xForceProperty.getValue());
    }
    else if (prop == &yForce && strcmp(TypeName, "App::PropertyFloat") == 0) {
        App::PropertyFloat yForceProperty;
        yForceProperty.Restore(reader);
        yForce.setValue(yForceProperty.getValue());
    }
    else if (prop == &zForce && strcmp(TypeName, "App::PropertyFloat") == 0) {
        App::PropertyFloat zForceProperty;
        zForceProperty.Restore(reader);
        zForce.setValue(zForceProperty.getValue());
    }
    else {
        Constraint::handleChangedPropertyType(reader, TypeName, prop);
    }
}

void ConstraintForce::onChanged(const App::Property* prop)
{
    Constraint::onChanged(prop);
}
