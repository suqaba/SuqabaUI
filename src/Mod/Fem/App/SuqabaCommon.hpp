#pragma once

#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <eigen3/Eigen/Dense>
//#define EIGEN_DONT_PARALLELIZE

#include <vtkNew.h>
#include <vtkPoints.h>
#include <vtkCellData.h>
#include <vtkPointData.h>
#include <vtkCellArray.h>
#include <vtkDoubleArray.h>
#include <vtkSmartPointer.h>
#include <vtkUnstructuredGrid.h>
#include <vtkMultiBlockDataSet.h>
#include <vtkZLibDataCompressor.h>
#include <vtkXMLMultiBlockDataWriter.h>
#include <vtkXMLUnstructuredGridWriter.h>
#include <vtkLookupTable.h>
#include <vtkDataSetAttributes.h>

typedef std::size_t u64;
typedef double f64;

enum class YieldCriterion {VonMises, Tresca};

//
template <u64 order>
struct T4;

template<>
struct T4<0>
{
  static constexpr u64 nTet = 4;
  static constexpr u64 nEnt = 1;
};


template <>
struct T4<1>
{
  static constexpr u64 nTet = 4;
  static constexpr u64 nEnt = 4;
  static constexpr int VTK_NAME = VTK_TETRA;
  
  static constexpr f64 coord_data[nTet][nEnt][4] =
    {
      {
        {1.00, 0.00, 0.00, 0.00},
        {0.00, 1.00, 0.00, 0.00},
        {0.00, 0.00, 1.00, 0.00},
        {0.25, 0.25, 0.25, 0.25}
      },
      {
        {1.00, 0.00, 0.00, 0.00},
        {0.00, 1.00, 0.00, 0.00},
        {0.25, 0.25, 0.25, 0.25},
        {0.00, 0.00, 0.00, 1.00}
      },
      {
        {1.00, 0.00, 0.00, 0.00},
        {0.25, 0.25, 0.25, 0.25},
        {0.00, 0.00, 1.00, 0.00},
        {0.00, 0.00, 0.00, 1.00}
      },
      {
        {0.25, 0.25, 0.25, 0.25},
        {0.00, 1.00, 0.00, 0.00},
        {0.00, 0.00, 1.00, 0.00},
        {0.00, 0.00, 0.00, 1.00}
      },
    };
  

  static Eigen::Map<const Eigen::Matrix<f64, 4, 1>> coord(const u64 i,  const u64 g)  {return Eigen::Map<const Eigen::Matrix<f64, 4, 1>>(coord_data[i][g]);}
};

//
template <>
struct T4<2>
{
  static constexpr u64 nTet = 4;
  static constexpr u64 nEnt = 10;
  static constexpr int VTK_NAME = VTK_QUADRATIC_TETRA;

  //switch edge (5-6) -> (6-5)
  static constexpr f64 coord_data[nTet][nEnt][4] =
    {
      {
        {1.000, 0.000, 0.000, 0.000},
        {0.000, 1.000, 0.000, 0.000},
        {0.000, 0.000, 1.000, 0.000},
        {0.250, 0.250, 0.250, 0.250},

        {0.500, 0.500, 0.000, 0.000},
        {0.000, 0.500, 0.500, 0.000},
        {0.500, 0.000, 0.500, 0.000},

        {0.625, 0.125, 0.125, 0.125},
        {0.125, 0.625, 0.125, 0.125},
        {0.125, 0.125, 0.625, 0.125}
      },
      {
        {1.000, 0.000, 0.000, 0.000},
        {0.000, 1.000, 0.000, 0.000},
        {0.250, 0.250, 0.250, 0.250},
        {0.000, 0.000, 0.000, 1.000},
        
        {0.500, 0.500, 0.000, 0.000},
        {0.125, 0.625, 0.125, 0.125},
        {0.625, 0.125, 0.125, 0.125},
        {0.500, 0.000, 0.000, 0.500},
        {0.000, 0.500, 0.000, 0.500},
        {0.125, 0.125, 0.125, 0.625}
      },
      {
        {1.000, 0.000, 0.000, 0.000},
        {0.250, 0.250, 0.250, 0.250},
        {0.000, 0.000, 1.000, 0.000},
        {0.000, 0.000, 0.000, 1.000},
        
        {0.625, 0.125, 0.125, 0.125},
        {0.125, 0.125, 0.625, 0.125},
        {0.500, 0.000, 0.500, 0.000},
        {0.500, 0.000, 0.000, 0.500},
        {0.125, 0.125, 0.125, 0.625},
        {0.000, 0.000, 0.500, 0.500}
      },
      {
        {0.250, 0.250, 0.250, 0.250},
        {0.000, 1.000, 0.000, 0.000},
        {0.000, 0.000, 1.000, 0.000},
        {0.000, 0.000, 0.000, 1.000},
        
        {0.125, 0.625, 0.125, 0.125},
        {0.000, 0.500, 0.500, 0.000},
        {0.125, 0.125, 0.625, 0.125},
        {0.125, 0.125, 0.125, 0.625},
        {0.000, 0.500, 0.000, 0.500},
        {0.000, 0.000, 0.500, 0.500}
        }
    };
        
  static Eigen::Map<const Eigen::Matrix<f64, 4, 1>> coord(const u64 i,  const u64 g)  {return Eigen::Map<const Eigen::Matrix<f64, 4, 1>>(coord_data[i][g]);}
};

