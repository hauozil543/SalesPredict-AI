import pandas as pd
sales_train    = pd.read_csv('C:/Users/Ho Hau/Downloads/M5/data/raw/sales_train_validation.csv')

household_2_074 = sales_train[(sales_train['item_id'] == 'HOUSEHOLD_2_074') & (sales_train['store_id'] == 'CA_1')]
day_columns = [col for col in sales_train.columns if col.startswith('d_')]
print(household_2_074[day_columns])


