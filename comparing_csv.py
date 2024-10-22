import pandas as pd

def compare_csvs(file1, file2, id_column1, id_column2, output_excel):
    # Load the two CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Ensure that both dataframes have the ID columns
    if id_column1 not in df1.columns or id_column2 not in df2.columns:
        raise ValueError(f"File1 must contain '{id_column1}' and File2 must contain '{id_column2}'.")

    # Handle NaN values in ID columns
    df1_with_nan = df1[df1[id_column1].isna()]
    df2_with_nan = df2[df2[id_column2].isna()]
    
    df1 = df1.dropna(subset=[id_column1])
    df2 = df2.dropna(subset=[id_column2])

    # Merge the dataframes on the two different ID columns (myID1 and myID2)
    merged_df = pd.merge(df1, df2, left_on=id_column1, right_on=id_column2, suffixes=('_file1', '_file2'))

    # Create a writer object for Excel output
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        sheets_written = False  # Flag to ensure we write at least one sheet

        # Add a "Matched Data" tab if merged_df is not empty
        if not merged_df.empty:
            merged_columns = merged_df[[id_column1, id_column2] + 
                                       [f'{col}_file1' for col in df1.columns if col != id_column1] +
                                       [f'{col}_file2' for col in df2.columns if col != id_column2]]
            merged_columns.to_excel(writer, sheet_name='Matched_Data', index=False)
            sheets_written = True

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
                    sheets_written = True
        
        # Write rows with NaN in the ID columns to separate tabs if they exist
        if not df1_with_nan.empty:
            df1_with_nan.to_excel(writer, sheet_name=f'{id_column1}_NaN', index=False)
            sheets_written = True
        if not df2_with_nan.empty:
            df2_with_nan.to_excel(writer, sheet_name=f'{id_column2}_NaN', index=False)
            sheets_written = True

        # If no sheets were written, create a default empty sheet with a message
        if not sheets_written:
            pd.DataFrame({'Message': ['No data to compare or no differences found.']}).to_excel(writer, sheet_name='No_Differences', index=False)

    print(f"Comparison complete! Differences saved to {output_excel}")
