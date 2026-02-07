#pragma once

#include "SuqabaField.hpp"

template <u64 order>
class SuqabaFieldVector : public SuqabaField {
  
public:
  using SuqabaField::SuqabaField;

  u64 getDim() const override { return dim; }
  
protected:
  static constexpr u64 dim = 3;
  
};

template class SuqabaFieldVector<0>;
template class SuqabaFieldVector<1>;
template class SuqabaFieldVector<2>;
