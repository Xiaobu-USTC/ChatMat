import re
import pandas as pd
from typing import Dict, Any, List, Optional
from ChatMat.tools.predictor.type_map import update_type_map
import dpdata
import numpy as np
import json
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from ChatMat.config import config as default_config
from ChatMat import __root_dir__
from ChatMat.config import config
from ChatMat.tools.search_csv.base import TableSearcher
from ChatMat.tools.predictor.FP_base import FP_Predictor
from ChatMat.tools.PT_Predictor.base import PT_Predictor
from ChatMat.tools.predictor.get_ids import get_ids
from ChatMat.tools.predictor.POSCAR_Generate import POSCAR_Generate
# from ChemAgent.tools.predictor.runner import MOFTransformerRunner
from ChatMat.tools.predictor.prompt import (
    PROMPT, FINAL_MARKDOWN_PROPMT, READ_PROPMT, READ_PT_PROMPT  
)
from .data_relaticity import data_relaticity
from pathlib import Path
import json
import dpdata
import numpy as np
import os
import shutil
import subprocess
 # 将路径改为当前文件夹
current_dir = os.getcwd()
print("当前工作目录：", current_dir)

# 设置当前工作目录
new_dir = current_dir + "/ChemAgent/tools/predictor"
os.chdir(new_dir)

# 再次获取当前工作目录
updated_dir = os.getcwd()
print("更新后的工作目录：", updated_dir)


# data_csv_path = '../../database/tables/data.csv'

_predictable_properties = [
    path.stem for path in Path(default_config['model_dir']).iterdir() if not path.stem.startswith('__')
]
prepath = config['fp_predictor']
model_names = ",".join(_predictable_properties)
print(f"model_name: {model_names}", _predictable_properties)
load_model_path = default_config['model_dir']
load_data_path = default_config['data_dir']

def create_folder(folder_name, path):
    """
    在指定路径下创建一个以 folder_name 命名的文件夹。

    参数：
    folder_name (str): 要创建的文件夹名称。
    path (str): 指定的路径，可以是绝对路径或相对路径。

    返回：
    None
    """
    # 拼接完整路径
    full_path = os.path.join(path, folder_name)

    try:
        # 创建文件夹，exist_ok=False 表示如果文件夹已存在，会引发异常
        os.makedirs(full_path, exist_ok=False)
        print(f"文件夹 '{folder_name}' 已成功创建在 '{path}'。")
    except FileExistsError:
        print(f"文件夹 '{folder_name}' 已存在于 '{path}'。")
    except Exception as e:
        print(f"创建文件夹时出错: {e}")

def pwdft2dpmd(pwdft_output,path):
    d_outcar = dpdata.LabeledSystem(pwdft_output, fmt = 'pwdft/hydrid')
    d_outcar.to_deepmd_raw(path+'/raw_data/')
    d_outcar.to_deepmd_npy(path+'/npy_data/')
    # 将路径下的load_model_path路径下的input.json复制到path路径下面
    src_file = os.path.join(load_model_path, 'input.json')
    dst_file = os.path.join(path, 'input.json')

    try:
        shutil.copyfile(src_file, dst_file)
        print(f"已成功复制 input.json 到: {dst_file}")
    except FileNotFoundError:
        print(f"源文件不存在: {src_file}")
    except Exception as e:
        print(f"复制文件时出错: {e}")

class Predictor(Chain):
    llm: BaseLanguageModel
    llm_chain: LLMChain
    read_chain: LLMChain
    read_pt_chain: LLMChain
    final_single_chain: LLMChain
    model_dir: str = config['model_dir']
    data_dir: str = config['data_dir']
    tool_names: str = model_names
    input_key: str = 'question'
    output_key: str = 'answer'

    # 新增字段
    # chem_formula: Optional[str] = None
    etot: Optional[float] = None
    efree: Optional[float] = None
    efreeHarris: Optional[float] = None
    fermiLevel: Optional[float] = None
    homo: Optional[float] = None
    EVdw: Optional[float] = None
    Eext: Optional[float] = None
    centroid_force: Optional[List[float]] = None
    atomic_force: Optional[float] = None
    other_result: Optional[Dict[str, float]] = None 
    egv_result: Optional[List[float]] = None
    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]
    
    def _parse_output(self, text) -> Dict[str, Any]:
        thought = re.search(r"Thought:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        PTModels = re.findall(r"PTModel:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        properties = re.findall(r"Property:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        materials = re.findall(r"Material:\s*(.+?)(?:\s*\n|$)", text, re.DOTALL)
        if not thought:
            raise ValueError(f'unknown format from LLM, no thought: {text}')
        if not properties:
            raise ValueError(f'unknown format from LLM, no properties: {text}')
        if not materials:
            raise ValueError(f'unknown format from LLM, materials: {text}')
        return {
            'Thought': thought.group(1).strip(),
            'PTModels': [pt.strip() for pt in PTModels],
            'Property': [prop.strip() for prop in properties],
            'Materials': [mat.strip() for mat in materials],
        }            

    def FP_predictor(self, mat):
        print("采用第一性原理计算软件")
        FP_Predictor(mat).cal_fp_predictor()
    
    def call_FP(self, inputs, output):
        self.FP_predictor(output['Materials'][0])
        
        file_path = 'statfile.0'
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            return f"文件不存在: {file_path}"

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "statfile.0 文件为空。"
        
        # 提取所需的数据
        from ChatMat.tools.predictor.read_agent_output import extract_atomic_force
        from ChatMat.tools.predictor.read_agent_output import extract_last_centroid_force
        from ChatMat.tools.predictor.read_agent_output import extract_last_iteration_energy
        from ChatMat.tools.predictor.read_agent_output import extract_last_energy_quantities
        self.etot = extract_last_iteration_energy(file_path)
        self.centroid_force = extract_last_centroid_force(file_path)
        self.atomic_force = extract_atomic_force(file_path)
        self.other_result = extract_last_energy_quantities(file_path)
        print(self.etot)
        print(self.centroid_force[0])
        print(self.centroid_force[0])
        print(self.atomic_force)
        print(self.other_result)
        # 检查 centroid_force 是否为包含三个元素的列表
        if not isinstance(self.centroid_force, (list, tuple)) or len(self.centroid_force) < 3:
            return "centroid_force 数据格式错误或不足。"


        final_result = self.read_chain.predict(
            question=inputs[self.input_key],
            etot=self.etot,  
            efree=self.other_result["Efree"],
            efreeHarris=self.other_result["EfreeHarris"],
            fermiLevel=self.other_result["Fermi"],
            homo=self.other_result["HOMO"],
            EVdw=self.other_result["EVdw"],
            Eext=self.other_result["Eext"],
            centroid_force_0=self.centroid_force[0],
            centroid_force_1=self.centroid_force[1],
            centroid_force_2=self.centroid_force[2],
            atomic_force=self.atomic_force
        )
        print("=======================final output:")
        print(final_result)
        # import pdb
        # pdb.set_trace()
        new_data = {
            'Name': output['Materials'][0],
            'Etot [a.u.]': self.etot,
            'Efress [a.u.]': self.other_result['Efree'],
            'EfreeHarris [a.u.]': self.other_result['EfreeHarris'],
            'EVdw [a.u.]': self.other_result['EVdw'],
            'Eext [a.u.]': self.other_result['Eext'],
            'Fermi [a.u.]': self.other_result['Fermi'],
            'HOMO [ev]': self.other_result['HOMO'],
            'Force for centroid (x) [a.u.]': self.centroid_force[0],
            'Force for centroid (y) [a.u.]': self.centroid_force[1],
            'force for centroid (z) [a.u.]': self.centroid_force[2],
            'Max force magnitude [a.u.]': self.other_result['Max force magnitude'],
        }
        # 获取答案输出之后，保存数据并训练model
        print("===============new data:")
        print(new_data)
        try:
            if not Path(load_data_path).exists():
                # 创建并写入表头
                df = pd.DataFrame([new_data])
                df.to_csv(Path(load_data_path), index=False)
                print(f"创建并写入新文件: {Path(load_data_path)}")
            else:
                # 追加数据行
                df = pd.DataFrame([new_data])
                df.to_csv(Path(load_data_path), mode='a', header=False, index=False)
                print(f"追加数据到文件: {Path(load_data_path)}")
        except Exception as e:
            print(f"写入 CSV 文件时出错: {e}")

        create_folder(output['Materials'][0], default_config['model_dir'])
        path = default_config['model_dir']+output['Materials'][0]
        #需要在文件夹力加入statfile.0文件和input.json文件
        pwdft2dpmd('statfile.0',path)

        update_type_map(output['Materials'][0], path+'/input.json')
        # os.system('dp --pt train input.json')
        subprocess.run(['dp', '--pt', 'train', 'input.json'], cwd=path, check=True)
        print("已完成MLPES模型训练")
        data = np.genfromtxt(f"{path}/lcurve.out", names=True)

        # 处理单行或多行的情况
        if data.ndim == 0:
            last = data
        else:
            last = data[-1]

        trn_result = {
            'rmse_val': float(last['rmse_val']),
            'rmse_trn': float(last['rmse_trn']),
            'rmse_e_val': float(last['rmse_e_val']),
            'rmse_e_trn': float(last['rmse_e_trn']),
            'rmse_f_val': float(last['rmse_f_val']),
            'rmse_f_trn': float(last['rmse_f_trn']),
            'lr': float(last['lr']),
        }

        result = os.path.join(path, 'result.json')
        with open(result, 'w') as json_file:
            json.dump(trn_result, json_file, indent=4)

        print(f"trn_result: {trn_result}")

    def PT_predictor(self, model_path, cor, box, atype):
        print("采用预训练模型")
        PT_Predictor_Res = PT_Predictor(model_path, cor, box, atype).cal_pt_predictor()
        return PT_Predictor_Res

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = run_manager.get_child()

        llm_output = self.llm_chain.predict(
            question=inputs[self.input_key],
            callbacks=callbacks
        )

        if config["handle_errors"]:
            try:
                output = self._parse_output(llm_output)
            except ValueError as e:
                return {self.output_key: f'ValueError : {str(e)}'}
        else:
            output = self._parse_output(llm_output)
        print(output['PTModels'])
        
        ##########################################################################
        if output['PTModels'] == ['null']:
            # apply FP predictor method
            self.call_FP(self, inputs, output)

        ###########################################################################

        else:
            print("进一步判断")
            # 获取模型路径
            model_dir = f"{load_model_path}{output['PTModels'][0]}"
            model_result_path = f"{model_dir}/result.json"
            with open(model_result_path, 'r') as file:
                pm_res = json.load(file)
                l2fa_train = pm_res['rmse_f_trn']
            ei_l = (1 + 0.1) * l2fa_train 
            ei_h = ei_l + 0.30
            # 获取分子结构
            cor = np.load(f'{model_dir}/npy_data/set.000/coord.npy')
            box = np.load(f'{model_dir}/npy_data/set.000/box.npy')
            with open(f'{model_dir}/npy_data/type.raw') as file:
                d = [line.strip() for line in file.readlines()]
                atype = [int(x) for x in d]
            # 计算误差
            model_path = f"{model_dir}/model.ckpt.pt"
            model_path_1 = f"{model_dir}/model.ckpt-1000.pt"
            # model_path_2 = f"{model_dir}/model.ckpt-8000.pt"
            model_devi = data_relaticity(cor, box, atype, [model_path,model_path_1])
            # print(ei_l)
            # print(ei_h)
            # print(model_devi[0][4])
            
            if model_devi[0][4] < ei_l:
                # 走预训练模型
                
                self.egv_result = self.PT_predictor(model_path, cor, box, atype)
                print(self.egv_result)
                final_result = self.read_pt_chain.predict(
                    question=inputs[self.input_key],
                    etot=self.egv_result[0],
                    force=self.egv_result[1],
                    virial=self.egv_result[2],
                )
                print(final_result)
            elif model_devi[0][4] > ei_h:
                # 走第一性原理软件
                self.call_FP(self, inputs, output)
            else:
                final_result = '不适合计算'
                print('不适合计算')

        # 使用 final_single_chain 生成最终回答
        formatted_output = self.final_single_chain.predict(
            question=inputs[self.input_key],
            final_result=final_result
        )
        print(formatted_output)
        return {self.output_key: formatted_output}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = PROMPT,
        read_prompt: str = READ_PROPMT,
        read_pt_prompt: str = READ_PT_PROMPT,
        final_single_prompt: str = FINAL_MARKDOWN_PROPMT,
        **kwargs: Any,
        ) -> Chain:
        template = PromptTemplate(
            template=prompt,
            input_variables=['question'],
            partial_variables={'model_names': model_names}
        )
        rd_template = PromptTemplate(
            template=read_prompt,
            input_variables=['question', 'etot', 'Efree', 'EfreeHarris', 'FermiLevel', 'HOMOEnergyLevel', 'EVdw', 'Eext', 'centroid_force_0', 'centroid_force_1', 'centroid_force_2', 'atomic_force'],
        )
        rd_pt_template = PromptTemplate(
            template=read_pt_prompt,
            input_variables=['question', 'etot', 'force', 'virial'],
        )
        fs_template = PromptTemplate(
            template=final_single_prompt,
            input_variables=['question', 'final_result']
        )

        llm_chain = LLMChain(llm=llm, prompt=template)
        read_pt_chain = LLMChain(llm=llm, prompt=rd_pt_template)
        read_chain = LLMChain(llm=llm, prompt=rd_template)
        final_single_chain = LLMChain(llm=llm, prompt=fs_template)

        return cls(
            llm=llm,
            llm_chain=llm_chain, 
            read_chain=read_chain,
            read_pt_chain=read_pt_chain,
            final_single_chain=final_single_chain,
            **kwargs
        )
