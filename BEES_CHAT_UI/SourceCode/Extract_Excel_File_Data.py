import pandas as pd
import io

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content}', metadata={self.metadata})"


# Load data from Excel file
def load_data_from_excel(file_path):
    if '.csv' in file_path:
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path,sheet_name=None)
    return df


# Convert each row into a single text string by concatenating all columns
def concatenate_row_with_columns(row, columns):
    return ' '.join(f'{col}: {row[col]}' for col in columns)


def get_excel_data(file_path):
    data_frame = load_data_from_excel(file_path)
    # data_frame['text_representation'] = data_frame.apply(lambda row: ' | '.join(row.values.astype(str)), axis=1)
    # row = data_frame.iloc[2]
    #
    # # Convert the row to a DataFrame
    # row_df = pd.DataFrame([row])
    # # Alternatively, you can focus on specific columns
    # # data_frame['text_representation'] = data_frame[['column1', 'column2']].apply(lambda row: ' | '.join(row.values.astype(str)), axis=1)
    # combined_text = row_df.to_csv(index=True)
    # # formatted_text_data = data_frame.apply(lambda row: concatenate_row_with_columns(row, columns), axis=1)
    # # combined_text = ' '.join(formatted_text_data)
    # # combined_text = ' '.join(data_frame.astype(str).values.flatten())
    # print(combined_text)
    # data_frame.to_excel(r"C:\Users\BRADSOL123\Downloads\Output_BMGFGrants (3).xlsx")
    return data_frame

