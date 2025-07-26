from typing import Any
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from ChatMat.config import config
from ChatMat.tools.search_csv.base import TableSearcher


def _get_search_csv(
        llm: BaseLanguageModel,
        file_path: str = config['data_dir'],
        verbose: bool = False,
        **kwargs: Any) -> Tool:
    
    # 初始化 TableSearcher
    table_searcher = TableSearcher.from_filepath(
        llm=llm, 
        file_path=file_path, 
        verbose=verbose
    )
    
    # 定义工具函数
    def search_csv(question: str) -> str:
        try:
            result = table_searcher.invoke({
                'question': question,  # 已更改为 'input'
                'information': "Include units in the output."
            })
            print(f"************{result}")
            # 确保返回的是字符串
            if isinstance(result, dict):
                return result.get('answer', 'No answer returned.')
            elif isinstance(result, str):
                return result
            else:
                return 'Unexpected response format.'
        except Exception as e:
            # print(f"************{e}")
            # return f"An error occurred during CSV search: {e}"
            return e
    
    return Tool(
        name="Search_csv",
        description=(
                "A tool that extracts accurate properties from a look-up table in the database. "
                "The input must be a detailed full sentence to answer the question."
        ),
        func=search_csv
    )
