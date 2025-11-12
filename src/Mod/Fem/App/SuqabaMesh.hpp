#pragma once

#include <cstring>
#include "SuqabaCommon.hpp"

struct SuqabaSizeMesh {
  u64 node = 0;
  u64 edge = 0;
  u64 elem = 0;
};

class SuqabaMesh {

public:
  SuqabaMesh() {};
  void setSize(const u64 n_node, const u64 n_edge, const u64 n_elem);
  void setMesh(char *ptr);
  void getElementT4sup(const u64 i, Eigen::Matrix<f64, 3, 5>& el);
  u64 getElementT4SupCount() const { return 4 * size.elem; }
  u64 getElementT4Count() const { return size.elem; }

  Eigen::Matrix<f64, 3, 15> getCoordT4Sup(const u64 ii) const;
  
  std::array<u64, 4> getElementT4Node(const u64 i);
  std::array<u64, 6> getElementT4Edge(const u64 i);
  vtkNew<vtkUnstructuredGrid> getVtk();

  u64 getSizeNode() const {return size.node;}
  u64 getSizeEdge() const {return size.edge;}
  
private:
  SuqabaSizeMesh size; 
  
  std::vector<f64> coord;
  std::vector<u64> node;
  std::vector<u64> edge;
  
};
