from math import log10, log, floor
from scipy import interpolate
import numpy as np

class TsPoint:
    def __init__(self, x, y, slope):
        self.x = x
        self.y = y
        self.slope = slope

        
lumLow = [ log10(0.0001), log10(0.02) ]           # luminance
stopsLow = [ -15.0, -6.5 ]                        # stops
pctsLow = [ 0.14, 0.35 ]                          # percentages

lumHigh = [ log10(48.), log10(10000.) ]           # luminance
stopsHigh = [ 6.5, 18. ]                          # stops
pctsHigh = [ 0.89, 0.91 ]                         # percentages

interp_ACESmin = interpolate.interp1d( lumLow, stopsLow)
interp_pctLow = interpolate.interp1d( stopsLow, pctsLow)

interp_ACESmax = interpolate.interp1d( lumHigh, stopsHigh)
interp_pctHigh = interpolate.interp1d( stopsHigh, pctsHigh)

def lookup_ACESmin( minLum):
    return 0.18*pow(2.,interp_ACESmin( log10(minLum)))
    
def lookup_ACESmax( maxLum):
    return 0.18*pow(2.,interp_ACESmax( log10(maxLum)))

def lookup_pctLow( ACESlow):
    return interp_pctLow( log(ACESlow/0.18,2.))

def lookup_pctHigh( ACEShigh):
    return interp_pctHigh( log(ACEShigh/0.18,2.))

def lookup_expShift( midLum):
    return log(inv_ssts( midLum),2.)-log(0.18,2.)

def shift( x, expShift):
    return pow(2.,(np.log2(x)-expShift));

M = np.array([[0.5, -1.0, 0.5], [-1.0, 1.0, 0.0], [0.5, 0.5, 0.0]])



def init_coefsLow_wPct( minPt, midPt, pctLow):
    coefsLow = [None] * 5

    knotIncLow = (log10(midPt.x) - log10(minPt.x)) / 3.

    # Determine two lowest coefficients (straddling minPt)
    coefsLow[0] = (minPt.slope * (log10(minPt.x)-0.5*knotIncLow)) + ( log10(minPt.y) - minPt.slope * log10(minPt.x))
    coefsLow[1] = (minPt.slope * (log10(minPt.x)+0.5*knotIncLow)) + ( log10(minPt.y) - minPt.slope * log10(minPt.x))

    # Determine two highest coefficients (straddling midPt)
    coefsLow[3] = (midPt.slope * (log10(midPt.x)-0.5*knotIncLow)) + ( log10(midPt.y) - midPt.slope * log10(midPt.x))
    coefsLow[4] = (midPt.slope * (log10(midPt.x)+0.5*knotIncLow)) + ( log10(midPt.y) - midPt.slope * log10(midPt.x))
    
    # Middle coefficient (which defines the "sharpness of the bend") is linearly interpolated
    coefsLow[2] = log10(minPt.y) + pctLow*(log10(midPt.y)-log10(minPt.y))
    
    return coefsLow

def init_coefsHigh_wPct( midPt, maxPt, pctHigh):
    coefsHigh = [None] * 5
    
    knotIncHigh = (log10(maxPt.x) - log10(midPt.x)) / 3.

    # Determine two lowest coefficients (straddling midPt)
    coefsHigh[0] = (midPt.slope * (log10(midPt.x)-0.5*knotIncHigh)) + ( log10(midPt.y) - midPt.slope * log10(midPt.x))
    coefsHigh[1] = (midPt.slope * (log10(midPt.x)+0.5*knotIncHigh)) + ( log10(midPt.y) - midPt.slope * log10(midPt.x))

    # Determine two highest coefficients (straddling maxPt)
    coefsHigh[3] = (maxPt.slope * (log10(maxPt.x)-0.5*knotIncHigh)) + ( log10(maxPt.y) - maxPt.slope * log10(maxPt.x))
    coefsHigh[4] = (maxPt.slope * (log10(maxPt.x)+0.5*knotIncHigh)) + ( log10(maxPt.y) - maxPt.slope * log10(maxPt.x))

    # Middle coefficient (which defines the "sharpness of the bend") is linearly interpolated
    coefsHigh[2] = log10(midPt.y) + pctHigh*(log10(maxPt.y)-log10(midPt.y))
    
    return coefsHigh;    





defaultMin = TsPoint( 0.18*pow(2.,-15.), 0.0001, 0.1)
defaultMid = TsPoint( 0.18, 4.8, 1.5)
defaultMax = TsPoint( 0.18*pow(2., 18.), 10000., 0.1)

def ssts( xIn, minPt=defaultMin, midPt=defaultMid, maxPt=defaultMax, pctLow=lookup_pctLow(defaultMin.x), pctHigh=lookup_pctHigh(defaultMax.x)):
    N_KNOTS = 4
    coefsLow = np.array(init_coefsLow_wPct( minPt, midPt, pctLow))
    coefsHigh = np.array(init_coefsHigh_wPct( midPt, maxPt, pctHigh))

    # Tone scale is defined in log-log space, so we must log the input
    logx = np.log10( xIn)

    # Create empty array to populate with the calculations
    logy = np.zeros_like( logx)
    
    indexLow = (logx <= log10(minPt.x))     # less than minPt (i.e. shadow linear extension)
    indexLowHalf = ( (logx > log10(minPt.x)) & (logx < log10(midPt.x)) )  # between minPt and midPt (i.e. lower half of S-curve, shadows)
    indexHighHalf = ( (logx >= log10(midPt.x)) & (logx < log10(maxPt.x)) ) # between midPt and maxPt (i.e. upper half of S-curve, highlights)
    indexHigh = (logx >= log10(maxPt.x))    # greater than maxPt (i.e. highlight linear extension)

#     print "indexLow: ", indexLow
#     print "indexLowHalf: ", indexLowHalf
#     print "indexHighHalf: ", indexHighHalf
#     print "indexHigh: ", indexHigh

    # Calculate values for linear extension in shadows
    # If minPt.slope=0, this reduces to logy[indexLow] = minPt.y
    logy[indexLow] = logx[indexLow] * minPt.slope + ( log10(minPt.y) - minPt.slope * log10(minPt.x) )

    # Calculate values for lower half of S-curve, shadows 
    if (np.sum( indexLowHalf) > 0):
        knot_coord = (N_KNOTS-1) * (logx[indexLowHalf]-log10(minPt.x))/(log10(midPt.x)-log10(minPt.x))
        jLow = np.int8(knot_coord)
        tLow = knot_coord - jLow
    
        cfLow = np.array( [coefsLow[ jLow], coefsLow[ jLow + 1], coefsLow[ jLow + 2]] )
        monomialsLow = np.array( [ tLow * tLow, tLow, np.ones_like(cfLow[0,:]) ] )
        basisLow = np.dot(M,cfLow)
        logy[indexLowHalf] = sum( monomialsLow * basisLow)

    # Calculate values for upper half of S-curve, highlights     
    if (np.sum( indexHighHalf) > 0):    
        knot_coord = (N_KNOTS-1) * (logx[indexHighHalf]-log10(midPt.x))/(log10(maxPt.x)-log10(midPt.x))
        jHigh = np.int8(knot_coord)
        tHigh = knot_coord - jHigh

        cfHigh = np.array( [coefsHigh[ jHigh], coefsHigh[ jHigh + 1], coefsHigh[ jHigh + 2]] )
        monomialsHigh = np.array( [ tHigh * tHigh, tHigh, np.ones_like(cfHigh[0,:]) ] )
        basisHigh = np.dot(M,cfHigh)
        logy[indexHighHalf] = sum( monomialsHigh * basisHigh)

    # Calculate values for linear extension in highlights
    logy[indexHigh] = logx[indexHigh] * maxPt.slope + ( log10(maxPt.y) - maxPt.slope * log10(maxPt.x) )

    # Unlog the result
    return pow(10.,logy)


def inv_ssts( yIn, minPt=defaultMin, midPt=defaultMid, maxPt=defaultMax, pctLow=lookup_pctLow(defaultMin.x), pctHigh=lookup_pctHigh(defaultMax.x)):
    N_KNOTS = 4

    coefsLow = np.array(init_coefsLow_wPct( minPt, midPt, pctLow))
    coefsHigh = np.array(init_coefsHigh_wPct( midPt, maxPt, pctHigh))

    KNOT_INC_LOW = (log10(midPt.x)-log10(minPt.x))/(N_KNOTS - 1.)
    KNOT_INC_HIGH = (log10(maxPt.x)-log10(midPt.x))/(N_KNOTS - 1.)    

    KNOT_Y_LOW = np.zeros(N_KNOTS)
    for i in range(0, N_KNOTS):
        KNOT_Y_LOW[ i] = (coefsLow[i] + coefsLow[i+1]) / 2.

    KNOT_Y_HIGH = np.zeros(N_KNOTS)
    for i in range(0, N_KNOTS):
        KNOT_Y_HIGH[ i] = (coefsHigh[i] + coefsHigh[i+1]) / 2.
        
    logy = np.log10( yIn );

    logx = np.zeros_like( logy)

    indexLow = (logy <= log10(minPt.y))  # less than minPt (i.e. shadow linear extension)
    indexLowHalf = ( (logy > log10(minPt.y)) & (logy <= log10(midPt.y)) )  # between minPt and midPt (i.e. lower half of S-curve, shadows)
    indexHighHalf = ( (logy > log10(midPt.y)) & (logy < log10(maxPt.y)) )  # between midPt and maxPt (i.e. upper half of S-curve, highlights)
    indexHigh = (logy >= log10(maxPt.y)) # greater than maxPt (i.e. highlight linear extension)

    # Calculate values for linear extension in shadows
    # Protect against slope=0, divide-by-zero error
    if (minPt.slope == 0):
        logx[indexLow] = log10( minPt.x)
    else:
        logx[indexLow] = (logy[indexLow] - (log10(minPt.y)-minPt.slope*log10(minPt.x))) / minPt.slope

    # Calculate values for lower half of S-curve, shadows 
    if (np.sum( indexLowHalf) > 0):
        j = np.zeros(np.sum(indexLowHalf),dtype=np.int)

        j[ (logy[indexLowHalf] > KNOT_Y_LOW[0]) & (logy[indexLowHalf] < KNOT_Y_LOW[1])] = 0
        j[ (logy[indexLowHalf] > KNOT_Y_LOW[1]) & (logy[indexLowHalf] < KNOT_Y_LOW[2])] = 1
        j[ (logy[indexLowHalf] > KNOT_Y_LOW[2]) & (logy[indexLowHalf] < KNOT_Y_LOW[3])] = 2

        cf = np.array( [coefsLow[j], coefsLow[j+1], coefsLow[j+2]] )
            
        tmp = np.dot(M,cf)
        
        a = tmp[0]
        b = tmp[1]
        c = tmp[2]
        c = c - logy[indexLowHalf]
        
        d = np.sqrt( b*b - 4.*a*c)
        t = (2.*c)/(-d-b)
        
        logx[indexLowHalf] = np.log10( minPt.x) + (t+j)*KNOT_INC_LOW

    # Calculate values for upper half of S-curve, highlights 
    if (np.sum( indexHighHalf) > 0):
        j = np.zeros(np.sum(indexHighHalf),dtype=np.int)

        j[ (logy[indexHighHalf] > KNOT_Y_HIGH[0]) & (logy[indexHighHalf] < KNOT_Y_HIGH[1])] = 0
        j[ (logy[indexHighHalf] > KNOT_Y_HIGH[1]) & (logy[indexHighHalf] < KNOT_Y_HIGH[2])] = 1
        j[ (logy[indexHighHalf] > KNOT_Y_HIGH[2]) & (logy[indexHighHalf] < KNOT_Y_HIGH[3])] = 2

        cf = np.array( [coefsHigh[j], coefsHigh[j+1], coefsHigh[j+2]] )
            
        tmp = np.dot(M,cf)
        
        a = tmp[0]
        b = tmp[1]
        c = tmp[2]
        c = c - logy[indexHighHalf]
        
        d = np.sqrt( b*b - 4.*a*c)
        t = (2.*c)/(-d-b)
        
        logx[indexHighHalf] = np.log10( midPt.x) + (t+j)*KNOT_INC_HIGH

    # Calculate values for linear extension in highlights
    # Protect against slope=0, divide-by-zero error
    if (maxPt.slope == 0.):
        logx[indexHigh] = log10( maxPt.x)
    else:
        logx[indexHigh] = (logy[indexHigh] - (log10(maxPt.y)-maxPt.slope*log10(maxPt.x))) / maxPt.slope

    return pow(10.,logx)
