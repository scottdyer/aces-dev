import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from ssts import ssts, TsPoint
from math import log10, log

def aces2stops( aces):
    return np.log2(aces)-np.log2(0.18)

hgt = 0.04
wdt = 0.23
hspc = 0.1
ledge = 0.05

fig, ax = plt.subplots( figsize=(12,7) )
plt.subplots_adjust(left=ledge, top=0.97, bottom=0.4, right=0.97)

aces = 0.18*pow(2.,np.arange(-20,21,0.5))
Y = ssts(aces)

x = aces2stops(aces)
y = np.log10(Y)
l, = plt.plot( x, y, lw=2, color='red')

minxRange = [-20.,-15.,-6.5]
minyRange = [0.0001,0.0001,0.02]
minsRange = [0.,0.,1.]
midxRange = [-5.,-0.,5.]
midyRange = [0.,4.8,48.]
midsRange = [1.,1.5,2.]
maxxRange = [6.5,15.,20.]
maxyRange = [48.,10000.,10000.]
maxsRange = [0.,0.,1.]
pctLRange = [0.1, 0.25, 0.4]
pctHRange = [0.6, 0.75, 0.9]

minx = 0.18*pow(2.,minxRange[1])
miny = minyRange[1]
midx = 0.18*pow(2.,midxRange[1])
midy = midyRange[1]
maxx = 0.18*pow(2.,maxxRange[1])
maxy = maxyRange[1]
hmin, = plt.plot( aces2stops(minx), log10(miny), color='red', marker='o')
hmid, = plt.plot( aces2stops(midx), log10(midy), color='red', marker='o')
hmax, = plt.plot( aces2stops(maxx), log10(maxy), color='red', marker='o')

hpctL, = plt.plot( midxRange[1]-((midxRange[1]-minxRange[1])/2.), log10(miny)+((log10(midy)-log10(miny))*pctLRange[1]), color='red', marker='x')
hpctH, = plt.plot( midxRange[1]+((maxxRange[1]-midxRange[1])/2.), log10(midy)+((log10(maxy)-log10(midy))*pctHRange[1]), color='red', marker='x')

plt.axis([-20, 20, -4.5, 4.5])
plt.grid(b=True,which='major',axis='both')
plt.xlabel("scene exposure - stops relative to 18% mid-gray")
plt.ylabel("log$_{10}$ luminance ($cd/m^2$)")


axcolor = '#d1d1fa'

ax_minX = plt.axes([ledge, 0.175, wdt, hgt], facecolor='white')
s_minX = Slider(ax_minX, 'X', minxRange[0], minxRange[2], valinit=minxRange[1], valfmt="%1.1f")
ax_minY = plt.axes([ledge, 0.125, wdt, hgt], facecolor='white')
s_minY = Slider(ax_minY, 'Y', minyRange[0], minyRange[2], valinit=minyRange[1], valfmt="%1.4f")
ax_minS = plt.axes([ledge, 0.075, wdt, hgt], facecolor='white')
s_minS = Slider(ax_minS, 'slope', minsRange[0], minsRange[2], valinit=minsRange[1], valfmt="%1.1f")

ax_midX = plt.axes([ledge+wdt+hspc, 0.175, wdt, hgt], facecolor='white')
s_midX = Slider(ax_midX, 'X', midxRange[0], midxRange[2], valinit=midxRange[1], valfmt="%1.1f")
ax_midY = plt.axes([ledge+wdt+hspc, 0.125, wdt, hgt], facecolor='white')
s_midY = Slider(ax_midY, 'Y', midyRange[0], midyRange[2], valinit=midyRange[1], valfmt="%1.1f")
ax_midS = plt.axes([ledge+wdt+hspc, 0.075, wdt, hgt], facecolor='white')
s_midS = Slider(ax_midS, 'slope', midsRange[0], midsRange[2], valinit=midsRange[1], valfmt="%1.2f")

ax_maxX = plt.axes([ledge+2*wdt+2*hspc, 0.175, wdt, hgt], facecolor='white')
s_maxX = Slider(ax_maxX, 'X', maxxRange[0], maxxRange[2], valinit=maxxRange[1], valfmt="%1.1f")
ax_maxY = plt.axes([ledge+2*wdt+2*hspc, 0.125, wdt, hgt], facecolor='white')
s_maxY = Slider(ax_maxY, 'Y', maxyRange[0], maxyRange[2], valinit=maxyRange[1], valfmt="%i")
ax_maxS = plt.axes([ledge+2*wdt+2*hspc, 0.075, wdt, hgt], facecolor='white')
s_maxS = Slider(ax_maxS, 'slope', maxsRange[0], maxsRange[2], valinit=maxsRange[1], valfmt="%1.1f")

ax_pctL = plt.axes([ledge+0.5*wdt+0.6*hspc, 0.25, wdt, hgt], facecolor='white')
s_pctL = Slider(ax_pctL, '% low', pctLRange[0], pctLRange[2], valinit=pctLRange[1], valfmt="%1.2f")
ax_pctH = plt.axes([ledge+1.5*wdt+1.6*hspc, 0.25, wdt, hgt], facecolor='white')
s_pctH = Slider(ax_pctH, '% high', pctHRange[0], pctHRange[2], valinit=pctHRange[1], valfmt="%1.2f")


def update(val):
    minx = 0.18*pow(2.,s_minX.val)
    miny = s_minY.val
    minsl = s_minS.val
    midx = 0.18*pow(2.,s_midX.val)
    midy = s_midY.val
    midsl = s_midS.val
    maxx = 0.18*pow(2.,s_maxX.val)
    maxy = s_maxY.val
    maxsl = s_maxS.val
    pctLow = s_pctL.val
    pctHigh = s_pctH.val

    Min = TsPoint( minx, miny, minsl)
    Mid = TsPoint( midx, midy, midsl)
    Max = TsPoint( maxx, maxy, maxsl)

    l.set_ydata( np.log10( ssts(aces,Min,Mid,Max,pctLow,pctHigh)) )

    hmin.set_xdata( aces2stops(minx))
    hmin.set_ydata( log10(miny))
    hmid.set_xdata( aces2stops(midx))
    hmid.set_ydata( log10(midy))
    hmax.set_xdata( aces2stops(maxx))
    hmax.set_ydata( log10(maxy))
    hpctL.set_xdata( s_midX.val-((s_midX.val-s_minX.val)/2.) )
    hpctL.set_ydata( log10(miny)+((log10(midy)-log10(miny))*pctLow) )
    hpctH.set_xdata( s_midX.val+((s_maxX.val-s_midX.val)/2.) )
    hpctH.set_ydata( log10(midy)+((log10(maxy)-log10(midy))*pctHigh) )
    
    fig.canvas.draw_idle()
s_minX.on_changed(update)
s_minY.on_changed(update)
s_minS.on_changed(update)
s_midX.on_changed(update)
s_midY.on_changed(update)
s_midS.on_changed(update)
s_maxX.on_changed(update)
s_maxY.on_changed(update)
s_maxS.on_changed(update)
s_pctL.on_changed(update)
s_pctH.on_changed(update)

# reset button
resetax = plt.axes([0.8, 0.025, 0.1, 0.03])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    s_minX.reset()
    s_minY.reset()
    s_minS.reset()
    s_midX.reset()
    s_midY.reset()
    s_midS.reset()
    s_maxX.reset()
    s_maxY.reset()
    s_maxS.reset()
    s_pctL.reset()
    s_pctH.reset()
button.on_clicked(reset)



plt.show()