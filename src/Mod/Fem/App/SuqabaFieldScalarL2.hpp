#pragma once

#include "SuqabaFieldScalar.hpp"

template<u64 Order>
class SuqabaFieldScalarL2 : public SuqabaFieldScalar {
public:
  using SuqabaFieldScalar::SuqabaFieldScalar;
  
  u64 getSizeField() const override;
  void getVtkFieldElementT4Sup(const u64 i, f64* ptr_field) override;
  u64 getVtkFieldElementT4SupSize() const override;
  void addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid) override;  
};
