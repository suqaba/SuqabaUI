#pragma once

#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cstring>
#include <zstd.h>
#include <cstdint>
#include <variant>
#include <iostream>


#include "SuqabaCommon.hpp"
#include "SuqabaProtos.hpp"
#include "SuqabaMesh.hpp"
#include "SuqabaFieldFactory.hpp"

void SuqabaZstdRead(const std::string& filename, SuqabaMesh& mesh, std::vector<std::unique_ptr<SuqabaField>>& field);

