//#include "PreCompiled.h"
#include "SuqabaZstdRead.hpp"

void SuqabaZstdRead(const std::string& filename, SuqabaMesh& mesh, std::vector<std::unique_ptr<SuqabaField>>& fields)
{
  std::ifstream file(filename, std::ios::binary);
    
  std::string line;
  std::getline(file, line);
  std::istringstream iss(line);

  std::string mesh_name;
  u64 n_node, n_edge, n_elem, order_mesh;
  iss >> mesh_name >> order_mesh >> n_node >> n_edge >> n_elem; 
  mesh.setSize(order_mesh, n_node, n_edge, n_elem);
  
  while (std::getline(file, line))
    {
      if (line == "---") break;
      std::istringstream iss(line);

      std::string name, unite, type, space;
      u64 size, order_field;
      iss >> name >> unite >> order_field >> type >> space >> size;

      if (unite == "(None)")
        unite = "";

      if (order_field == 0)
        fields.push_back(createField<0>(name, unite, type, space, size, mesh));
      else if (order_field == 1)
        fields.push_back(createField<1>(name, unite, type, space, size, mesh));
      else if (order_field == 2)
        {
          if (order_mesh == 1)
            fields.push_back(createField<1>(name, unite, type, space, size, mesh));
          else
            fields.push_back(createField<2>(name, unite, type, space, size, mesh));
        }
    }

  //
  uint64_t raw_size = 0, comp_size = 0;
  file.read(reinterpret_cast<char*>(&raw_size), sizeof(raw_size));
  file.read(reinterpret_cast<char*>(&comp_size), sizeof(comp_size));
    
  //
  std::vector<char> compressed(comp_size);
  file.read(compressed.data(), comp_size);

  //
  std::vector<char> data(raw_size);
  ZSTD_decompress(data.data(), raw_size, compressed.data(), comp_size);

  mesh.setMesh(data.data());

  u64 offset_bytes = 3 * n_node * sizeof(f64) + 10 * n_elem * sizeof(u64);

  //
  for (auto& field : fields)
    {
      field->setData(data.data() + offset_bytes);
      offset_bytes += field->getSize() * sizeof(f64);
    }
}
