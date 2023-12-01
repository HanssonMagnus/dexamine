# Import packages

###################################################################################################
# Uniswp v3 check functions
###################################################################################################
def has_uniswap_v3_swap_event(topics_0):
    '''Check if the tx has any Uniswp v3 swap events.'''
    swap_v3 = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
    if swap_v3 in topics_0:
        return True
    else:
        return False

