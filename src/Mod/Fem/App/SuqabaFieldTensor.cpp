#include "PreCompiled.h"
#include "SuqabaFieldTensor.hpp"

//
std::string SuqabaFieldTensor::toStringYieldCriterion(SuqabaFieldTensor::YieldCriterion yc) const 
{
  switch (yc)
    {
    case YieldCriterion::VonMises: return "VonMises";
    case YieldCriterion::Tresca:   return "Tresca";
    }
  return "Unknown";
}

//
void SuqabaFieldTensor::insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid)
{
  std::array<std::string, 6> field_name = {" xx ", " yy ", " zz ", " xy ", " yz ", " xz "};

  std::array<vtkNew<vtkDoubleArray>, 6> vtk_field;
  std::array<f64*, 6> ptr_field;
  
  for (u64 i = 0; i < 6; ++i)
    {
      vtk_field[i]->SetName((name + field_name[i] + unit).c_str());
      vtk_field[i]->SetNumberOfComponents(1);
      vtk_field[i]->SetNumberOfTuples(getSizeField());
      ptr_field[i] = vtk_field[i]->GetPointer(0);
    }
  
  for (u64 i = 0; i < mesh.getElementT4Count(); ++i)
     getVtkFieldElementT4Sup(i, ptr_field);

  for (u64 i = 0; i < 6; ++i)
    addFieldToVtkUnstructuredGrid(vtk_field[i], vtk_unstructured_grid);
}


//
void SuqabaFieldTensor::getVtkFieldElementT4Sup(const u64 ii, std::array<f64*, 6>& ptr_field)
{
  for (u64 i = 0; i < 4; ++i)
    for (u64 j = 0; j < 4; ++j)
      {
        const u64 rk = 16 * ii + 4 * i + j;
        for (u64 k = 0; k < 6; ++k)
          ptr_field[k][rk] = data[6 * rk + k];
      }
}

//
template<>
f64 SuqabaFieldTensor::getNorm<SuqabaFieldTensor::YieldCriterion::VonMises>(const u64 ii) 
{
  std::array<f64, 6> tensor = {data[6 * ii], data[6 * ii + 1], data[6 * ii + 2], data[6 * ii + 3], data[6 * ii + 4], data[6 * ii + 5]};
  
  const f64 tr = (tensor[0] + tensor[1] + tensor[2]) / 3.0;

  for (u64 i = 0; i < 3; ++i) 
    tensor[i] -= tr;

  f64 sig_vm = 0.0;
  for (u64 i = 0; i < 3; ++i)
    sig_vm += tensor[i] * tensor[i];

  for (u64 i = 3; i < 6; ++i)
    sig_vm += 2 * tensor[i] * tensor[i];
  
  return std::sqrt(1.5 * sig_vm);
}

//
template<>
f64 SuqabaFieldTensor::getNorm<SuqabaFieldTensor::YieldCriterion::Tresca>(const u64 ii)
{
  Eigen::Matrix<f64, 3, 3> sig; sig <<
                                  data[6 * ii + 0], data[6 * ii + 3], data[6 * ii + 5],
                                  data[6 * ii + 3], data[6 * ii + 1], data[6 * ii + 4], 
                                  data[6 * ii + 5], data[6 * ii + 4], data[6 * ii + 2];
  
  Eigen::SelfAdjointEigenSolver<Eigen::Matrix<f64, 3, 3>> sig_val(sig);
  
  return sig_val.eigenvalues()(2) - sig_val.eigenvalues()(0);
}

//
template<SuqabaFieldTensor::YieldCriterion YC>
std::unique_ptr<SuqabaFieldScalarL2<1>> SuqabaFieldTensor::getFieldNorm()
 {   
   auto field_yc = std::make_unique<SuqabaFieldScalarL2<1>>("Equivalent " + name + " " + toStringYieldCriterion(YC), unit, 4 * mesh.getElementT4SupCount(), getMesh());

   u64 ii = 0;
   for (u64 i = 0; i < mesh.getElementT4Count(); ++i)
     for (u64 j = 0; j < 4; ++j)
       for (u64 k = 0; k < 4; ++k)
         {
           field_yc->setValueField(ii, getNorm<YC>(ii));
           ++ii;
         }
   
   return field_yc;
 }

template std::unique_ptr<SuqabaFieldScalarL2<1>> SuqabaFieldTensor::getFieldNorm<SuqabaFieldTensor::YieldCriterion::VonMises>();
template std::unique_ptr<SuqabaFieldScalarL2<1>> SuqabaFieldTensor::getFieldNorm<SuqabaFieldTensor::YieldCriterion::Tresca>();

//
void SuqabaFieldTensor::setValueFieldTensorT4sup(const u64 ii, std::array<Eigen::Matrix<f64, 6, 4>, 4>& tensor)
{
  u64 cpt = 4 * 4 * 6 * ii;
  
  for (u64 i = 0; i < 4; ++i)
    for (u64 j = 0; j < 4; ++j)
      for (u64 k = 0; k < 6; ++k)
        setValueField(cpt++, tensor[i](k, j));
}
