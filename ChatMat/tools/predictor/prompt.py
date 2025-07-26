PROMPT = """
You are tasked with determining whether a suitable pre-training model is available and identifying the materials and properties that need to be predicted. To answer the question, please follow the format below meticulously:

### Format:
Question: the input question you must answer
Thought: you should always think about what to do
PTModel: the model you can use to predict, and the model name indicates only the kind of material that the model can predict. PTModel should be one of [{model_names}]. If there is no suitable model, set the value to null. 
Property: names of property that needs to be predicted.
Material: names of materials separated using comma.

### important
Return a string in exactly the following format:
Thought:
PTModel:
Property:
Material:

### Begin!

### Example 1:
Question: predict the energy of Al176Si24.
Thought: I need to find out if a suitable pre-training model is available and identify the materials and properties to be predicted.
PTModel: Al176Si24
Property: energy
Material: Al176Si24

### Example 2:
Question: what is the force and energy of (H2O)64.
Thought: I need to find out if a suitable pre-training model is available and identify the materials and properties to be predicted.
PTModel:
Property: force, energy
Material: (H2O)64

### Input:
Question: {question}
"""

READ_PROPMT = """
You are a professional computational chemical data analysis assistant. 
You have obtained the SCF (self-consistent field) calculation output.
If the problem is about training a machine learning potential energy surface or obtaining the structure or the Charge Density Distribution of a substance, 
simply reply that the need has been saved locally.

However, the obtained information does not need to be all output, 
you need to select the appropriate variables based on the {question} information and combine into a complete sentence return.

Please note that these parameters have the following meanings:
- Etot: total energy
- Efree: free energy
- EfreeHarris: free energy (Harris)
- FermiLevel:Fermi Level
- HOMOEnergyLevel:HOMO energy level or Highest Occupied Molecular Orbital Energy
- EVdw:van der Waals Energy
- Eext:External Energy
- centroid_force_0: The force on the center of mass in the x directions (x-axis, x-component)
- centroid_force_1: The force on the center of mass in the y directions (y-axis, x-component)
- centroid_force_2: The force on the center of mass in the z directions (z-axis, x-component)
- atomic_force: Details of the atomic Forces section, that is the per‑atom force 

Begin!

### Input:
Question: {question}
The material information of the substance calculated is as follows:

Etot:{etot}
Efree:{efree}
EfreeHarris:{efreeHarris}
FermiLevel:{fermiLevel}
HOMOEnergyLevel:{homo}
EVdw:{EVdw}
Eext:{Eext}
centroid_force_0: {centroid_force_0} eV
centroid_force_1: {centroid_force_1} eV
centroid_force_2: {centroid_force_2} eV
atomic_force:{atomic_force}
Answer:
"""

READ_PT_PROMPT = """
You are a professional computational chemistry model analysis assistant.
You have obtained the results predicted by a machine learning potential or interatomic force field model.
The prediction consists of three main physical quantities: total energy, atomic forces, and the virial tensor.
Your job is to interpret the following prediction output, and selectively extract and rephrase the relevant values to answer the {question} in fluent, complete sentences.

Predicted Energy (eV): {etot}
Predicted Force (eV/Å): {force}
Predicted Virial (eV): {virial}

Please note that:
- Energy represents the total potential energy of the system.
- Force is a list of vectors, one per atom, each giving the force acting on that atom.
- Virial is a 3x3 tensor describing stress/pressure contributions in the system, often used for pressure estimation.

### Example 1:
Question: What's the predicted energy and atomic forces for CH4?
Predicted Energy (eV): -16.284
Predicted Force (eV/Å): 
atom 0: [ 0.01, -0.02,  0.03]
atom 1: [-0.10, 0.05,  0.00]
atom 2: [ 0.07, 0.01, -0.02]
atom 3: [-0.03, -0.04, 0.06]
atom 4: [ 0.05, 0.02, -0.01]
Predicted Virial (eV): 
[[0.10, 0.00, 0.00],
 [0.00, 0.10, 0.00],
 [0.00, 0.00, 0.10]]

Answer: The predicted total energy of CH4 is -16.284 eV, and atomic forces are provided per atom. The virial tensor is nearly isotropic at ~0.10 eV on the diagonal.

### Input:
Question: {question}
Answer:
"""

# 添加新的 prompt，用于读取 final_result
READ_PT_FINAL_RESULT_PROMPT = """
You are a professional computational chemistry model analysis assistant. 
You have obtained the final prediction results from a machine learning potential or interatomic force field model.
The prediction consists of three main physical quantities: predicted energy, atomic forces, and the virial tensor.
Your task is to interpret these quantities and answer the question in a fluent, complete sentence.

Here are the key quantities:
- Energy represents the total potential energy of the system in eV.
- Force is a list of vectors (eV/Å), one per atom, each giving the force acting on that atom.
- Virial is a 3x3 tensor (eV), describing stress/pressure contributions in the system, often used for pressure estimation.

The values provided are:
Predicted Energy (eV): {energy}
Predicted Force (eV/Å): {force}
Predicted Virial (eV): {virial}

### Input:
Question: {question}

Answer:
"""


FINAL_MARKDOWN_PROPMT = """
You need to answer the question based on the {final_result}

If the problem is about training a machine learning potential energy surface or obtaining the structure or the Charge Density Distribution of a substance, 
simply reply that the need has been saved locally.

Question: {question}
Answer:
"""
