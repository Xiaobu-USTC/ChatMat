import os

__version__ = '0.1.0'   
__root_dir__ = os.path.dirname(__file__)


from langchain_community.chat_models import ChatOpenAI
# from langchain.chat_models import ChatOpenAI
from ChatMat.agent.chem_agent import ChemAgent
from ChatMat.config import config
from ChatMat import models_load


__all__ = [
    "ChemAgent",
    "config",
    "ChatOpenAI",
    "__version__",
    'models_load',
]
