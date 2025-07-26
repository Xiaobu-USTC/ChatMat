import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ["CUDA_VISIBLE_DEVICES"]='0'
import pandas as pd
import json
import copy
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from ChatMat.models_load import ModelsLoad
from ChatMat.config import config as config_default
from ChatMat.agent.chem_agent import ChemAgent

# Initialize ChemAgent
config = copy.deepcopy(config_default)
search_internet = config['search_internet']
verbose = config['verbose']

llm = ModelsLoad(model='gpt-4o', temperature=0.2).get_llm()
chemagent = ChemAgent.from_llm(
    llm=llm, 
    verbose=verbose, 
    search_internet=search_internet,
)

# Define task
task = (
    "Generate the material structure of (H2O)64."
    "Give me the charge density distribution of (HClO4)16."
    "Please train the MLPES Construction of Al176Si24."
)

def main(model='gpt-4o', temperature=0.0) -> str:
    config = copy.deepcopy(config_default)

    search_internet = config['search_internet']
    verbose = config['verbose']
    # Load the language model
    llm = ModelsLoad(model='gpt-4o', temperature=0.2).get_llm()

    # Initialize CallbackManager with StdOutCallbackHandler
    callback_manager = CallbackManager([StdOutCallbackHandler()])

    # Initialize ChemAgent
    chemagent = ChemAgent.from_llm(
        llm=llm, 
        verbose=verbose, 
        search_internet=search_internet,
    )
    
    print ('#' * 50 + "\n")
    print ('Welcome to ChemAgent!')
    print("\n" + "#"*30 + ' Question ' + "#"*30)
    print ('Please enter the question below >>')
    # question = input()
    abc_index = True
    if abc_index:
        question = "What is the totle energy of Ga2O3?"
        try:
            output = chemagent.invoke({"input": question}, callbacks=callback_manager)
        except ValueError as ve:
            print(f"Input validation error: {ve}")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        print ('\n')
        print ("#"*10 + ' Output ' + "#" * 30)
        print (output['output'])
        print ('\n')
        print ('Thanks for using ChemAgent!')
    else:
        file_path = '/home/shuai-2204/code/AgentCode/ChemAgent2pl/experiment_results.jsonl' 
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue  # 跳过注释行或空行
                data = json.loads(line)
                question = data["input"]
        
                try:
                    output = chemagent.invoke({"input": question}, callbacks=callback_manager)
                except ValueError as ve:
                    print(f"Input validation error: {ve}")
                    return
                except Exception as e:
                    print(f"An error occurred: {e}")
                    return

                print ('\n')
                print ("#"*10 + ' Output ' + "#" * 30)
                print (output['output'])
                print ('\n')
                print ('Thanks for using ChemAgent!')
                output_path = "/home/shuai-2204/code/AgentCode/ChemAgent2pl/experiment_results_0605.jsonl"
                with open(output_path, "a", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(output['output'], ensure_ascii=False) + "\n")
                # return output

if __name__ == '__main__':
    main()
