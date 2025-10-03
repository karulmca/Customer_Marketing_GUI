import pandas as pd

# Read Test5.xlsx
df = pd.read_excel('Test5.xlsx')
print("Data in Test5.xlsx:")
print("=" * 50)
print("Columns:", list(df.columns))
print("=" * 50)

for i, row in df.iterrows():
    print(f"{i+1}. Company: {row['Company Name']}")
    print(f"   Website: {row['Website']}")
    if 'LinkedIn_URL' in df.columns:
        print(f"   LinkedIn: {row['LinkedIn_URL']}")
    print(f"   Current Revenue: {row['Revenue']}")
    print("-" * 30)