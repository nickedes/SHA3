def kernel_vortex():
    """
        Section 2.4.5 Pg 27.
    """
    # no. of points, will vary if result not found
    e2 = 4*4
    # need to generate e2 no. of points
    state = [[[list(GF(2))[0] for k in xrange(64)]
                   for j in xrange(5)] for i in xrange(5)]
    
    return state
