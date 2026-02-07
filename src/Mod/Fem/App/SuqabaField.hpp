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
  
  virtual u64 getSizeField() const {return 10 * mesh.getElementSupCount();};
  
  virtual void getVtkFieldElementSup(const u64 i, f64* ptr_field) = 0;
  virtual u64 getVtkFieldElementSupSize() const = 0;
  
  virtual void insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid);
  virtual void addFieldToVtkUnstructuredGrid(vtkNew<vtkDoubleArray>& vtk_field, vtkNew<vtkUnstructuredGrid>& vtk_grid);

  virtual std::unique_ptr<SuqabaField> getFieldNorm(YieldCriterion) {return nullptr;}
  virtual std::unique_ptr<SuqabaField> getFieldGradSym(const std::string&, const std::string&) {return nullptr;}
protected:
  static constexpr u64 dim = 1;
  u64 size;
  std::string name;
  std::string unit;
  SuqabaMesh& mesh;
  std::vector<f64> data;
};
