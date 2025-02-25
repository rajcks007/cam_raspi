def data_valid(data) :
    # Loop through each bit position (from 0 to 6)
    for bit_position in range(7):  # We have 7 bits, so positions 0 to 6
        found_one = False
        # Check each data point to see if the bit at the current position is '1'
        for data_point in data:
            if data_point[bit_position] == 1:
                found_one = True
                break  # No need to check further if we find at least one '1'
        
        # Print the result for the current bit position
        #   if found_one:
        #       print(f"Bit position {bit_position} has at least one '1'.")
        #   else:
        #       print(f"Bit position {bit_position} has only '0' values.")

        # For bit position 3, we don't care about the result
        if bit_position == 3:
            print(f"Bit position {bit_position}: result ignored.")
            continue
    
        # For other positions, check the result and print accordingly
        if found_one:
            print(f"Bit position {bit_position} has at least one '1'.")
        else:
            print(f"Error: Bit position {bit_position} does not have any '1' values.")