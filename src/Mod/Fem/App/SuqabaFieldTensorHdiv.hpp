#pragma once

#include "SuqabaFieldTensor.hpp"

template <u64 order>
class SuqabaFieldTensorHdiv : public SuqabaFieldTensor<order> {
public:
  using SuqabaFieldTensor<order>::SuqabaFieldTensor;

};

template class SuqabaFieldTensorHdiv<1>;
template class SuqabaFieldTensorHdiv<2>;
