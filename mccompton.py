import os,sys
import ROOT as rt
import numpy as np

def drawFromVial( center, height, width ):
    """
    modeled as box
    """
    z = height*2.0*(np.random.random()-0.5) + center[2]
    x = width*2.0*(np.random.random()-0.5) + center[0]
    y = width*2.0*(np.random.random()-0.5) + center[1]
    return np.asarray( (x,y,z), dtype=np.float )
    

def drawFromNaI( center_dist, radius, thickness, angle ):
    """
    modeled as cylinder. doing rejection throwing.
    starts on x+ facing x-: basis
    localz+ = global x-
    localx+ = global z+
    localy+ = global y+
    """
    ok = False
    r = 0.0
    ntries = 0
    while not ok:
        box = drawFromVial( (0,0,0), thickness, radius )
        r = np.sqrt(box[0]*box[0]+box[1]*box[1])
        if r<radius:
            ok = True
        ntries +=1
        if ntries>100000:
            print "stuck in throwing NaI position!"
            sys.exit(-1)

    # put in global cooidinates
    globalx = center_dist - box[2]
    globaly = box[1]
    globalz = box[0]

    # rotate to correct angle
    angle_rad = angle*np.pi/180.0
    c = np.cos( angle_rad )
    s = np.sin( angle_rad )
    rotx = c*globalx - s*globaly
    roty = s*globalx + c*globaly
    rotz = globalz

    return np.asarray( (rotx,roty,rotz), dtype=np.float )

def comptonProb( p_in, p_out ):
    pass

def electronDir( p_in, p_out ):
    pass

def runMC(nthrows,naidist,naiangle,sourcedist,sourceangle,vis=None):

    # define source pos
    csrc = np.cos( sourceangle*np.pi/180.0 )
    ssrc = np.sin( sourceangle*np.pi/180.0 )

    srcpos = np.asarray( ( csrc*sourcedist, -ssrc*sourcedist, 0.0  ), dtype=np.float )


    naihit = np.zeros( (nthrows,3) )
    vialhit = np.zeros( (nthrows,3) )

    for i in range(0,nthrows):
        vialpos = drawFromVial( (0,0,0), 5.0, 1.0 ) # vial
        naipos = drawFromNaI( naidist, 2.54*2.5, 2.54*2.5, naiangle )
        naihit[i,:] = naipos[:]
        vialhit[i,:] = vialpos[:]
    if vis is not None:
        gnai = gl.GLScatterPlotItem(pos=naihit, color=(1,1,1,.3), size=0.1, pxMode=False)
        gvial = gl.GLScatterPlotItem(pos=vialhit, color=(1,1,1,.3), size=0.1, pxMode=False)
        vis.addItem( gnai )
        vis.addItem( gvial )
        
        srcarr = np.empty( (1,3) )
        srcarr[0,:] = srcpos[:]
        gsrc = gl.GLScatterPlotItem(pos=srcarr, color=(1,0,0,1), size=2.0, pxMode=False)
        vis.addItem( gsrc )
            

if __name__ == "__main__":
    app = None
    usevis = True
    vis = None
    nthrows = 10000
    sourcedist = 100.0
    sourceangle = 0.0

    if usevis:
        from pyqtgraph.Qt import QtCore, QtGui
        import pyqtgraph.opengl as gl
        # start up qt
        app = QtGui.QApplication([])
        # define vis
        vis = gl.GLViewWidget()
        vis.opts['distance'] = 500.0
        vis.show()
        vis.setWindowTitle('compton scattering')
        # define grid
        g = gl.GLGridItem()
        g.setSize( x=500, y=500, z=0 )
        g.setSpacing( x=10, y=10, z=10 )
        vis.addItem(g)

    runMC( nthrows, 100.0, 45.0, sourcedist, sourceangle, vis=vis )
    ## Start Qt event loop unless running in interactive mode.
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    
