import pandas as pd

reference_path = 'data/Reference_Froggy_Spreadsheet.xlsx'
analysis_path = 'results/froggy_analysis_results.xlsx'
cross_verification_path = 'results/cross_verification_results.xlsx'

columns_to_check = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '13', '14', '15', '16']

df_reference = pd.read_excel(reference_path, dtype=str)
df_analysis = pd.read_excel(analysis_path, dtype=str)
df_cross = pd.read_excel(cross_verification_path, dtype=str)

df_reference.set_index('Name', inplace=True)
df_analysis.set_index('Name', inplace=True)

def compare_values(name, col):
    val_ref = df_reference.at[name, int(col)] if name in df_reference.index and int(col) in df_reference.columns else "-" # stores it as nums not str
    val_analysis = df_analysis.at[name, col] if name in df_analysis.index and col in df_analysis.columns else "-"

    val_ref = val_ref.strip() if isinstance(val_ref, str) else "-"
    val_analysis = val_analysis.strip() if isinstance(val_analysis, str) else "-"

    if val_ref == "-" or val_ref == "" or val_analysis == "-" or val_analysis == "":
        print("BREH")
        return "-"
    elif val_ref == val_analysis:
        return val_ref
    else:
        return "invalid"

for col in columns_to_check:
    df_cross[col] = df_cross['Name'].apply(lambda name: compare_values(name, col))

df_cross.to_excel(cross_verification_path, index=False)
