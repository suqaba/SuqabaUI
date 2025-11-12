#pragma once

#include <unordered_map>

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


#include "SuqabaMesh.hpp"
#include "SuqabaFields.hpp"
#include "SuqabaZstdRead.hpp"
