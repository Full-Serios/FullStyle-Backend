from decimal import Decimal

# PostgreSQL maneja tipo Decimal, para no causar problemas al serializar a JSON, se convierte a float
def convert_decimal_to_float(data): 
    if isinstance(data, Decimal):
        return float(data)
    return data

def convert_row_to_dict(row, column_names):
    row_dict = {}
    for column_name in column_names:
        row_dict[column_name] = convert_decimal_to_float(getattr(row, column_name))
    return row_dict