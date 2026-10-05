import pandas as pd

folder_source = '/Users/krinashah/personal/study/college/DAV/dataset/adv-filing-data-20111105-20241231-part1'
folder_out = '/Users/krinashah/personal/study/college/DAV'

df = pd.read_csv(f'{folder_source}/IA_DRP_Regulatory_20210101_20241231.csv', low_memory=False, encoding='latin1')

keep_rename = {
    'FilingID': 'FilingID',
    'ReferenceID': 'EventID',
    'Initiator Type': 'Initiator_Type',
    'Initiated By': 'Initiated_By',
    'Principal Sanction': 'Principal_Sanction',
    'Other Sanctions': 'Other_Sanctions',
    'Date Initiated': 'DateInitiated',
    'Case Number': 'CaseNumber',
    'Allegations': 'Allegations',
    'Status': 'Status',
    'Resolution': 'Resolution',
    'Resolution Date': 'ResolutionDate',
    'Monetary Sanction': 'HasMonetarySanction_Flag',
    'Monetary Amount': 'MonetaryAmount',
    'Revocation/Expulsion/Denial': 'Sanction_Revocation',
    'Censure': 'Sanction_Censure',
    'Bar': 'Sanction_Bar',
    'Disgorgement/Restitution': 'Sanction_Disgorgement',
    'Cease and Desist/Injunction': 'Sanction_CeaseDesist',
    'Suspension': 'Sanction_Suspension',
    'Summary': 'Summary',
}

cols_present = [c for c in keep_rename if c in df.columns]
missing = [c for c in keep_rename if c not in df.columns]
df_trimmed = df[cols_present].rename(columns=keep_rename)

# filter to 2023-2024 using DateInitiated
df_trimmed['DateInitiated'] = pd.to_datetime(df_trimmed['DateInitiated'], errors='coerce', format='mixed')
df_filtered = df_trimmed[df_trimmed['DateInitiated'].dt.year.isin([2023, 2024])]

print("Full trimmed shape:", df_trimmed.shape)
print("Filtered (2023-2024) shape:", df_filtered.shape)
print("Missing columns:", missing)

output_path = f'{folder_out}/drp_regulatory_2023_2024.csv'
df_filtered.to_csv(output_path, index=False)
print("Saved:", output_path)
