import pandas as pd

def compare_csvs(file1, file2, id_column1, id_column2, output_excel):
    # Load the two CSV files, forcing all columns to be strings
    df1 = pd.read_csv(file1, dtype=str)
    df2 = pd.read_csv(file2, dtype=str)

    # Ensure that both dataframes have the ID columns
    if id_column1 not in df1.columns:
        raise KeyError(f"File1 must contain the ID column: '{id_column1}'")
    if id_column2 not in df2.columns:
        raise KeyError(f"File2 must contain the ID column: '{id_column2}'")

    # Handle NaN values in ID columns (but we will not create separate tabs for these)
    df1 = df1.dropna(subset=[id_column1])
    df2 = df2.dropna(subset=[id_column2])

    # Merge the dataframes on the two different ID columns (myID1 and myID2)
    merged_df = pd.merge(df1, df2, left_on=id_column1, right_on=id_column2, suffixes=('_file1', '_file2'))

    # Create a writer object for Excel output
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Create a dummy sheet to avoid "no visible sheets" error
        pd.DataFrame({'Message': ['Temporary sheet - will be removed if data is written.']}).to_excel(writer, sheet_name='Temp_Sheet')

        sheets_written = False  # Flag to ensure we write at least one real sheet

        # Add a "Matched Data" tab if merged_df is not empty
        if not merged_df.empty:
            # Write all the columns (ID columns + other columns from both files) to a "Matched Data" sheet
            merged_columns = merged_df[[id_column1, id_column2] + 
                                       [f'{col}_file1' for col in df1.columns if col != id_column1] +
                                       [f'{col}_file2' for col in df2.columns if col != id_column2]]
            merged_columns.to_excel(writer, sheet_name='Matched_Data', index=False)
            sheets_written = True

        # Iterate over the columns present in both files, excluding the ID columns
        for column in df1.columns:
            # Ensure we do not compare the ID columns (id_column1 or id_column2)
            if column != id_column1 and column in df2.columns and column != id_column2:
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

        # Remove the dummy sheet if any real data was written
        if sheets_written:
            workbook = writer.book
            if 'Temp_Sheet' in workbook.sheetnames:
                del workbook['Temp_Sheet']

        # If no sheets were written, keep the dummy sheet with a more appropriate message
        if not sheets_written:
            pd.DataFrame({'Message': ['No data to compare or no differences found.']}).to_excel(writer, sheet_name='No_Differences', index=False)

    print(f"Comparison complete! Differences saved to {output_excel}")

# Example usage
# compare_csvs('file1.csv', 'file2.csv', 'myID1', 'myID2', 'comparison_output.xlsx')
