#pragma once

#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <eigen3/Eigen/Dense>
#define EIGEN_DONT_PARALLELIZE

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

