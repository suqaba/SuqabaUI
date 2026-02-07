#pragma once

#include "SuqabaFieldTensor.hpp"

template <u64 order>
class SuqabaFieldTensorL2 : public SuqabaFieldTensor<order> {
public:
  using SuqabaFieldTensor<order>::SuqabaFieldTensor;
};

template class SuqabaFieldTensorL2<1>;
template class SuqabaFieldTensorL2<2>;
