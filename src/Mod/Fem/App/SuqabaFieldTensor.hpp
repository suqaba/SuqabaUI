#pragma once

#include "SuqabaCommon.hpp"
#include "SuqabaField.hpp"
#include "SuqabaFieldScalarL2.hpp"

template <u64 order>
class SuqabaFieldTensor : public SuqabaField {
public:
  using SuqabaField::SuqabaField;
  using YC = YieldCriterion;
  
  std::string toStringYieldCriterion(YieldCriterion c) const ;
  
  u64 getDim() const override {return dim;};

  void insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid);

  u64 getSizeField() const {return T4<order>::nEnt * mesh.getElementSupCount();};

  u64 getVtkFieldElementSupSize() const {return T4<order>::nTet * T4<order>::nEnt;}

  void getVtkFieldElementSup(const u64 i, std::array<f64*, 6>& ptr_field);
  //void getVtkFieldElementSup(const u64 i, f64* ptr_field) {(void) i; (void) ptr_field;};
  void getVtkFieldElementSup(const u64 , f64*) override {};
  
  f64 getNorm(YC yc, const u64 i);
  std::unique_ptr<SuqabaField> getFieldNorm(YieldCriterion yc) override ;

  void setValueFieldTensorSup(const u64 i,
                              std::array<Eigen::Matrix<f64, 6, T4<order>::nEnt>,
                              T4<order>::nTet>& tensor);
  
protected:
  using SuqabaField::name;
  using SuqabaField::unit;
  using SuqabaField::data;
  using SuqabaField::mesh;
  static constexpr u64 dim = 6;
};

template class SuqabaFieldTensor<0>;
template class SuqabaFieldTensor<1>;
template class SuqabaFieldTensor<2>;
