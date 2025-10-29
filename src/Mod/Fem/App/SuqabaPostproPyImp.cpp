#include "PreCompiled.h"

#include "Mod/Fem/App/SuqabaPostpro.h"

// inclusion of the generated files (generated out of SuqabaPostproPy.xml)
#include "SuqabaPostproPy.h"
#include "SuqabaPostproPy.cpp"

using namespace Fem;

// returns a string which represents the object e.g. when printed in python
std::string SuqabaPostproPy::representation() const
{
  return {"<SuqabaPostpro object>"};
}


Py::String SuqabaPostproPy::getInputFile() const
{
  return Py::String(getSuqabaPostproPtr()->getInputFile());
}


void SuqabaPostproPy::setInputFile(Py::String file_path)
{
  getSuqabaPostproPtr()->setInputFile(Py::String(file_path));
}


PyObject* SuqabaPostproPy::setPostproRequest(PyObject* args)
{
  PyObject* listObj = nullptr;
  if (!PyArg_ParseTuple(args, "O", &listObj))
    return nullptr;

  if (!PyList_Check(listObj))
    {
      PyErr_SetString(PyExc_TypeError, "Expected a list");
      return nullptr;
    }
  
  Py_ssize_t len = PyList_Size(listObj);
  std::vector<bool> input_request(len, false);

  for (Py_ssize_t i = 0; i < len; ++i)
    {
      PyObject* item = PyList_GetItem(listObj, i);
      long val = PyLong_AsLong(item);
      
      if (val == -1 && PyErr_Occurred())
        return nullptr;
      
      input_request[i] = val != 0;
    }
  
  int errchk = getSuqabaPostproPtr()->setPostproRequest(input_request);
  
  if (errchk != 0)
    {
      PyErr_SetString(PyExc_TypeError, "List does not have expected size");
      return nullptr;
    }
    
  return Py_None;
}


PyObject* SuqabaPostproPy::run(PyObject* /* args */)
{
  int errchk = getSuqabaPostproPtr()->run();

  if (errchk != 0)
    {
      PyErr_SetString(PyExc_TypeError, "An error occurred during postprocessing");
      return nullptr;
    }
  
  return Py_None;
}


PyObject *SuqabaPostproPy::getCustomAttributes(const char* /*attr*/) const
{
  return nullptr;
}

int SuqabaPostproPy::setCustomAttributes(const char* /*attr*/, PyObject* /*obj*/)
{
  return 0;
}
