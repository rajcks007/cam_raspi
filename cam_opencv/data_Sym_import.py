from lib import sys, importlib  

def data_import():
    if "digit_data" in sys.modules:
        del sys.modules["digit_data"]  # Remove old module completely
    import digit_data
    importlib.reload(digit_data)  # Force reload every time
    from digit_data import data_1, data_2
    return data_1, data_2

def symbol_import():
    if "symbol_data" in sys.modules:
        del sys.modules["symbol_data"]  # Remove old module completely
    import symbol_data
    importlib.reload(symbol_data)  # Force reload every time
    from symbol_data import symbol_1, symbol_2 # Adjust these imports based on the actual variables you need
    return symbol_1, symbol_2