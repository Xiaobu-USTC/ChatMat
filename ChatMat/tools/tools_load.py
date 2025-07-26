import warnings
from typing import Dict, Callable, List
from pydantic import ValidationError
from langchain.base_language import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_community.agent_toolkits.load_tools import load_tools, get_all_tool_names
from ChatMat.tools.search_csv import _get_search_csv
from ChatMat.tools.predictor import _get_predict_properties
_ChemAgent_TOOLS: Dict[str, Callable[[BaseLanguageModel, bool], BaseTool]] = {
    # "Search_csv": _get_search_csv,
    # Add other tools here
    "Predictor": _get_predict_properties,
    # "fp_predictor": _get_fp_predictor,
    # "pt_predictor": _get_pt_predictor,
    # "python_repl": _get_python_repl,
}

_load_internet_tool_names: list[str] = [
    'google-search',
    'google-search-results-json',
    'wikipedia',
]

def load_chemagent_tools(
        llm: BaseLanguageModel, 
        verbose: bool=False,
        search_internet: bool=False,    
    ) -> List[BaseTool]:
    # Initialize custom tools with verbose
    custom_tools = [model(llm=llm, verbose=verbose) for model in _ChemAgent_TOOLS.values()]

    if search_internet:
        try:
            internet_tools = load_tools(_load_internet_tool_names, llm=llm)
            custom_tools += internet_tools
        except Exception as e:
            warnings.warn(f'The internet tool does not work - {str(e)}')
    
    return custom_tools
