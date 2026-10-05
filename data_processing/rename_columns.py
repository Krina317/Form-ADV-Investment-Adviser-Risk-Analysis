import pandas as pd

# --- Load the filtered files (small now, fast to work with) ---
df_a = pd.read_csv('/Users/krinashah/personal/study/college/DAV/base_a_2023_2024.csv', low_memory=False)
df_b = pd.read_csv('/Users/krinashah/personal/study/college/DAV/base_b_2023_2024.csv', low_memory=False, encoding='latin1')

# --- Rename map for Base_A (confirmed + best-guess, we'll verify uncertain ones together) ---
rename_map_a = {
    'FilingID': 'FilingID',
    'DateSubmitted': 'DateSubmitted',
    '1A': 'LegalName',
    '1B1': 'BusinessName_Primary',
    '1B2': 'BusinessName_Other',
    '1C-Legal': 'PriorLegalName',
    '1C-Business': 'PriorBusinessName',
    '1D': 'SEC_File_Number',
    '1E1': 'CRD_Number',
    '1F1-Street 1': 'Office_Street1',
    '1F1-Street 2': 'Office_Street2',
    '1F1-City': 'Office_City',
    '1F1-State': 'Office_State',
    '1F1-Country': 'Office_Country',
    '1F1-Postal': 'Office_Postal',
    '1I': 'HasWebsite_Flag',
    '4A': 'Succession_Flag',
    '4B': 'Succession_Date',
    '5A': 'NumEmployees',
    '5B1': 'NumEmployees_AdvisoryFunctions',
    '5B2': 'NumEmployees_RegisteredReps',
    '5B3': 'NumEmployees_InsuranceLicensed',
    '5F2c': 'Total_AUM_USD',
    '5F2d': 'Discretionary_NumAccounts',
    '5F2e': 'NonDiscretionary_NumAccounts',
    '5F2f': 'Total_NumAccounts',
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
    '11': 'HasDisclosure_Overall_Flag',
    '11A1': 'Disclosure_CriminalFelony_Firm',
    '11A2': 'Disclosure_CriminalFelony_Affiliate',
    '11B1': 'Disclosure_CriminalMisdemeanor_Firm',
    '11B2': 'Disclosure_CriminalMisdemeanor_Affiliate',
    '11C1': 'Disclosure_RegulatoryAction1_Firm',
    '11C2': 'Disclosure_RegulatoryAction2_Firm',
    '11D1': 'Disclosure_SRO_Action1',
    '11E1': 'Disclosure_CivilJudicial1',
}

df_a_renamed = df_a.rename(columns=rename_map_a)

# --- Rename map for Base_B ---
rename_map_b = {
    'FilingID': 'FilingID',
    '3A': 'OrgForm',
    '3A-Other': 'OrgForm_Other',
    '3B': 'MonthOfFiscalYearEnd',
    '3C': 'StateOfOrg',
    '3C-State': 'StateOfOrg_State',
    '3C-Country': 'StateOfOrg_Country',
}

df_b_renamed = df_b.rename(columns=rename_map_b)

print("Base_A columns after rename:", df_a_renamed.columns.tolist())
print("\nBase_B columns after rename:", df_b_renamed.columns.tolist())

df_a_renamed.to_csv('/Users/krinashah/personal/study/college/DAV/base_a_renamed.csv', index=False)
df_b_renamed.to_csv('/Users/krinashah/personal/study/college/DAV/base_b_renamed.csv', index=False)

print("\nSaved renamed files.")
