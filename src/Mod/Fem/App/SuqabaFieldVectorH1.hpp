#pragma once

#include "SuqabaFieldVector.hpp"
#include "SuqabaFieldTensorL2.hpp"

class SuqabaFieldVectorH1 : public SuqabaFieldVector {
public:
  using SuqabaFieldVector::SuqabaFieldVector;

  SuqabaFieldVectorH1(const std::string& field_name, const u64 field_size, SuqabaMesh& input_mesh) : SuqabaFieldVector(field_name, field_size, input_mesh) {offset_node_edge = 3 * (mesh.getSizeNode() + mesh.getSizeEdge()); offset_node = 3 * mesh.getSizeNode();}
  
  void getVtkFieldElementT4Sup(const u64 i, f64* ptr_field) override;
  u64 getVtkFieldElementT4SupSize() const override {return 4 * 4 * 3;};

  void getGradSymElementT4sup(const u64 ii, std::array<Eigen::Matrix<f64, 6, 4>, 4> &eps);
  
  std::unique_ptr<SuqabaFieldTensorL2> getFieldGradSym(const std::string& name_field);
  Eigen::Matrix<f64, 45, 1>  getFieldElementT4Sup(const u64 ii);
  
  
  
protected:
  u64 offset_node;
  u64 offset_node_edge;
  
};
