#pragma once

#include "SuqabaFieldScalar.hpp"

template<u64 order>
class SuqabaFieldScalarL2 : public SuqabaFieldScalar<order> {
public:
  using SuqabaFieldScalar<order>::SuqabaFieldScalar;
  
  u64 getSizeField() const override;
  void getVtkFieldElementSup(const u64 i, f64* ptr_field) override;
  u64 getVtkFieldElementSupSize() const override;
  void addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid) override;

protected:
  using SuqabaField::data;
  using SuqabaField::mesh;
};

template class SuqabaFieldScalarL2<0>;
template class SuqabaFieldScalarL2<1>;
template class SuqabaFieldScalarL2<2>;
