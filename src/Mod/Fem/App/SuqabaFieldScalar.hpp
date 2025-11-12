#pragma once

#include "SuqabaField.hpp"

class SuqabaFieldScalar : public SuqabaField {
public:
  using SuqabaField::SuqabaField;
  
  u64 getDim() const override {return dim;};
  
protected:
  static constexpr u64 dim = 1;
  
};
