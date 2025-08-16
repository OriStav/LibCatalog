#%%
import pandas as pd

file_id = "1sEnOeXcBb0JEYQBPMMKs587mkERo9b6Q"
loans_log_link = f"https://drive.google.com/uc?export=download&id={file_id}"

df = pd.read_csv(loans_log_link)
print(df.head())
df["available"] = ~df['book_id'].isin(df[df['return_date'].isna()]['book_id'].unique())