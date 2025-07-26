from mp_api.client import MPRester
from pymatgen.io.vasp import Poscar
api_key = "Hw3bFW7AGxLzfKnDPg4EvOOPXPSw0ytI"
# 使用 mp-api 连接 Material Project
mpr = MPRester(api_key)

structure = mpr.get_structure_by_material_id("mp-24043")
print(structure)