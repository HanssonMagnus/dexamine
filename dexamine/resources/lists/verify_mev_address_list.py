'''
When the MEV contract list is updated check that:
    - All the old addresses are present in the new list.
    - No duplicates in the new list.
'''
# Import packages
from collections import Counter

# Read the two files
with open('mev_contracts_old.txt') as f1, open('mev_contracts.txt') as f2:
    list1 = set(line.strip().lower() for line in f1)  # Normalize to lowercase
    list2 = set(line.strip().lower() for line in f2)  # Normalize to lowercase

# Find duplicates in list2
duplicates_in_list2 = [address for address, count in Counter(list2).items() if count > 1]

# Convert list2 to a set for subset check
list2_set = set(list2)

# Find missing addresses
missing_addresses = list1 - list2_set

# Results
if missing_addresses:
    print("Some addresses in list1 are missing from list2:")
    for address in missing_addresses:
        print(address)
else:
    print("All addresses in list1 are in list2")

if duplicates_in_list2:
    print("\nDuplicates found in list2:")
    for address in duplicates_in_list2:
        print(address)
else:
    print("\nNo duplicates found in list2")
