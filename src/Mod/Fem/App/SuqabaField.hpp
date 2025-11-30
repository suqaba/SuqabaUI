#pragma once

#include <cstring>
#include "SuqabaCommon.hpp"
#include "SuqabaMesh.hpp"

class SuqabaField {
public:

  SuqabaField(const std::string& field_name, const std::string& unit_name, const u64 field_size, SuqabaMesh& input_mesh) :
    size(field_size), name(field_name), unit(unit_name), mesh(input_mesh) { data.resize(size); }

  virtual ~SuqabaField() = default;

  void setData(char *ptr);
  SuqabaMesh& getMesh() const {return mesh;}
  std::string getName() const {return name;}
  std::string getVtkName() const {return name + " " + unit;}
  u64 getSize() const {return size;};
  virtual u64 getDim() const {return dim;};

  virtual void setValueField(const u64 i, f64 val) {data[i] = val;}
  
  virtual u64 getSizeField() const {return 4 * mesh.getElementT4SupCount();};
  
  virtual void getVtkFieldElementT4Sup(const u64 i, f64* ptr_field) = 0;
  virtual u64 getVtkFieldElementT4SupSize() const = 0;
  
  virtual void insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid);
  virtual void addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid);
  
protected:
  static constexpr u64 dim = 1;
  u64 size;
  std::string name;
  std::string unit;
  SuqabaMesh& mesh;
  std::vector<f64> data;
};
