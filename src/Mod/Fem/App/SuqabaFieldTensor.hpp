#pragma once

#include "SuqabaCommon.hpp"
#include "SuqabaField.hpp"
#include "SuqabaFieldScalarL2.hpp"

class SuqabaFieldTensor : public SuqabaField {
public:
  using SuqabaField::SuqabaField;

  enum class YieldCriterion {VonMises, Tresca};

  std::string toStringYieldCriterion(YieldCriterion c) const ;
  
  u64 getDim() const override {return dim;};
  
  void insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid) override;
  u64 getSizeField() const {return 4 * mesh.getElementT4SupCount();};
  u64 getVtkFieldElementT4SupSize() const {return 4 * 4;}

  void getVtkFieldElementT4Sup(const u64 i, std::array<f64*, 6>& ptr_field);
  void getVtkFieldElementT4Sup(const u64 i, f64* ptr_field) {};

  template<SuqabaFieldTensor::YieldCriterion YC>
  f64 getNorm(const u64 i);

  template<SuqabaFieldTensor::YieldCriterion YC>
  std::unique_ptr<SuqabaFieldScalarL2<1>> getFieldNorm();
  void setValueFieldTensorT4sup(const u64 i, std::array<Eigen::Matrix<f64, 6, 4>, 4>& tensor);
  
protected:
  static constexpr u64 dim = 6;
};
