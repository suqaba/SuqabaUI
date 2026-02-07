#include <cstring>
#include "PreCompiled.h"
#include "SuqabaMesh.hpp"

//
void SuqabaMesh::setSize(const u64 order, const u64 n_node, const u64 n_edge, const u64 n_elem)
{
  size.order = order;
  size.node = n_node;
  size.edge = n_edge;
  size.elem = n_elem;
}


//
void SuqabaMesh::setMesh(char *ptr)
{
  coord.resize(3 * size.node);

  node.resize(4 * size.elem);
  edge.resize(6 * size.elem);

  u64 offset_bytes = 0;
  
  u64 size_bytes = 3 * size.node * sizeof(u64);
  std::memcpy(coord.data(), ptr + offset_bytes, size_bytes);
  offset_bytes += size_bytes;

  size_bytes = 4 * size.elem * sizeof(u64);
  std::memcpy(node.data(), ptr + offset_bytes, size_bytes);
  offset_bytes += size_bytes;

  size_bytes = 6 * size.elem * sizeof(u64);
  std::memcpy(edge.data(), ptr + offset_bytes, size_bytes);
}

template <u64 order>
void SuqabaMesh::getElementSup(const u64 i, std::array<Eigen::Matrix<f64, 3, T4<order>::nEnt>, 4>& el)
{
  Eigen::Matrix<f64, 3, 4> elT4;
  
  for (u64 j = 0; j < 4; ++j)
    for (u64 k = 0; k < 3; ++k)
      elT4(k, j) = coord[3 * node[4 * i + j] + k];

  for (u64 j = 0; j < 4; ++j)
    for (u64 k = 0; k < T4<order>::nEnt; ++k)
      el[j].col(k) = elT4 * T4<order>::coord(j, k);
  
}

template void SuqabaMesh::getElementSup<1>(const u64 i, std::array<Eigen::Matrix<f64, 3, T4<1>::nEnt>, 4>& el);
template void SuqabaMesh::getElementSup<2>(const u64 i, std::array<Eigen::Matrix<f64, 3, T4<2>::nEnt>, 4>& el);


//
template <u64 order>
vtkNew<vtkUnstructuredGrid> SuqabaMesh::getVtk()
{
  vtkNew<vtkPoints> vtk_points;
  vtk_points->SetDataTypeToDouble();
  vtk_points->SetNumberOfPoints(4 * T4<order>::nEnt * size.elem);

  f64* ptr_points = static_cast<f64*>(vtk_points->GetVoidPointer(0));

  vtkNew<vtkIdTypeArray> cell_connectivity;
  cell_connectivity->SetNumberOfComponents(1);
  cell_connectivity->SetNumberOfValues(4 * T4<order>::nEnt * size.elem);

  vtkIdType* ptr_cell_connectivity = cell_connectivity->GetPointer(0);

  std::array<Eigen::Matrix<f64, 3, T4<order>::nEnt>, T4<order>::nTet> el;

  u64 ii = 0, jj = 0;
  for (u64 i = 0; i < size.elem; ++i)
    {
      getElementSup<order>(i, el);
      
      for (u64 j = 0; j < T4<order>::nTet; ++j)
        for (u64 h = 0; h < T4<order>::nEnt; ++h)
          {
            ptr_cell_connectivity[ii] = ii; ++ii;
            
            for (u64 k = 0; k < 3; ++k)
              ptr_points[jj++] = el[j](k, h);
          }
    }
  
  vtkNew<vtkCellArray> vtk_cell;
  vtk_cell->SetData(T4<order>::nEnt, cell_connectivity);

  vtkNew<vtkUnstructuredGrid> vtk_unstructured_grid;
  vtk_unstructured_grid->SetPoints(vtk_points);
  vtk_unstructured_grid->SetCells(T4<order>::VTK_NAME, vtk_cell);

  return vtk_unstructured_grid;
}

template vtkNew<vtkUnstructuredGrid> SuqabaMesh::getVtk<1>();
template vtkNew<vtkUnstructuredGrid> SuqabaMesh::getVtk<2>();

//
std::array<u64, 4> SuqabaMesh::getElementNode(const u64 ii)
{
  std::array<u64, 4> arr;

  for (u64 i = 0; i < 4; ++i)
    arr[i] = node[4 * ii + i];

  return arr;
}

//
std::array<u64, 6> SuqabaMesh::getElementEdge(const u64 ii)
{
  std::array<u64, 6> arr;

  for (u64 i = 0; i < 6; ++i)
    arr[i] = edge[6 * ii + i];

  return arr;
}

//
Eigen::Matrix<f64, 3, 15> SuqabaMesh::getCoordSup(const u64 ii) const
{
  Eigen::Matrix<f64, 3, 15> el;

  for (u64 i = 0; i < 4; ++i)
    for (u64 k = 0; k < 3; ++k)
      el(k, 5 + i) = coord[3 * node[4 * ii + i] + k];

  el.col(0) = 0.25 * (el.col(5) + el.col(6) + el.col(7) + el.col(8));

  el.col(9)  = 0.5 * (el.col(5) + el.col(6));
  el.col(10) = 0.5 * (el.col(6) + el.col(7));
  el.col(11) = 0.5 * (el.col(5) + el.col(7));
  el.col(12) = 0.5 * (el.col(5) + el.col(8));
  el.col(13) = 0.5 * (el.col(7) + el.col(8));
  el.col(14) = 0.5 * (el.col(6) + el.col(8));
  el.col(1)  = 0.5 * (el.col(5) + el.col(0));
  el.col(2)  = 0.5 * (el.col(7) + el.col(0));
  el.col(3)  = 0.5 * (el.col(6) + el.col(0));
  el.col(4)  = 0.5 * (el.col(8) + el.col(0));

  return el;
}
