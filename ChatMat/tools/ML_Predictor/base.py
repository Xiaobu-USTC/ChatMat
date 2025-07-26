import subprocess
import sys
import os
import numpy as np
from deepmd.infer import DeepPot

class PT_Predictor():
    def __init__(self, path, cor, box, atype):
        self.path = path
        self.cor = cor
        self.box = box
        self.atype = atype
    

    def cal_dpmd(self):
        dp = DeepPot(self.path)
        # coord = np.array([[1, 0, 0], [0, 0, 1.5], [1, 0, 3]]).reshape([1, -1])
        # cell = np.diag(10 * np.ones(3)).reshape([1, -1])
        # atype = [1, 0, 1]
        # print(self.box)
        # print(np.array(self.cor).shape)
        # print(np.diag(self.box).shape)

        e, f, v = dp.eval(np.array(self.cor).reshape([1, -1]), np.array(self.box).reshape([1, -1]), self.atype)
        # e, f, v = dp.eval(self.cor[0].reshape([1, -1]), self.box.reshape([1, -1]), self.atype)
        # print(f"e: {e}\n, f: {f}\n, v: {v}\n")
        # print(e)
        # print(f)
        return [e[0][0], f[0][0], v[0][0]]
    
    def cal_fp_predictor(self, pro):
        res= self.cal_dpmd()
        ret = ''
        if 'energy' in pro:
            ret += f'energy: {res[0]}. '
        if 'force' in pro:
            ret += f'foece: {res[1]}. '
        
        
        return ret