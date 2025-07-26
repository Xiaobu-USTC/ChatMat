from deepmd.infer import calc_model_devi
from deepmd.infer import DeepPot as DP
import numpy as np

def data_relaticity(coord=[[1, 0, 0], [0, 0, 1.5], [1, 0, 3]], cell=10 * np.ones(3), atype = [1, 0, 1], model_list=["model.ckpt.pt"]):
    # coord = np.array(coord[0]).reshape([1, -1])
    print(coord)
    # cell = np.diag(cell).reshape([1, -1])
    print(cell)
    atype = atype
    print(atype)
    models = []
    for model in model_list:
        models.append(DP(f"{model}"))

    # Model deviation results. The first column is index of steps, 
    # the other 7 columns are max_devi_v, min_devi_v, avg_devi_v, max_devi_f, min_devi_f, avg_devi_f, devi_e
    model_devi = calc_model_devi(coord, cell, atype, models)
    return model_devi

# data_relaticity()