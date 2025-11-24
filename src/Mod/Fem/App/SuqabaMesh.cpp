#include <cstring>
#include "PreCompiled.h"
#include "SuqabaMesh.hpp"

//
void SuqabaMesh::setSize(const u64 n_node, const u64 n_edge, const u64 n_elem)
{
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

  std::cout << "Mesh size : " << size.node << " " << size.edge << " " << size.elem << "\n";
  
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

void SuqabaMesh::getElementT4sup(const u64 i, Eigen::Matrix<f64, 3, 5>& el)
{
  for (u64 j = 0; j < 4; ++j)
    for (u64 k = 0; k < 3; ++k)
      el(k, j) = coord[3 * node[4 * i + j] + k];

  el.col(4) = 0.25 * (el.col(0) + el.col(1) + el.col(2) + el.col(3));
}

//
vtkNew<vtkUnstructuredGrid> SuqabaMesh::getVtk()
{
  vtkNew<vtkPoints> vtk_points;
  vtk_points->SetDataTypeToDouble();
  vtk_points->SetNumberOfPoints(4 * 4 * size.elem);

  f64* ptr_points = static_cast<f64*>(vtk_points->GetVoidPointer(0));

  vtkNew<vtkIdTypeArray> cell_connectivity;
  cell_connectivity->SetNumberOfComponents(1);
  cell_connectivity->SetNumberOfValues(4 * 4 * size.elem);

  vtkIdType* ptr_cell_connectivity = cell_connectivity->GetPointer(0);

  constexpr u64 id_T4_elem[4][4] = {{0, 1, 2, 4}, {0, 1, 4, 3}, {0, 4, 2, 3}, {4, 1, 2, 3}};
  Eigen::Matrix<f64, 3, 5> el;

  u64 ii = 0, jj = 0;
  for (u64 i = 0; i < size.elem; ++i)
    {
      getElementT4sup(i, el);

      for (u64 j = 0; j < 4; ++j)
        for (u64 h = 0; h < 4; ++h)
          {
            ptr_cell_connectivity[ii] = ii; ++ii;
            
            for (u64 k = 0; k < 3; ++k)
              ptr_points[jj++] = el(k, id_T4_elem[j][h]);
          }

    }

  vtkNew<vtkCellArray> vtk_cell;
  vtk_cell->SetData(4, cell_connectivity);

  vtkNew<vtkUnstructuredGrid> vtk_unstructured_grid;
  vtk_unstructured_grid->SetPoints(vtk_points);
  vtk_unstructured_grid->SetCells(VTK_TETRA, vtk_cell);

  return vtk_unstructured_grid;
}

//
std::array<u64, 4> SuqabaMesh::getElementT4Node(const u64 ii)
{
  std::array<u64, 4> arr;

  for (u64 i = 0; i < 4; ++i)
    arr[i] = node[4 * ii + i];

  return arr;
}

//
std::array<u64, 6> SuqabaMesh::getElementT4Edge(const u64 ii)
{
  std::array<u64, 6> arr;

  for (u64 i = 0; i < 6; ++i)
    arr[i] = edge[6 * ii + i];

  return arr;
}

//
Eigen::Matrix<f64, 3, 15> SuqabaMesh::getCoordT4Sup(const u64 ii) const
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
