from mp_api.client import MPRester
import os
def get_ids(chem_formula):
    # 推荐使用环境变量来存储 API 密钥
    api_key = "Hw3bFW7AGxLzfKnDPg4EvOOPXPSw0ytI"
    if not api_key:
        raise ValueError("请设置 MATERIALS_PROJECT_API_KEY 环境变量")
    
    with MPRester(api_key) as mpr:
        try:
            # 使用 materials.summary.search 方法进行查询
            results = mpr.materials.summary.search(
                formula=chem_formula,
                crystal_system="Orthorhombic"
            )
            
            # 提取 material_id 列表
            material_ids = [result.material_id for result in results]
        
        except Exception as e:
            print(f"查询失败: {e}")
            return []
    
    return material_ids

# print(get_ids('Al176Si24'))
print(get_ids('(H2O)64'))