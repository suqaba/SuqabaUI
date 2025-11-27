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

#ifndef GUI_TASKVIEW_TaskFemConstraintForce_H
#define GUI_TASKVIEW_TaskFemConstraintForce_H

#include <QObject>
#include <memory>

#include <Gui/Selection/Selection.h>
#include <Gui/TaskView/TaskView.h>

#include "TaskFemConstraint.h"
#include "TaskFemConstraintOnBoundary.h"
#include "ViewProviderFemConstraintForce.h"


class Ui_TaskFemConstraintForce;

namespace FemGui
{
  class TaskFemConstraintForce: public TaskFemConstraintOnBoundary
  {
    Q_OBJECT

  public:
    explicit TaskFemConstraintForce(ViewProviderFemConstraintForce* ConstraintView,
                                    QWidget* parent = nullptr);
    ~TaskFemConstraintForce() override;
    
    const std::string getReferences() const override;

    std::string get_spinxForce() const;
    std::string get_spinyForce() const;
    std::string get_spinzForce() const;
  
    std::string get_xFormula() const;
    std::string get_yFormula() const;
    std::string get_zFormula() const;
    
    bool get_forcexfree() const;
    bool get_hasForceXFormula() const;

    bool get_forceyfree() const;
    bool get_hasForceYFormula() const;

    bool get_forcezfree() const;
    bool get_hasForceZFormula() const;
                                  
  private Q_SLOTS:
    void onReferenceDeleted();
    void formulaX(bool);
    void formulaY(bool);
    void formulaZ(bool);
    void flowForce(bool state);
    void addToSelection() override;
    void removeFromSelection() override;
    
  protected:
    void changeEvent(QEvent* e) override;
    void clearButtons(const SelectionChangeModes notThis) override;

  private:
    void updateUI();
    std::unique_ptr<Ui_TaskFemConstraintForce> ui;
  };

  class TaskDlgFemConstraintForce: public TaskDlgFemConstraint
  {
    Q_OBJECT

  public:
    explicit TaskDlgFemConstraintForce(ViewProviderFemConstraintForce* ConstraintView);
    bool accept() override;
  };
  
}  // namespace FemGui

#endif  // GUI_TASKVIEW_TaskFemConstraintForce_H
