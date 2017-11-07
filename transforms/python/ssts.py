from math import log10, log, floor
from scipy import interpolate
import numpy as np

class TsPoint:
    def __init__(self, x, y, slope):
        self.x = x
        self.y = y
        self.slope = slope

        
lumLow = [ log10(0.0001), log10(0.02) ]           # luminance
stopsLow = [ -16.0, -6.5 ]                        # stops
pctsLow = [ 0.14, 0.35 ]                          # percentages

lumHigh = [ log10(48.), log10(10000.) ]           # luminance
stopsHigh = [ 6.5, log(65504.,2)-log(0.18,2) ]    # stops
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





defaultMin = TsPoint( 0.18*pow(2.,-16.), 0.0001, 0.0)
defaultMid = TsPoint( 0.18, 4.8, 1.5)
defaultMax = TsPoint( 65504., 10000., 0.0)

def ssts( xIn, minPt=defaultMin, midPt=defaultMid, maxPt=defaultMax, pctLow=lookup_pctLow(defaultMin.x), pctHigh=lookup_pctHigh(defaultMax.x)):
    N_KNOTS = 4.
    coefsLow = np.array(init_coefsLow_wPct( minPt, midPt, pctLow))
    coefsHigh = np.array(init_coefsHigh_wPct( midPt, maxPt, pctHigh))

    logx = np.log10( xIn)

    logy = np.zeros_like( logx)
    
    indexLow = (logx <= log10(minPt.x))
    indexLowHalf = ( (logx > log10(minPt.x)) & (logx < log10(midPt.x)) )
    indexHighHalf = ( (logx >= log10(midPt.x)) & (logx < log10(maxPt.x)) )
    indexHigh = (logx >= log10(maxPt.x))
    
    logy[indexLow] = logx[indexLow] * minPt.slope + ( log10(minPt.y) - minPt.slope * log10(minPt.x) )

    if (np.sum( indexLowHalf) > 0):
        knot_coord = (N_KNOTS-1) * (logx[indexLowHalf]-log10(minPt.x))/(log10(midPt.x)-log10(minPt.x))
        jLow = np.int8(knot_coord)
        tLow = knot_coord - jLow
    
        cfLow = np.array( [coefsLow[ jLow], coefsLow[ jLow + 1], coefsLow[ jLow + 2]] )
        monomialsLow = np.array( [ tLow * tLow, tLow, np.ones_like(cfLow[0,:]) ] )
        basisLow = np.dot(M,cfLow)        
        logy[indexLowHalf] = sum( monomialsLow * basisLow)
    
    if (np.sum( indexHighHalf) > 0):    
        knot_coord = (N_KNOTS-1) * (logx[indexHighHalf]-log10(midPt.x))/(log10(maxPt.x)-log10(midPt.x))
        jHigh = np.int8(knot_coord)
        tHigh = knot_coord - jHigh

        cfHigh = np.array( [coefsHigh[ jHigh], coefsHigh[ jHigh + 1], coefsHigh[ jHigh + 2]] )
        monomialsHigh = np.array( [ tHigh * tHigh, tHigh, np.ones_like(cfHigh[0,:]) ] )
        basisHigh = np.dot(M,cfHigh)
        logy[indexHighHalf] = sum( monomialsHigh * basisHigh)

    logy[indexHigh] = logx[indexHigh] * maxPt.slope + ( log10(maxPt.y) - maxPt.slope * log10(maxPt.x) )

    return pow(10.,logy)


# print ssts(np.array([0.15, 0.18, 0.5, 1.0, 10., 100., 40000.]))