/***************************************************************************
 *   Copyright (c) 2015, 2023 FreeCAD Developers                           *
 *   Authors: Michael Hindley <hindlemp@eskom.co.za>                       *
 *            Ruan Olwagen <olwager@eskom.co.za>                           *
 *            Oswald van Ginkel <vginkeo@eskom.co.za>                      *
 *            Uwe Stöhr <uwestoehr@lyx.org>                                *
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
#ifndef _PreComp_
#include <QAction>
#include <QMessageBox>
#include <limits>
#include <sstream>
#endif

#include <Gui/Command.h>
#include <Gui/Selection/SelectionObject.h>
#include <Mod/Fem/App/FemConstraintForce.h>
#include <Mod/Part/App/PartFeature.h>

#include "TaskFemConstraintForce.h"
#include "ui_TaskFemConstraintForce.h"


using namespace FemGui;
using namespace Gui;

/* TRANSLATOR FemGui::TaskFemConstraintForce */

TaskFemConstraintForce::TaskFemConstraintForce(ViewProviderFemConstraintForce* ConstraintView, QWidget* parent)
  : TaskFemConstraintOnBoundary(ConstraintView, parent, "FEM_ConstraintForce")
  , ui(new Ui_TaskFemConstraintForce)
{
  proxy = new QWidget(this);
  ui->setupUi(proxy);
  QMetaObject::connectSlotsByName(this);

  // create a context menu for the listview of the references
  createDeleteAction(ui->lw_references);
  connect(deleteAction,
          &QAction::triggered,
          this,
          &TaskFemConstraintForce::onReferenceDeleted);
  
  connect(ui->lw_references,
          &QListWidget::currentItemChanged,
          this,
          &TaskFemConstraintForce::setSelection);
  connect(ui->lw_references,
          &QListWidget::itemClicked,
          this,
          &TaskFemConstraintForce::setSelection);

  this->groupLayout()->addWidget(proxy);

  // setup ranges
  constexpr float max = std::numeric_limits<float>::max();
  ui->spinxForce->setMinimum(-max);
  ui->spinxForce->setMaximum(max);
  ui->spinyForce->setMinimum(-max);
  ui->spinyForce->setMaximum(max);
  ui->spinzForce->setMinimum(-max);
  ui->spinzForce->setMaximum(max);

  // Get the feature data
  Fem::ConstraintForce* pcConstraint =
    ConstraintView->getObject<Fem::ConstraintForce>();
  Base::Quantity fStates[3] {};
  const char* sStates[3] {};
  bool bStates[6] {};
  fStates[0] = pcConstraint->xForce.getQuantityValue();
  fStates[1] = pcConstraint->yForce.getQuantityValue();
  fStates[2] = pcConstraint->zForce.getQuantityValue();

  sStates[0] = pcConstraint->xForceFormula.getValue();
  sStates[1] = pcConstraint->yForceFormula.getValue();
  sStates[2] = pcConstraint->zForceFormula.getValue();

  bStates[0] = false; // pcConstraint->xFree.getValue();
  bStates[1] = false; // pcConstraint->yFree.getValue();
  bStates[2] = false; // pcConstraint->zFree.getValue();
  bStates[3] = pcConstraint->hasXFormula.getValue();
  bStates[4] = pcConstraint->hasYFormula.getValue();
  bStates[5] = pcConstraint->hasZFormula.getValue();

  std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
  std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

  ui->lw_references->clear();
  for (std::size_t i = 0; i < Objects.size(); i++) {
    ui->lw_references->addItem(makeRefText(Objects[i], SubElements[i]));
  }
  if (!Objects.empty()) {
    ui->lw_references->setCurrentRow(0, QItemSelectionModel::ClearAndSelect);
  }

  // Connect check box values displacements
  connect(ui->ForceXFormulaCB,
          &QCheckBox::toggled,
          this,
          &TaskFemConstraintForce::formulaX);
  connect(ui->ForceYFormulaCB,
          &QCheckBox::toggled,
          this,
          &TaskFemConstraintForce::formulaY);
  connect(ui->ForceZFormulaCB,
          &QCheckBox::toggled,
          this,
          &TaskFemConstraintForce::formulaZ);

  // Fill data into dialog elements
  ui->spinxForce->setValue(fStates[0]);
  ui->spinyForce->setValue(fStates[1]);
  ui->spinzForce->setValue(fStates[2]);

  ui->ForceXFormulaLE->setText(QString::fromUtf8(sStates[0]));
  ui->ForceYFormulaLE->setText(QString::fromUtf8(sStates[1]));
  ui->ForceZFormulaLE->setText(QString::fromUtf8(sStates[2]));

  ui->ForceXGB->setChecked(!bStates[0]);
  ui->ForceYGB->setChecked(!bStates[1]);
  ui->ForceZGB->setChecked(!bStates[2]);

  ui->ForceXFormulaCB->setChecked(bStates[3]);
  ui->ForceYFormulaCB->setChecked(bStates[4]);
  ui->ForceZFormulaCB->setChecked(bStates[5]);


  // Selection buttons
  buttonGroup->addButton(ui->btnAdd, static_cast<int>(SelectionChangeModes::refAdd));
  buttonGroup->addButton(ui->btnRemove, static_cast<int>(SelectionChangeModes::refRemove));

  // Bind input fields to properties
  ui->spinxForce->bind(pcConstraint->xForce);
  ui->spinyForce->bind(pcConstraint->yForce);
  ui->spinzForce->bind(pcConstraint->zForce);

  updateUI();
}

TaskFemConstraintForce::~TaskFemConstraintForce() = default;

void TaskFemConstraintForce::updateUI()
{
  if (ui->lw_references->model()->rowCount() == 0) {
    // Go into reference selection mode if no reference has been selected yet
    onButtonReference(true);
    return;
  }
}

void TaskFemConstraintForce::formulaX(bool state)
{
  ui->spinxForce->setEnabled(!state);
  ui->ForceXFormulaLE->setEnabled(state);
}

void TaskFemConstraintForce::formulaY(bool state)
{
  ui->spinyForce->setEnabled(!state);
  ui->ForceYFormulaLE->setEnabled(state);
}

void TaskFemConstraintForce::formulaZ(bool state)
{
  ui->spinzForce->setEnabled(!state);
  ui->ForceZFormulaLE->setEnabled(state);
}

void TaskFemConstraintForce::flowForce(bool state)
{
  if (state) {
    ui->ForceXGB->setChecked(!state);
    ui->ForceYGB->setChecked(!state);
    ui->ForceZGB->setChecked(!state);
  }
}

void TaskFemConstraintForce::addToSelection()
{
  std::vector<Gui::SelectionObject> selection =
    Gui::Selection().getSelectionEx();  // gets vector of selected objects of active document
  if (selection.empty()) {
    QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
    return;
  }
  Fem::ConstraintForce* pcConstraint =
    ConstraintView->getObject<Fem::ConstraintForce>();
  std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
  std::vector<std::string> SubElements = pcConstraint->References.getSubValues();

  for (auto& it : selection) {  // for every selected object
    if (!it.isObjectTypeOf(Part::Feature::getClassTypeId())) {
      QMessageBox::warning(this, tr("Selection error"), tr("Selected object is not a part!"));
      return;
    }
    const std::vector<std::string>& subNames = it.getSubNames();
    App::DocumentObject* obj = it.getObject();
    for (const auto& subName : subNames) {  // for every selected sub element
      bool addMe = true;
      for (auto itr = std::ranges::find(SubElements.begin(), SubElements.end(), subName);
           itr != SubElements.end();
           itr = std::find(++itr,
                           SubElements.end(),
                           subName)) {  // for every sub element in selection that
        // matches one in old list
        if (obj
            == Objects[std::distance(
                                     SubElements.begin(),
                                     itr)]) {  // if selected sub element's object equals the one in old list
          // then it was added before so don't add
          addMe = false;
        }
      }
      // limit constraint such that only vertexes or faces or edges can be used depending on
      // what was selected first
      std::string searchStr;
      if (subName.find("Vertex") != std::string::npos) {
        searchStr = "Vertex";
      }
      else if (subName.find("Edge") != std::string::npos) {
        searchStr = "Edge";
      }
      else {
        searchStr = "Face";
      }

      if (subName.substr(0, 4) != "Face") {
        QMessageBox::warning(this, tr("Selection error"), tr("Only faces can be picked"));
        return;
      }

      for (const auto& SubElement : SubElements) {
        if (SubElement.find(searchStr) == std::string::npos) {
          QString msg = tr("Only one type of selection (vertex, face or edge) per "
                           "analysis feature allowed!");
          QMessageBox::warning(this, tr("Selection error"), msg);
          addMe = false;
          break;
        }
      }
      if (addMe) {
        QSignalBlocker block(ui->lw_references);
        Objects.push_back(obj);
        SubElements.push_back(subName);
        ui->lw_references->addItem(makeRefText(obj, subName));
      }
    }
  }
  // Update UI
  pcConstraint->References.setValues(Objects, SubElements);
  updateUI();
}

void TaskFemConstraintForce::removeFromSelection()
{
  std::vector<Gui::SelectionObject> selection =
    Gui::Selection().getSelectionEx();  // gets vector of selected objects of active document
  if (selection.empty()) {
    QMessageBox::warning(this, tr("Selection error"), tr("Nothing selected!"));
    return;
  }
  Fem::ConstraintForce* pcConstraint =
    ConstraintView->getObject<Fem::ConstraintForce>();
  std::vector<App::DocumentObject*> Objects = pcConstraint->References.getValues();
  std::vector<std::string> SubElements = pcConstraint->References.getSubValues();
  std::vector<size_t> itemsToDel;
  for (const auto& it : selection) {  // for every selected object
    if (!it.isObjectTypeOf(Part::Feature::getClassTypeId())) {
      QMessageBox::warning(this, tr("Selection error"), tr("Selected object is not a part!"));
      return;
    }
    const std::vector<std::string>& subNames = it.getSubNames();
    const App::DocumentObject* obj = it.getObject();
    
    for (const auto& subName : subNames) {  // for every selected sub element
      for (auto itr = std::ranges::find(SubElements, subName); itr != SubElements.end();
           itr = std::find(++itr,
                           SubElements.end(),
                           subName)) {  // for every sub element in selection that
        // matches one in old list
        if (obj
            == Objects[std::distance(
                                     SubElements.begin(),
                                     itr)]) {  // if selected sub element's object equals the one in old list
          // then it was added before so mark for deletion
          itemsToDel.push_back(std::distance(SubElements.begin(), itr));
        }
      }
    }
  }
  std::sort(itemsToDel.begin(), itemsToDel.end());
  while (!itemsToDel.empty()) {
    Objects.erase(Objects.begin() + itemsToDel.back());
    SubElements.erase(SubElements.begin() + itemsToDel.back());
    itemsToDel.pop_back();
  }
  // Update UI
  {
    QSignalBlocker block(ui->lw_references);
    ui->lw_references->clear();
    for (unsigned int j = 0; j < Objects.size(); j++) {
      ui->lw_references->addItem(makeRefText(Objects[j], SubElements[j]));
    }
  }
  pcConstraint->References.setValues(Objects, SubElements);
  updateUI();
}

void TaskFemConstraintForce::onReferenceDeleted()
{
  TaskFemConstraintForce::removeFromSelection();  // OvG: On right-click face is
  // automatically selected, so just remove
}

const std::string TaskFemConstraintForce::getReferences() const
{
  int rows = ui->lw_references->model()->rowCount();
  std::vector<std::string> items;
  for (int r = 0; r < rows; r++) {
    items.push_back(ui->lw_references->item(r)->text().toStdString());
  }
  return TaskFemConstraint::getReferences(items);
}

std::string TaskFemConstraintForce::get_spinxForce() const
{
  return ui->spinxForce->value().getSafeUserString();
}

std::string TaskFemConstraintForce::get_spinyForce() const
{
  return ui->spinyForce->value().getSafeUserString();
}

std::string TaskFemConstraintForce::get_spinzForce() const
{
  return ui->spinzForce->value().getSafeUserString();
}

std::string TaskFemConstraintForce::get_xFormula() const
{
  QString xFormula = ui->ForceXFormulaLE->text();
  xFormula.replace(QStringLiteral("\""), QStringLiteral("\\\""));
  return xFormula.toStdString();
}

std::string TaskFemConstraintForce::get_yFormula() const
{
  QString yFormula = ui->ForceYFormulaLE->text();
  yFormula.replace(QStringLiteral("\""), QStringLiteral("\\\""));
  return yFormula.toStdString();
}

std::string TaskFemConstraintForce::get_zFormula() const
{
  QString zFormula = ui->ForceZFormulaLE->text();
  zFormula.replace(QStringLiteral("\""), QStringLiteral("\\\""));
  return zFormula.toStdString();
}

bool TaskFemConstraintForce::get_forcexfree() const
{
  // return !ui->ForceXGB->isChecked();
  return false;
}

bool TaskFemConstraintForce::get_hasForceXFormula() const
{
  return ui->ForceXFormulaCB->isChecked();
}

bool TaskFemConstraintForce::get_forceyfree() const
{
  // return !ui->ForceYGB->isChecked();
  return false;
}

bool TaskFemConstraintForce::get_hasForceYFormula() const
{
  return ui->ForceYFormulaCB->isChecked();
}

bool TaskFemConstraintForce::get_forcezfree() const
{
  // return !ui->ForceZGB->isChecked();
  return false;
}

bool TaskFemConstraintForce::get_hasForceZFormula() const
{
  return ui->ForceZFormulaCB->isChecked();
}

void TaskFemConstraintForce::changeEvent(QEvent*)
{
  //    TaskBox::changeEvent(e);
  //    if (e->type() == QEvent::LanguageChange) {
  //        ui->if_pressure->blockSignals(true);
  //        ui->retranslateUi(proxy);
  //        ui->if_pressure->blockSignals(false);
  //    }
}

void TaskFemConstraintForce::clearButtons(const SelectionChangeModes notThis)
{
  if (notThis != SelectionChangeModes::refAdd) {
    ui->btnAdd->setChecked(false);
  }
  if (notThis != SelectionChangeModes::refRemove) {
    ui->btnRemove->setChecked(false);
  }
}

//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgFemConstraintForce::TaskDlgFemConstraintForce(ViewProviderFemConstraintForce* ConstraintView)
{
  this->ConstraintView = ConstraintView;
  assert(ConstraintView);
  this->parameter = new TaskFemConstraintForce(ConstraintView);
  
  Content.push_back(parameter);
}

//==== calls from the TaskView ===============================================================

bool TaskDlgFemConstraintForce::accept()
{
  std::string name = ConstraintView->getObject()->getNameInDocument();
  const TaskFemConstraintForce* parameterForce =
    static_cast<const TaskFemConstraintForce*>(parameter);
  
  try {
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.xForce = \"%s\"",
                            name.c_str(),
                            parameterForce->get_spinxForce().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.xForceFormula = \"%s\"",
                            name.c_str(),
                            parameterForce->get_xFormula().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.yForce = \"%s\"",
                            name.c_str(),
                            parameterForce->get_spinyForce().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.yForceFormula = \"%s\"",
                            name.c_str(),
                            parameterForce->get_yFormula().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.zForce = \"%s\"",
                            name.c_str(),
                            parameterForce->get_spinzForce().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.zForceFormula = \"%s\"",
                            name.c_str(),
                            parameterForce->get_zFormula().c_str());
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.xFree = %s",
                            name.c_str(),
                            parameterForce->get_forcexfree() ? "True" : "False");
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.hasXFormula = %s",
                            name.c_str(),
                            parameterForce->get_hasForceXFormula() ? "True" : "False");
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.yFree = %s",
                            name.c_str(),
                            parameterForce->get_forceyfree() ? "True" : "False");
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.hasYFormula = %s",
                            name.c_str(),
                            parameterForce->get_hasForceYFormula() ? "True" : "False");
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.zFree = %s",
                            name.c_str(),
                            parameterForce->get_forcezfree() ? "True" : "False");
    Gui::Command::doCommand(Gui::Command::Doc,
                            "App.ActiveDocument.%s.hasZFormula = %s",
                            name.c_str(),
                            parameterForce->get_hasForceZFormula() ? "True" : "False");
  }
  catch (const Base::Exception& e) {
    QMessageBox::warning(parameter, tr("Input error"), QString::fromLatin1(e.what()));
    return false;
  }
  
  return TaskDlgFemConstraint::accept();
}

#include "moc_TaskFemConstraintForce.cpp"
