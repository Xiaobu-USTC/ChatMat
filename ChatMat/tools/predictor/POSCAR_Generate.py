from mp_api.client import MPRester
from pymatgen.io.vasp import Poscar
from ChatMat.config import config
prepath = config['fp_predictor']


def POSCAR_Generate(material_id):
    # 你的 Material Project API 密钥
    api_key = "Hw3bFW7AGxLzfKnDPg4EvOOPXPSw0ytI"
    # 使用 mp-api 连接 Material Project
    mpr = MPRester(api_key)

    structure = mpr.get_structure_by_material_id(material_id,conventional_unit_cell=True)
    # 创建 POSCAR 文件
    poscar = Poscar(structure)

    # 保存为 POSCAR 文件
    poscar.write_file(f"{prepath}/POSCAR")
