DF_PROMPT = """You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
You should make a valid python command as input. You must use print the output using the `print` function at the end.
You should use the `to_markdown` function when you print a pandas object.

Use the following strict format without deviations:

Question: the input question you must answer
Thought: you should always think about what to do
Input: the valid python code only using the Pandas library
Observation: the result of python code
... (this Thought/Input/Observation can repeat N times)
Final Thought: you should think about how to answer the question based on your observation
Final Answer: the final answer to the original input question. If you can't answer the question, say `nothing`

The index of the dataframe must be one of {df_index}. You can determine which index to use based on the problem. 
Please note that the following terms have the following meanings:
- Etot: total energy
- Efree: free energy
- EfreeHarris: free energy (Harris)
- FermiLevel:Fermi Level
- HOMOEnergyLevel:HOMO energy level or Highest Occupied Molecular Orbital Energy
- EVdw:van der Waals Energy
- Eext:External Energy
- Fx, Fy, Fz: The force on the center of mass in the x, y, and z directions
- Atomic Force: Details of the atomic Forces section
If it's not in the index you want, skip straight to Final Thought.
{information}

Begin!

Question: What is the head of df? If you extracted successfully, derive 'success' as the final answer
Thought: To get the head of a DataFrame, we can use the pandas function head(), which will return the first N rows. By default, it returns the first 5 rows.
Input: 
```python
import pandas as pd
import json
print(df.head().to_markdown())
Observation: {df_head} 
Final Thought: The head() function in pandas provides the first 5 rows of the DataFrame. 
Final Answer: success

Question: {input} 
Thought:{agent_scratchpad}
"""