#pragma once

#include "SuqabaFieldVector.hpp"
#include "SuqabaFieldTensorL2.hpp"

template <u64 order>
class SuqabaFieldVectorH1 : public SuqabaFieldVector<order> {
public:
  using SuqabaFieldVector<order>::SuqabaFieldVector;

  SuqabaFieldVectorH1(const std::string& field_name, const std::string& unit, const u64 field_size, SuqabaMesh& input_mesh) :
    SuqabaFieldVector<order>(field_name, unit, field_size, input_mesh)
  {offset_node_edge = 3 * (this->mesh.getSizeNode() + this->mesh.getSizeEdge()); offset_node = 3 * this->mesh.getSizeNode();}
  
  void getVtkFieldElementSup(const u64 i, f64* ptr_field) override;
  u64 getVtkFieldElementSupSize() const override {return this->dim * T4<order>::nTet * T4<order>::nEnt;};
  
  void getGradSymElementSup(const u64 ii, std::array<Eigen::Matrix<f64, 6, T4<order>::nEnt>, T4<order>::nTet> &eps);
  
  std::unique_ptr<SuqabaField> getFieldGradSym(const std::string& name_field, const std::string& unit) override;
  Eigen::Matrix<f64, 45, 1>  getFieldElementSup(const u64 ii);
  
  
  
protected:
  using SuqabaField::data;
  using SuqabaField::mesh;

  u64 offset_node;
  u64 offset_node_edge;
  
};


template class SuqabaFieldVectorH1<0>;
template class SuqabaFieldVectorH1<1>;
template class SuqabaFieldVectorH1<2>;
