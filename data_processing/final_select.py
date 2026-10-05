import pandas as pd

folder = '/Users/krinashah/personal/study/college/DAV'

df_a = pd.read_csv(f'{folder}/base_a_2023_2024.csv', low_memory=False)
df_b = pd.read_csv(f'{folder}/base_b_2023_2024.csv', low_memory=False, encoding='latin1')

keep_rename_a = {
    'FilingID': 'FilingID',
    'DateSubmitted': 'DateSubmitted',
    '1A': 'LegalName',
    '1B1': 'BusinessName_Primary',
    '1E1': 'CRD_Number',
    '1F1-City': 'Office_City',
    '1F1-State': 'Office_State',
    '1F1-Country': 'Office_Country',
    '1F1-Postal': 'Office_Postal',
    '1I': 'HasWebsite_Flag',
    '5A': 'NumEmployees',
    '5B1': 'NumEmployees_Advisory',
    '5F1': 'HasRegulatoryAUM_Flag',
    '5F2a': 'Discretionary_AUM',
    '5F2b': 'NonDiscretionary_AUM',
    '5F2c': 'Total_AUM_USD',
    '5F3': 'Total_NumAccounts',
    '5G1': 'Service_FinancialPlanning',
    '5G2': 'Service_PortfolioMgmt_Individuals',
    '5G3': 'Service_PortfolioMgmt_InvestmentCompanies',
    '5G4': 'Service_PortfolioMgmt_PooledVehicles',
    '5G5': 'Service_PortfolioMgmt_Businesses',
    '5G6': 'Service_PensionConsulting',
    '5G7': 'Service_SelectionOfOtherAdvisers',
    '5G8': 'Service_Publications',
    '5G9': 'Service_SecurityRatings',
    '5G10': 'Service_MarketTiming',
    '5G11': 'Service_EducationalSeminars',
    '5G12': 'Service_Other',
    '5E1': 'Fee_PercentAUM',
    '5E2': 'Fee_Hourly',
    '5E3': 'Fee_FixedFee',
    '5E4': 'Fee_Commission',
    '5E5': 'Fee_PerformanceBased',
    '5E7': 'Fee_Other',
    '5H': 'NumClients_Bucket',
    '9A1a': 'Custody_ClientFunds_Flag',
    '9A1b': 'Custody_ClientSecurities_Flag',
    '11': 'HasDisclosure_Overall_Flag',
    '11A1': 'Disclosure_CriminalFelony_Firm',
    '11A2': 'Disclosure_CriminalFelony_Affiliate',
    '11B1': 'Disclosure_CriminalMisdemeanor_Firm',
    '11B2': 'Disclosure_CriminalMisdemeanor_Affiliate',
    '11C1': 'Disclosure_RegulatoryAction1',
    '11C2': 'Disclosure_RegulatoryAction2',
    '11D1': 'Disclosure_SROAction1',
    '11E1': 'Disclosure_CivilJudicial1',
    '11F': 'Disclosure_Bankruptcy_Flag',
    '11G': 'Disclosure_Bond_Flag',
}
cols_present_a = [c for c in keep_rename_a if c in df_a.columns]
missing_a = [c for c in keep_rename_a if c not in df_a.columns]
df_a_trimmed = df_a[cols_present_a].rename(columns=keep_rename_a)

keep_rename_b = {
    'FilingID': 'FilingID',
    '3A': 'OrgForm',
    '3C-State': 'StateOfOrg',
    '3C-Country': 'CountryOfOrg',
}
cols_present_b = [c for c in keep_rename_b if c in df_b.columns]
df_b_trimmed = df_b[cols_present_b].rename(columns=keep_rename_b)

df_final = df_a_trimmed.merge(df_b_trimmed, on='FilingID', how='left')

print("Final shape:", df_final.shape)
print("Columns:", df_final.columns.tolist())
print("Missing from source (check these):", missing_a)

df_final.to_csv(f'{folder}/adv_final_trimmed.csv', index=False)
print("Saved.")
