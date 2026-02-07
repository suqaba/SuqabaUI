#include "PreCompiled.h"
#include "SuqabaFieldTensor.hpp"

//
template <u64 order>
std::string SuqabaFieldTensor<order>::toStringYieldCriterion(YieldCriterion yc) const 
{
  switch (yc)
    {
    case YieldCriterion::VonMises: return "VonMises";
    case YieldCriterion::Tresca:   return "Tresca";
    }
  return "Unknown";
}

//
template <u64 order>
void SuqabaFieldTensor<order>::insertVtkField(vtkNew<vtkUnstructuredGrid>& vtk_unstructured_grid)
{
  std::array<std::string, dim> field_name = {" xx ", " yy ", " zz ", " xy ", " yz ", " xz "};

  std::array<vtkNew<vtkDoubleArray>, dim> vtk_field;
  std::array<f64*, dim> ptr_field;
  
  for (u64 i = 0; i < dim; ++i)
    {
      vtk_field[i]->SetName((name + field_name[i] + unit).c_str());
      vtk_field[i]->SetNumberOfComponents(1);
      vtk_field[i]->SetNumberOfTuples(getSizeField());
      ptr_field[i] = vtk_field[i]->GetPointer(0);
    }
  
  for (u64 i = 0; i < mesh.getElementCount(); ++i)
    getVtkFieldElementSup(i, ptr_field);

  for (u64 i = 0; i < dim; ++i)
    this->addFieldToVtkUnstructuredGrid(vtk_field[i], vtk_unstructured_grid);
}

//
template <u64 order>
void SuqabaFieldTensor<order>::getVtkFieldElementSup(const u64 ii, std::array<f64*, 6>& ptr_field)
{
  for (u64 i = 0; i < T4<order>::nTet; ++i)
    for (u64 j = 0; j < T4<order>::nEnt; ++j)
      {
        const u64 rk = T4<order>::nTet * T4<order>::nEnt * ii + T4<order>::nEnt * i + j;
        for (u64 k = 0; k < dim; ++k)
          ptr_field[k][rk] = data[dim * rk + k];
      }
}


//
template <u64 order>
f64 SuqabaFieldTensor<order>::getNorm(YieldCriterion yc, const u64 ii)
{
  if (yc == YieldCriterion::VonMises)
    {
      std::array<f64, dim> tensor = {
        this->data[dim * ii + 0],
        this->data[dim * ii + 1],
        this->data[dim * ii + 2],
        this->data[dim * ii + 3],
        this->data[dim * ii + 4],
        this->data[dim * ii + 5]
      };

      const f64 tr = (tensor[0] + tensor[1] + tensor[2]) / 3.0;
      for (u64 i = 0; i < 3; ++i) tensor[i] -= tr;

      f64 sig_vm = 0.0;
      for (u64 i = 0; i < 3; ++i) sig_vm += tensor[i] * tensor[i];
      for (u64 i = 3; i < dim; ++i) sig_vm += 2 * tensor[i] * tensor[i];

      return std::sqrt(1.5 * sig_vm);
    }
    
  else if (yc == YieldCriterion::Tresca)
    {
      Eigen::Matrix<f64, 3, 3> sig;
      sig << this->data[dim * ii + 0], this->data[dim * ii + 3], this->data[dim * ii + 5],
        this->data[dim * ii + 3], this->data[dim * ii + 1], this->data[dim * ii + 4],
        this->data[dim * ii + 5], this->data[dim * ii + 4], this->data[dim * ii + 2];

      Eigen::SelfAdjointEigenSolver<Eigen::Matrix<f64, 3, 3>> eig(sig);
      return eig.eigenvalues()(2) - eig.eigenvalues()(0);
    }

  std::cout << "PB\n";
  return -1.0;
}


//
template <u64 order>
std::unique_ptr<SuqabaField> SuqabaFieldTensor<order>::getFieldNorm(YieldCriterion yc)
 {   
   auto field_yc = std::make_unique<SuqabaFieldScalarL2<order>>("Equivalent " + name + " " + toStringYieldCriterion(yc), unit, T4<order>::nEnt * mesh.getElementSupCount(), this->getMesh());

   u64 ii = 0;
   for (u64 i = 0; i < mesh.getElementCount(); ++i)
     for (u64 j = 0; j < T4<order>::nTet; ++j)
       for (u64 k = 0; k < T4<order>::nEnt; ++k)
         {
           field_yc->setValueField(ii, getNorm(yc, ii));
           ++ii;
         }
   
   return field_yc;
 }

template <u64 order>
void SuqabaFieldTensor<order>::setValueFieldTensorSup(const u64 ii, std::array<Eigen::Matrix<f64, dim, T4<order>::nEnt>, T4<order>::nTet>& tensor)
{
  u64 cpt = T4<order>::nTet * T4<order>::nEnt * dim * ii;
  
  for (u64 i = 0; i < T4<order>::nTet; ++i)
    for (u64 j = 0; j < T4<order>::nEnt; ++j)
      for (u64 k = 0; k < dim; ++k)
        this->setValueField(cpt++, tensor[i](k, j));
}
