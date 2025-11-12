#include "SuqabaZstdRead.hpp"

void SuqabaZstdRead(const std::string& filename, SuqabaMesh& mesh, std::vector<std::unique_ptr<SuqabaField>>& fields)
{
  std::ifstream file(filename, std::ios::binary);
    
  std::string line;
  u64 total_bytes = 0;

  std::getline(file, line);
  std::istringstream iss(line);

  std::string mesh_name;
  u64 n_node, n_edge, n_elem;
  iss >> mesh_name >> n_node >> n_edge >> n_elem; 
  mesh.setSize(n_node, n_edge, n_elem);
  
  //
  while (std::getline(file, line))
    {
      if (line == "---") break;
      std::istringstream iss(line);

      std::string name, type, space;
      u64 size;
      iss >> name >> type >> space >> size;

      fields.push_back(createField(name, type, space, size, mesh));
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
  u64 dsize = ZSTD_decompress(data.data(), raw_size, compressed.data(), comp_size);

  mesh.setMesh(data.data());

  u64 offset_bytes = 3 * n_node * sizeof(f64) + 10 * n_elem * sizeof(u64);

  //
  for (auto& field : fields)
    {
      field->setData(data.data() + offset_bytes);
      offset_bytes += field->getSize() * sizeof(f64);
    }
}
