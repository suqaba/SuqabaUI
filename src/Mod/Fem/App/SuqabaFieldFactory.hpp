#pragma once
#include "SuqabaCommon.hpp"
#include "SuqabaFields.hpp"

inline std::unique_ptr<SuqabaField> createField(const std::string& name, const std::string& type, const std::string& space, const u64 size, SuqabaMesh& mesh)
{
  if (type == "Scalar")
    {
      if (space == "L2")
        return std::make_unique<SuqabaFieldScalarL2<0>>(name, size, mesh);
      
    }
  else if (type == "Vector")
    {
      if (space == "H1")
        return std::make_unique<SuqabaFieldVectorH1>(name, size, mesh);
      
      throw std::runtime_error("Espace non reconnu : " + space);
    }
  else if (type == "Tensor")
    {
      if (space == "L2")
        return std::make_unique<SuqabaFieldTensorL2>(name, size, mesh);
      else if (space == "Hdiv")
        return std::make_unique<SuqabaFieldTensorHdiv>(name, size, mesh);

      throw std::runtime_error("Espace non reconnu : " + space);
    }
  
  throw std::runtime_error("Type non reconnu : " + type);
}

