import pandas as pd

def compare_csvs(file1, file2, id_column, output_excel):
    # Load the two CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Ensure that both dataframes have the id_column
    if id_column not in df1.columns or id_column not in df2.columns:
        raise ValueError(f"Both files must contain the '{id_column}' column.")

    # Set the index of both dataframes to the ID column for easier comparison
    df1.set_index(id_column, inplace=True)
    df2.set_index(id_column, inplace=True)

    # Ensure both dataframes have the same structure
    common_columns = df1.columns.intersection(df2.columns)
    
    # Create a writer object for Excel output
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Iterate over the columns, excluding the ID column
        for column in common_columns:
            # Compare the two dataframes for the current column
            diff_mask = df1[column] != df2[column]
            diffs = pd.DataFrame({
                'ID': df1.index[diff_mask],  # myID column
                f'{column}_file1': df1[column][diff_mask],
                f'{column}_file2': df2[column][diff_mask]
            }).set_index('ID')

            # Write to an Excel sheet if there are differences
            if not diffs.empty:
                diffs.to_excel(writer, sheet_name=column)

    print(f"Comparison complete! Differences saved to {output_excel}")
