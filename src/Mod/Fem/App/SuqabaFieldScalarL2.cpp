#include "SuqabaFieldScalarL2.hpp"

//
template<>
void SuqabaFieldScalarL2<0>::getVtkFieldElementT4Sup(const u64 ii, f64* ptr_field)
{
  for (u64 i = 0; i < 4; ++i)
    ptr_field[i] = data[4 * ii + i];
}

template<>
void SuqabaFieldScalarL2<0>::addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid)
{
  vtk_grid->GetCellData()->AddArray(vtk_field);
}

template<>
u64 SuqabaFieldScalarL2<0>::getVtkFieldElementT4SupSize() const {return 4;}

template<>
u64 SuqabaFieldScalarL2<0>::getSizeField() const {return mesh.getElementT4SupCount();};


//
template<>
void SuqabaFieldScalarL2<1>::getVtkFieldElementT4Sup(const u64 ii, f64* ptr_field)
{
  for (u64 i = 0; i < 4; ++i)
    for (u64 j = 0; j < 4; ++j)
      ptr_field[4 * i + j] = data[16 * ii + 4 * i + j];
}

template<>
void SuqabaFieldScalarL2<1>::addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid)
{
  vtk_grid->GetPointData()->AddArray(vtk_field);
}

template<>
u64 SuqabaFieldScalarL2<1>::getVtkFieldElementT4SupSize() const {return 4 * 4;}

template<>
u64 SuqabaFieldScalarL2<1>::getSizeField() const {return 4 * mesh.getElementT4SupCount();};
