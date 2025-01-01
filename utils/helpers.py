from decimal import Decimal

# PostgreSQL handles Decimal type, to avoid problems when serializing to JSON, it is converted to float
def convert_decimal_to_float(data): 
    if isinstance(data, Decimal):
        return float(data)
    return data

def convert_row_to_dict(row, column_names):
    row_dict = {}
    for column_name in column_names:
        row_dict[column_name] = convert_decimal_to_float(getattr(row, column_name))
    return row_dict