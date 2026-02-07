#pragma once

#include <cstring>
#include "SuqabaCommon.hpp"

struct SuqabaSizeMesh {
  u64 order = 1;
  u64 node = 0;
  u64 edge = 0;
  u64 elem = 0;
};

class SuqabaMesh {

public:
  SuqabaMesh() {};
  void setSize(const u64 order, const u64 n_node, const u64 n_edge, const u64 n_elem);
  void setMesh(char *ptr);

  template <u64 order>
  void getElementSup(const u64 i, std::array<Eigen::Matrix<f64, 3, T4<order>::nEnt>, 4>& el);
  
  u64 getElementSupCount() const {return 4 * size.elem;}
  //u64 getElementSupCount() const {return 10 * size.elem;}
  u64 getElementCount() const {return size.elem;}

  Eigen::Matrix<f64, 3, 15> getCoordSup(const u64 ii) const;
  
  std::array<u64, 4> getElementNode(const u64 i);
  std::array<u64, 6> getElementEdge(const u64 i);

  template <u64 order>
  vtkNew<vtkUnstructuredGrid> getVtk();

  u64 getSizeNode() const {return size.node;}
  u64 getSizeEdge() const {return size.edge;}

  u64 getSizeOrder() const {return size.order;}
  
private:
  SuqabaSizeMesh size; 
  
  std::vector<f64> coord;
  std::vector<u64> node;
  std::vector<u64> edge;
  
};
