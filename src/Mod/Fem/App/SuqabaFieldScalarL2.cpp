#include "PreCompiled.h"
#include "SuqabaFieldScalarL2.hpp"

//
template <u64 order>
void SuqabaFieldScalarL2<order>::getVtkFieldElementSup(const u64 ii, f64* ptr_field)
{
  for (u64 i = 0; i < T4<order>::nTet; ++i)
    for (u64 j = 0; j < T4<order>::nEnt; ++j)
      ptr_field[T4<order>::nEnt * i + j] = data[T4<order>::nTet * T4<order>::nEnt * ii + T4<order>::nEnt * i + j];
}

//
template<u64 order>
u64 SuqabaFieldScalarL2<order>::getVtkFieldElementSupSize() const {return T4<order>::nTet * T4<order>::nEnt;}

template<u64 order>
u64 SuqabaFieldScalarL2<order>::getSizeField() const {return T4<order>::nEnt * mesh.getElementSupCount();};

template<u64 order>
void SuqabaFieldScalarL2<order>::addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid)
{
  if constexpr (order == 0)
    vtk_grid->GetCellData()->AddArray(vtk_field);
  else
    vtk_grid->GetPointData()->AddArray(vtk_field);
}
