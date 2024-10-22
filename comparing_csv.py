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
