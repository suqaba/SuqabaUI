#pragma once

#include "SuqabaField.hpp"

template <u64 order>
class SuqabaFieldScalar : public SuqabaField {
public:
  using SuqabaField::SuqabaField;
  
  u64 getDim() const override {return dim;};
  
protected:
  static constexpr u64 dim = 1;
  
};

template class SuqabaFieldScalar<0>;
template class SuqabaFieldScalar<1>;
template class SuqabaFieldScalar<2>;
