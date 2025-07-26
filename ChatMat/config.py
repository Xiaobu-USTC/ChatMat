import os
from ChatMat import __root_dir__


config = {
    # ChatMOF
    'search_internet': False,
    'verbose': True,
    'handle_errors': True,

    # LLM - openAI
    'temperature': 0.0,    
    'model': 'gpt-40',

    # data directory
    'model_dir': os.path.join(__root_dir__, 'database/load_model/'),


    # fp predictor
    'fp_predictor': os.path.join(__root_dir__, 'tools/predictor'),
    # table searcher
    'data_dir': os.path.join(__root_dir__, 'database/load_data/data.xlsx'),
    'max_iteration': 3,
    'token_limit': False,

    # predictor
    'max_length_in_predictor' : 30,
    'accelerator' : 'cuda',
}
