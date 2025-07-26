import re
import pandas as pd
from typing import Dict, Any, List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from ChatMat.config import config as default_config
from ChatMat import __root_dir__
from ChatMat.config import config
from ChemAgent2pl.ChatMat.tools.FP_Predictor.base import FP_Predictor
from ChatMat.tools.ML_Predictor.base import PT_Predictor
from ChemAgent2pl.ChatMat.tools.FP_Predictor.get_ids import get_ids
from ChemAgent2pl.ChatMat.tools.FP_Predictor.POSCAR_Generate import POSCAR_Generate
# from ChemAgent.tools.predictor.runner import MOFTransformerRunner
from ChatMat.tools.predictor.prompt import (
    PROMPT, FINAL_MARKDOWN_PROPMT, READ_PROPMT
)
from ..predictor.data_relaticity import data_relaticity
from pathlib import Path
import json
import dpdata
import numpy as np
import os

_predictable_properties = [
    path.stem for path in Path(default_config['model_dir']).iterdir() if not path.stem.startswith('__')
]
load_model_path = default_config['model_dir']
prepath = config['fp_predictor']
model_names = ",".join(_predictable_properties)
print(f"model_name: {model_names}", _predictable_properties)

class Predictor(Chain):
    llm: BaseLanguageModel
    llm_chain: LLMChain
    read_chain: LLMChain
    final_single_chain: LLMChain
    model_dir: str = config['model_dir']
    data_dir: str = config['data_dir']
    tool_names: str = model_names
    input_key: str = 'question'
    output_key: str = 'answer'

    # 新增字段
    # chem_formula: Optional[str] = None
    etot: Optional[float] = None
    centroid_force: Optional[List[float]] = None  # 定义为包含三个浮点数的列表
    atomic_force: Optional[float] = None

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
    
    def PT_predictor(self, pro, model_path, cor, box, atype):
        print("采用预训练模型")
        PT_Predictor_Res = PT_Predictor(model_path, cor, box, atype).cal_fp_predictor(pro)
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
        # print(output['PTModels'])
        # self.FP_predictor(output['Materials'][0])
        if output['PTModels'] == ['null']:
            self.FP_predictor(output['Materials'][0])
            file_path = '/home/shuai-2204/code/AgentCode/ChemAgent_test/ChemAgent/tools/predictor/statfile.0'
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                return f"文件不存在: {file_path}"

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return "statfile.0 文件为空。"
            
            # 提取所需的数据
            from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_atomic_force
            from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_last_centroid_force
            from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_last_iteration_energy
            self.etot = extract_last_iteration_energy(file_path)
            self.centroid_force = extract_last_centroid_force(file_path)
            self.atomic_force = extract_atomic_force(file_path)
            
            # print(self.etot)
            # print(self.centroid_force)
            # print(self.atomic_force)
            # 检查 centroid_force 是否为包含三个元素的列表
            if not isinstance(self.centroid_force, (list, tuple)) or len(self.centroid_force) < 3:
                return "centroid_force 数据格式错误或不足。"
            # print(f"Inputs to read_chain.predict: question={inputs[self.input_key]}, etot={self.etot}, centroid_force_0={self.centroid_force[0]}, centroid_force_1={self.centroid_force[1]}, centroid_force_2={self.centroid_force[2]}, atomic_force={self.atomic_force}")
            final_output = self.read_chain.predict(
                question=inputs[self.input_key],
                etot=self.etot,  
                centroid_force_0=self.centroid_force[0],
                centroid_force_1=self.centroid_force[1],
                centroid_force_2=self.centroid_force[2],
                atomic_force=self.atomic_force
            )
            print(final_output)
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
            model_path_1 = f"{model_dir}/model.ckpt-9000.pt"
            # model_path_2 = f"{model_dir}/model.ckpt-8000.pt"
            model_devi = data_relaticity(cor, box, atype, [model_path])
            # print(ei_l)
            # print(ei_h)
            # print(model_devi[0][4])
            if model_devi[0][4] < ei_l:
                # 走预训练模型
                
                final_output = self.PT_predictor(output['Property'], model_path, cor, box, atype)
            elif model_devi[0][4] < ei_h:
                # 走第一性原理软件
                self.FP_predictor(output['Materials'][0])
                file_path = '/home/shuai-2204/code/AgentCode/ChemAgent_test/ChemAgent/tools/predictor/statfile.0'
                # 检查文件是否存在
                if not os.path.isfile(file_path):
                    return f"文件不存在: {file_path}"

                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    return "statfile.0 文件为空。"
                
                # 提取所需的数据
                from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_atomic_force
                from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_last_centroid_force
                from ChemAgent2pl.ChatMat.tools.predictor.read_agent_output import extract_last_iteration_energy
                self.etot = extract_last_iteration_energy(file_path)
                self.centroid_force = extract_last_centroid_force(file_path)
                self.atomic_force = extract_atomic_force(file_path)
                
                # print(self.etot)
                # print(self.centroid_force)
                # print(self.atomic_force)
                # 检查 centroid_force 是否为包含三个元素的列表
                if not isinstance(self.centroid_force, (list, tuple)) or len(self.centroid_force) < 3:
                    return "centroid_force 数据格式错误或不足。"
                # print(f"Inputs to read_chain.predict: question={inputs[self.input_key]}, etot={self.etot}, centroid_force_0={self.centroid_force[0]}, centroid_force_1={self.centroid_force[1]}, centroid_force_2={self.centroid_force[2]}, atomic_force={self.atomic_force}")
                final_output = self.read_chain.predict(
                    question=inputs[self.input_key],
                    etot=self.etot,  
                    centroid_force_0=self.centroid_force[0],
                    centroid_force_1=self.centroid_force[1],
                    centroid_force_2=self.centroid_force[2],
                    atomic_force=self.atomic_force
                )
                print(final_output)
            else:
                final_output = '不适合计算'
                print('不适合计算')

        # 使用 final_single_chain 生成最终回答
        formatted_output = self.final_single_chain.predict(
            question=inputs[self.input_key],
            final_output=final_output
        )
        print(formatted_output)
        return {self.output_key: formatted_output}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        prompt: str = PROMPT,
        read_prompt: str = READ_PROPMT,
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
            input_variables=['question'],
            partial_variables={
                'etot': '',
                'centroid_force_0': '',
                'centroid_force_1': '',
                'centroid_force_2': '',
                'atomic_force': '',
            }
        )

        fs_template = PromptTemplate(
            template=final_single_prompt,
            input_variables=['question', 'final_output']
        )

        llm_chain = LLMChain(llm=llm, prompt=template)
        read_chain = LLMChain(llm=llm, prompt=rd_template)
        final_single_chain = LLMChain(llm=llm, prompt=fs_template)

        return cls(
            llm=llm,
            llm_chain=llm_chain, 
            read_chain=read_chain,
            final_single_chain=final_single_chain,
            **kwargs
        )
