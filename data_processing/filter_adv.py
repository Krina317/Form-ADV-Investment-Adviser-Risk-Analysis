import pandas as pd

folder = '/Users/krinashah/personal/study/college/DAV/dataset/adv-filing-data-20111105-20241231-part1'

df_a = pd.read_csv(f'{folder}/IA_ADV_Base_A_20111105_20241231.csv', low_memory=False)
df_a['DateSubmitted'] = pd.to_datetime(df_a['DateSubmitted'], errors='coerce', format='mixed')
df_a_filtered = df_a[df_a['DateSubmitted'].dt.year.isin([2023, 2024])]

print("Base_A filtered shape:", df_a_filtered.shape)

output_a = '/Users/krinashah/personal/study/college/DAV/base_a_2023_2024.csv'
df_a_filtered.to_csv(output_a, index=False)
print("Saved:", output_a)

df_b = pd.read_csv(f'{folder}/IA_ADV_Base_B_20111105_20241231.csv', low_memory=False, encoding='latin1')
df_b_filtered = df_b[df_b['FilingID'].isin(df_a_filtered['FilingID'])]

print("Base_B filtered shape:", df_b_filtered.shape)

output_b = '/Users/krinashah/personal/study/college/DAV/base_b_2023_2024.csv'
df_b_filtered.to_csv(output_b, index=False)
print("Saved:", output_b)
