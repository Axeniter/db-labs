def print_table(data, title=None):
    """Вывод таблицы"""
    if not data:
        print("Нет данных")
        return
    
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    columns = list(data[0].keys())
    
    col_widths = {}
    for col in columns:
        max_len = len(str(col))
        for row in data:
            value = row.get(col, '')
            max_len = max(max_len, len(str(value)))
        col_widths[col] = min(max_len, 50)
    
    total_width = sum(col_widths.values()) + (3 * len(columns)) + 1
    

    print("┌" + "─" * (total_width - 2) + "┐")
    print("│", end="")
    for col in columns:
        print(f" {col:<{col_widths[col]}} │", end="")
    print()
    print("├" + "─" * (total_width - 2) + "┤")
    
    for row in data:
        print("│", end="")
        for col in columns:
            value = row.get(col)
            
            if value is None:
                value = "-"
            
            str_value = str(value)
            if len(str_value) > col_widths[col]:
                str_value = str_value[:col_widths[col] - 3] + "..."
            
            print(f" {str_value:<{col_widths[col]}} │", end="")
        print()
    
    print("└" + "─" * (total_width - 2) + "┘")
    print()