#include "PreCompiled.h"
#include "SuqabaFieldVectorH1.hpp"


//
void SuqabaFieldVectorH1::getVtkFieldElementT4Sup(const u64 ii, f64* ptr_field)
{
  constexpr u64 id_T4_sup[4][12] =
    {{ 0,  1,  2,  3,  4,  5,  6,  7,  8, 12, 13, 14},
     { 0,  1,  2,  3,  4,  5, 12, 13, 14,  9, 10, 11},
     { 0,  1,  2, 12, 13, 14,  6,  7,  8,  9, 10, 11},
     {12, 13, 14,  3,  4,  5,  6,  7,  8,  9, 10, 11}};
  
  std::array<u64, 4> i_node = mesh.getElementT4Node(ii);
  std::array<f64, 15> u_T4_sup;

  for (u64 i = 0; i < 4; ++i)
    for (u64 k = 0; k < 3; ++k)
      u_T4_sup[3 * i + k] = data[3 * i_node[i] + k];

  u_T4_sup[12] = data[offset_node_edge + 15 * ii + 0];
  u_T4_sup[13] = data[offset_node_edge + 15 * ii + 1];
  u_T4_sup[14] = data[offset_node_edge + 15 * ii + 2];
  
  u64 jj = 0;
  for (u64 i = 0; i < 4; ++i)
    for (u64 j = 0; j < 12; ++j)
      ptr_field[jj++] = u_T4_sup[id_T4_sup[i][j]];
}

//
Eigen::Matrix<f64, 45, 1> SuqabaFieldVectorH1::getFieldElementT4Sup(const u64 ii)
{
  Eigen::Matrix<f64, 45, 1> u_T4sup;

  for (u64 i = 0; i < 15; ++i)
    u_T4sup(i) = data[offset_node_edge + 15 * ii + i];

  std::array<u64, 4> i_node = mesh.getElementT4Node(ii);
  std::array<u64, 6> i_edge = mesh.getElementT4Edge(ii);
  
  for (u64 i = 0; i < 4; ++i)
    for (u64 k = 0; k < 3; ++k)
      u_T4sup(15 + 3 * i + k) = data[3 * i_node[i] + k];

  for (u64 i = 0; i < 6; ++i)
    for (u64 k = 0; k < 3; ++k)
      u_T4sup(27 + 3 * i + k) = data[offset_node + 3 * i_edge[i] + k];
  
  return u_T4sup;
}


//
void SuqabaFieldVectorH1::getGradSymElementT4sup(const u64 iel, std::array<Eigen::Matrix<f64, 6, 4>, 4> &eps)
{
  Eigen::Matrix<f64, 30, 1> u_T10;
  Eigen::Matrix<f64, 45, 1> u_T10sup = getFieldElementT4Sup(iel);

  Eigen::Matrix<f64, 3, 10> el_T10;
  Eigen::Matrix<f64, 3, 15> el_T10sup = mesh.getCoordT4Sup(iel);

  Eigen::Matrix<f64, 10,  3> DN, GN;
  Eigen::Matrix<f64,  6, 30> Be = Eigen::Matrix<f64, 6, 30>::Zero();
  Eigen::Matrix<f64,  3,  3> J;

  u64 ii[3][2] = {{0, 1}, {1, 2}, {0, 2}};
  u64 jj[3][2] = {{1, 0}, {2, 1}, {2, 0}};

  constexpr u64 ide[4][10] =
    {{5, 6, 7, 0, 9, 10, 11,  1,  2,  3},
     {5, 6, 0, 8, 9,  3,  1, 12,  4, 14},
     {5, 0, 7, 8, 1,  2, 11, 12, 13,  4},
     {0, 6, 7, 8, 3, 10,  2,  4, 13, 14}};
  
    constexpr u64 iue[4][30] =
    {{15, 16, 17, 18, 19, 20, 21, 22, 23,  0,  1,  2, 27, 28, 29, 30, 31, 32, 33, 34, 35,  3,  4,  5,  6,  7,  8,  9, 10, 11},
     {15, 16, 17, 18, 19, 20,  0,  1,  2, 24, 25, 26, 27, 28, 29,  9, 10, 11,  3,  4,  5, 36, 37, 38, 12, 13, 14, 42, 43, 44},
     {15, 16, 17,  0,  1,  2, 21, 22, 23, 24, 25, 26,  3,  4,  5,  6,  7,  8, 33, 34, 35, 36, 37, 38, 39, 40, 41, 12, 13, 14},
     { 0,  1,  2, 18, 19, 20, 21, 22, 23, 24, 25, 26,  9, 10, 11, 30, 31, 32,  6,  7,  8, 12, 13, 14, 39, 40, 41, 42, 43, 44}};

    constexpr f64 ag[4][3] = {{0., 0., 0.}, {1., 0., 0.}, {0., 1., 0.}, {0., 0., 1.}}; 
    f64 x, y, z, w;
    
    for (u64 a = 0; a < 4; ++a)
    {
      for (u64 j = 0; j < 10; ++j)
        el_T10.col(j) = el_T10sup.col(ide[a][j]);

      for (u64 j = 0; j < 30; ++j)
        u_T10(j) = u_T10sup(iue[a][j]);
      
      for (u64 g = 0; g < 4; g++)
        {
          x = ag[g][0]; y = ag[g][1]; z = ag[g][2]; w = 1. - x - y - z;

          DN <<
            0., 4. * y - 1., 0.,
            0., 0., 4. * z - 1.,
            1. - 4. * w, 1. - 4 * w, 1. - 4. * w,
            4. * x - 1., 0., 0.,
            0., 4. * z, 4. * y,
            -4. * z, -4. * z, 4. * (w - z),
            -4. * y, 4. * (w - y), -4. * y,
            4. * y, 4. * x, 0.,
            4. * (w - x), -4. * x, -4. * x,
            4. * z, 0., 4. * x;

          J = el_T10 * DN;
          GN = DN * J.inverse();
          
          for (u64 i = 0; i < 3; i++)
            for (u64 j = 0; j < 10; j++)
              Be(i, 3 * j + i) = GN(j, i);

          for (u64 i = 0; i < 3; i++)
            for (u64 j = 0; j < 10; j++)
              for (u64 k = 0; k < 2; k++)
                Be(3 + i, 3 * j + ii[i][k]) = GN(j, jj[i][k]);

          eps[a].col(g) = Be * u_T10;
        }
    }
}

//
std::unique_ptr<SuqabaFieldTensorL2> SuqabaFieldVectorH1::getFieldGradSym(const std::string& name_field, const std::string& unit)
{
  auto field_tensor = std::make_unique<SuqabaFieldTensorL2>(name_field, unit, 6 * 4 * mesh.getElementT4SupCount(), getMesh());

  std::array<Eigen::Matrix<f64, 6, 4>, 4> eps;
  for (u64 i = 0; i < mesh.getElementT4Count(); ++i)
    {
      getGradSymElementT4sup(i, eps);
      field_tensor->setValueFieldTensorT4sup(i, eps);
    }
  
  return field_tensor;
}
