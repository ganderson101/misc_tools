import pandas as pd

def compare_csvs(file1, file2, id_column1, id_column2, output_excel):
    # Load the two CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Ensure that both dataframes have the ID columns
    if id_column1 not in df1.columns or id_column2 not in df2.columns:
        raise ValueError(f"File1 must contain '{id_column1}' and File2 must contain '{id_column2}'.")

    # Merge the dataframes on the two different ID columns (myID1 and myID2)
    merged_df = pd.merge(df1, df2, left_on=id_column1, right_on=id_column2, suffixes=('_file1', '_file2'))
    
    # Create a writer object for Excel output
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Iterate over the columns present in both files, excluding the ID columns
        for column in df1.columns:
            if column != id_column1 and column in df2.columns:
                # Compare the two dataframes for the current column
                col_file1 = f'{column}_file1'
                col_file2 = f'{column}_file2'
                
                # Extract the columns for comparison
                diff_mask = merged_df[col_file1] != merged_df[col_file2]
                diffs = pd.DataFrame({
                    id_column1: merged_df[id_column1][diff_mask],  # myID1
                    id_column2: merged_df[id_column2][diff_mask],  # myID2
                    f'{column}_file1': merged_df[col_file1][diff_mask],
                    f'{column}_file2': merged_df[col_file2][diff_mask]
                })

                # Write to an Excel sheet if there are differences
                if not diffs.empty:
                    diffs.to_excel(writer, sheet_name=column, index=False)

    print(f"Comparison complete! Differences saved to {output_excel}")

# Example usage
# compare_csvs('file1.csv', 'file2.csv', 'myID1', 'myID2', 'comparison_output.xlsx')
