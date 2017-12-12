import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import ssts
from math import log10, log

def aces2stops( aces):
    return np.log2(aces)-np.log2(0.18)

hgt = 0.04
wdt = 0.17
hspc = 0.15
ledge = 0.05

fig, ax = plt.subplots( figsize=(12,7) )
plt.subplots_adjust(left=ledge, top=0.97, bottom=0.25, right=0.97)

# ACES values to plot
aces = 0.18*pow(2.,np.arange(-23,23,0.1))

# "RRT" settings
rrtMin = ssts.TsPoint( 0.18*pow(2.,-15.), 0.0001, 0.0)
rrtMid = ssts.TsPoint( 0.18, 4.8, 1.5)
rrtMax = ssts.TsPoint( 0.18*pow(2.,18.), 10000., 0.0)
rrt = np.log10( ssts.ssts(aces, rrtMin, rrtMid, rrtMax, ssts.lookup_pctLow(rrtMin.x), ssts.lookup_pctHigh(rrtMax.x)) )

# "48-nit" settings
cinemaMin = ssts.TsPoint( 0.18*pow(2.,-6.5), 0.02, 0.0)
cinemaMid = ssts.TsPoint( 0.18, 4.8, 1.5)
cinemaMax = ssts.TsPoint( 0.18*pow(2.,6.5), 48., 0.0)
cinema = np.log10( ssts.ssts(aces, cinemaMin, cinemaMid, cinemaMax, ssts.lookup_pctLow(cinemaMin.x), ssts.lookup_pctHigh(cinemaMax.x)) )

# "key points"
minyRange = [0.0001,0.001,0.02]
midyRange = [2.,4.8,20.]
maxyRange = [48.,1000.,10000.]
minSlopeRange = [0.0, 0.0, 0.15]
maxSlopeRange = [0.0, 0.0, 0.15]

minsl = minSlopeRange[1]
midsl = 1.5
maxsl = maxSlopeRange[1]

miny = minyRange[1]
minx = ssts.lookup_ACESmin( miny)

midy = 4.8
midx = 0.18

maxy = maxyRange[1]
maxx = ssts.lookup_ACESmax( maxy)

pctLow = ssts.lookup_pctLow( minx)
pctHigh = ssts.lookup_pctHigh( maxx)

# Parameterized tone curve
initialMin = ssts.TsPoint( minx, miny, minsl)
initialMid = ssts.TsPoint( midx, midy, midsl)
initialMax = ssts.TsPoint( maxx, maxy, maxsl)
Y = np.log10( ssts.ssts(aces,initialMin,initialMid,initialMax,ssts.lookup_pctLow(initialMin.x),ssts.lookup_pctHigh(initialMax.x)) )
# d1 = ssts.ssts_d1(aces,initialMin,initialMid,initialMax,ssts.lookup_pctLow(initialMin.x),ssts.lookup_pctHigh(initialMax.x))

# Make the initial plot
x = aces2stops(aces)
ll, = plt.plot( x, rrt, lw=1, color='black', linestyle='--', label='"OCES" (i.e. RRT)')
lll, = plt.plot( x, cinema, lw=1, color='black', linestyle=':', label='48-nit cinema')
l, = plt.plot( x, Y, lw=2, color='red', label='Adjustable')
# lderiv, = plt.plot( x, d1, lw=1, color='red', linestyle=':', label='First derivative')

hmin, = plt.plot( aces2stops(minx), log10(miny), color='red', marker='o')
hmid, = plt.plot( aces2stops(midx), log10(midy), color='red', marker='o')
hmax, = plt.plot( aces2stops(maxx), log10(maxy), color='red', marker='o')

# hpctL, = plt.plot( aces2stops(midx)-((aces2stops(midx)-aces2stops(minx))/2.), log10(miny)+((log10(midy)-log10(miny))*pctLow), color='red', marker='x')
# hpctH, = plt.plot( aces2stops(maxx)-((aces2stops(maxx)-aces2stops(midx))/2.), log10(midy)+((log10(maxy)-log10(midy))*pctHigh), color='red', marker='x')

plt.axis([-20, 20, -4.5, 4.5])
plt.grid(b=True,which='major',axis='both')
plt.xlabel("scene exposure - stops relative to 18% mid-gray")
plt.ylabel("log$_{10}$ luminance ($cd/m^2$)")

plt.legend(loc='upper left')

axcolor = '#d1d1fa'

# Create sliders
ax_minY = plt.axes([ledge+0.07, 0.135, wdt, hgt], facecolor='white')
s_minY = Slider(ax_minY, 'black lum ($cd/m^2$)', np.log10(minyRange[0]), np.log10(minyRange[2]), valinit=np.log10(minyRange[1]), valfmt="%0.4f")
s_minY.valtext.set_text( pow(10., s_minY.val))

ax_midY = plt.axes([ledge+wdt+hspc+0.07, 0.135, wdt, hgt], facecolor='white')
s_midY = Slider(ax_midY, '18% lum ($cd/m^2$)', np.log10(midyRange[0]), np.log10(midyRange[2]), valinit=np.log10(midyRange[1]), valfmt="%0.1f")
s_midY.valtext.set_text( pow(10., s_midY.val))

ax_maxY = plt.axes([ledge+2*wdt+2*hspc+0.07, 0.135, wdt, hgt], facecolor='white')
s_maxY = Slider(ax_maxY, 'white lum ($cd/m^2$)', np.log10(maxyRange[0]), np.log10(maxyRange[2]), valinit=np.log10(maxyRange[1]), valfmt="%i")
s_maxY.valtext.set_text( pow(10., s_maxY.val))

ax_minSlope = plt.axes([ledge+0.07, 0.08, wdt, hgt], facecolor='white')
s_minSlope = Slider(ax_minSlope, 'low slope', minSlopeRange[0], minSlopeRange[2], valinit=minSlopeRange[1], valfmt="%0.1f")
s_minSlope.valtext.set_text( s_minSlope.val)

ax_maxSlope = plt.axes([ledge+2*wdt+2*hspc+0.07, 0.08, wdt, hgt], facecolor='white')
s_maxSlope = Slider(ax_maxSlope, 'high slope', maxSlopeRange[0], maxSlopeRange[2], valinit=maxSlopeRange[1], valfmt="%0.1f")
s_maxSlope.valtext.set_text( s_maxSlope.val)

def update(val):
    midy = 4.8
    midx = 0.18
    miny = pow(10.,s_minY.val)
    minx = ssts.lookup_ACESmin(miny)
    maxy = pow(10.,s_maxY.val)
    maxx = ssts.lookup_ACESmax(maxy)
    pctLow = ssts.lookup_pctLow( minx)
    pctHigh = ssts.lookup_pctHigh( maxx)
    minsl = s_minSlope.val
    maxsl = s_maxSlope.val

    Min = ssts.TsPoint( minx, miny, minsl)
    Mid = ssts.TsPoint( midx, midy, midsl)
    Max = ssts.TsPoint( maxx, maxy, maxsl)

    expShift = ssts.lookup_expShift( pow(10.,s_midY.val) )

    l.set_ydata( np.log10( ssts.ssts(aces,Min,Mid,Max,pctLow,pctHigh)) )
    l.set_xdata( aces2stops( ssts.shift(aces,expShift)))
#     lderiv.set_ydata( ssts.ssts_d1(aces,Min,Mid,Max,pctLow,pctHigh))
#     lderiv.set_xdata( aces2stops( ssts.shift(aces,expShift)))

    hmin.set_xdata( aces2stops(ssts.shift(minx,expShift)))
    hmin.set_ydata( log10(miny))
#     hmid.set_xdata( aces2stops(ssts.shift(midx,expShift)))
    hmid.set_xdata( aces2stops(midx))
    hmid.set_ydata( s_midY.val)
    hmax.set_xdata( aces2stops(ssts.shift(maxx,expShift)))
    hmax.set_ydata( log10(maxy))
#     hpctL.set_xdata( s_midX.val-((s_midX.val-s_minX.val)/2.) )
#     hpctL.set_ydata( log10(miny)+((log10(midy)-log10(miny))*pctLow) )
#     hpctH.set_xdata( s_midX.val+((s_maxX.val-s_midX.val)/2.) )
#     hpctH.set_ydata( log10(midy)+((log10(maxy)-log10(midy))*pctHigh) )
    
    s_minY.valtext.set_text( round(miny,4))
    s_midY.valtext.set_text( round(pow(10.,s_midY.val),1))
    s_maxY.valtext.set_text( round(maxy))
    s_minSlope.valtext.set_text( round(minsl,2))
    s_maxSlope.valtext.set_text( round(maxsl,2))
    
    fig.canvas.draw_idle()

s_minY.on_changed(update)
s_midY.on_changed(update)
s_maxY.on_changed(update)
s_minSlope.on_changed(update)
s_maxSlope.on_changed(update)

# Reset button
resetax = plt.axes([0.8, 0.025, 0.1, 0.03])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    s_minY.reset()
    s_midY.reset()
    s_maxY.reset()
button.on_clicked(reset)


# Preset buttons
presetaxcolor = '#92CCEA'
presetax1 = plt.axes([0.05, 0.025, 0.1, 0.03])
button1 = Button(presetax1, '"OCES"', color=presetaxcolor)

presetax2 = plt.axes([0.2, 0.025, 0.1, 0.03])
button2 = Button(presetax2, 'x300', color=presetaxcolor)

presetax3 = plt.axes([0.35, 0.025, 0.1, 0.03])
button3 = Button(presetax3, 'PRM-4220', color=presetaxcolor)

presetax4 = plt.axes([0.5, 0.025, 0.1, 0.03])
button4 = Button(presetax4, 'Dolby Cinema', color=presetaxcolor)

presetax5 = plt.axes([0.65, 0.025, 0.1, 0.03])
button5 = Button(presetax5, 'Standard Cinema', color=presetaxcolor)

def preset_OCES(event):
    s_minY.set_val( np.log10(0.0001))
    s_midY.set_val( np.log10(4.8))
    s_maxY.set_val( np.log10(10000.))

def preset_x300(event):
    s_minY.set_val( np.log10(0.0001))
    s_midY.set_val( np.log10(10.0))
    s_maxY.set_val( np.log10(1000.))

def preset_prm4220(event):
    s_minY.set_val( np.log10(0.005))
    s_midY.set_val( np.log10(10.0))
    s_maxY.set_val( np.log10(600.))

def preset_dolbyCinema(event):
    s_minY.set_val( np.log10(0.0001))
    s_midY.set_val( np.log10(7.2))
    s_maxY.set_val( np.log10(108.))

def preset_cinema(event):
    s_minY.set_val( np.log10(0.02))
    s_midY.set_val( np.log10(4.8))
    s_maxY.set_val( np.log10(48.))
    
button1.on_clicked(preset_OCES)
button2.on_clicked(preset_x300)
button3.on_clicked(preset_prm4220)
button4.on_clicked(preset_dolbyCinema)
button5.on_clicked(preset_cinema)


plt.show()