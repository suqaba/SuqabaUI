#include "PreCompiled.h"
#include "SuqabaField.hpp"

//
void SuqabaField::setData(char *ptr)
{
  std::memcpy(data.data(), ptr, size * sizeof(f64));
}

//
void SuqabaField::addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid)
{
  vtk_grid->GetPointData()->AddArray(vtk_field);
}

//
void SuqabaField::insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_grid)
{
  vtkNew<vtkDoubleArray> vtk_field;
  vtk_field->SetName(getVtkName().c_str());
  
  vtk_field->SetNumberOfComponents(getDim());
  vtk_field->SetNumberOfTuples(getSizeField());
  
  f64* ptr_field = vtk_field->GetPointer(0);

  const u64 offset = getVtkFieldElementT4SupSize();
  for (u64 i = 0; i < mesh.getElementT4Count(); ++i)
    {
      getVtkFieldElementT4Sup(i, ptr_field);
      ptr_field += offset;
    }

  addFieldToVtkUnstructuredGrid(vtk_field, vtk_grid);
}
