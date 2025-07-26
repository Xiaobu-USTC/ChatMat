import pandas as pd

# CSV 转 XLSX
df = pd.read_excel('data.xlsx')
# df.to_excel('data.xlsx', index=False)
sio2_data = df[df['Name'] == 'SiO2']
print(sio2_data[['Force for centroid (y) [a.u.]']].to_markdown())
# print(df.columns.tolist())  # 确认列名
# print(df.head(1))           # 看看数据内容结构