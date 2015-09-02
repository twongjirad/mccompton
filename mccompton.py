import os,sys
import ROOT as rt
import numpy as np

import gen

class EventData:
    """
    a place to store all the numpy data associated with each event
    """
    def __init__(self):
        # these will all be numpy arrays
        self.nthrows = None
        self.initialphotonE = None
        self.photon_in = None
        self.photon_out = None
        self.electron_dir = None
        self.electron_energy = None
        self.vialhit = None
        self.NaIhit = None

def comptonProb( p_in, p_out ):
    pass

def electronDir( p_in, p_out, Ekev ):
    """
    E1 = initial gamma energy
    E2 = out-going gamma energy
    Ee = electron energy
    """
    norm1 = np.linalg.norm(p_in)
    norm2 = np.linalg.norm(p_out)
    d1 = np.copy( p_in )
    d2 = np.copy( p_out )
    d1 /= norm1
    d2 /= norm2
    pcos = np.dot( d1, d2 )
    me = 511.0 # keV
    E2 = Ekev/(1 + (Ekev/me)*(1-pcos)) # kev
    Ee = Ekev-E2+me # kev
    #print Ekev,"+",me," = ",E2,"+",Ee
    mome = np.zeros( 3, dtype=np.float )
    mome = Ekev*d1 - E2*d2
    de = np.copy( mome )
    de /= np.linalg.norm( de )
    return de, Ee

def runMC(nthrows,naidist,naiangle,sourcedist,sourceangle,pmtplanedist,vis=None):
    """
    pmt plane sits normal to -x
    """

    data = EventData()
    data.nthrows = nthrows
    data.initialphotonE = 611.0 # Na source

    # define source pos
    csrc = np.cos( sourceangle*np.pi/180.0 )
    ssrc = np.sin( sourceangle*np.pi/180.0 )

    srcpos = np.asarray( ( csrc*sourcedist, -ssrc*sourcedist, 0.0  ), dtype=np.float )

    # maybe this moves into EventData
    data.NaIhit = np.zeros( (nthrows,3) )
    data.vialhit = np.zeros( (nthrows,3) )
    data.electron_dir = np.zeros( (nthrows,3) )
    data.electron_dir[:,0] = 1.0
    data.electron_energy = np.zeros( nthrows, dtype=np.float )
    data.photon_in = np.zeros( (nthrows,3) )    
    data.photon_out = np.zeros( (nthrows,3) )

    for i in range(0,nthrows):
        data.vialhit[i,:] = gen.drawFromVial( (0,0,0), 5.0, 1.0 ) # vial
        data.NaIhit[i,:] = gen.drawFromNaI( naidist, 2.54*2.5, 2.54*2.5, naiangle )
        data.photon_in[i,:] = data.vialhit[i,:] - srcpos[:]
        data.photon_out[i,:] = data.NaIhit[i,:] - data.vialhit[i,:]
        data.photon_in[i,:] /= np.linalg.norm( data.photon_in[i] )
        data.photon_out[i,:] /= np.linalg.norm( data.photon_out[i] )
        data.electron_dir[i,:], data.electron_energy[i] = electronDir( data.photon_in[i], data.photon_out[i], data.initialphotonE )
        
    return data

    if vis is not None:
        me = 511.0 # keV
        
        
                

if __name__ == "__main__":
    app = None
    usevis = True
    display = None
    vis = None
    nthrows = 200
    sourcedist = 100.0
    sourceangle = 10.0
    pmtplanedist = 30.0
    pmtplanewidth = 2.54*10.0

    if usevis:
        # start up qt
        app = QtGui.QApplication([])
        # define vis
        display = ComptonDisplay()
        display.show()
        vis = display.vis
                
    runMC( nthrows, 100.0, 45.0, sourcedist, sourceangle, pmtplanedist, vis=vis )
    ## Start Qt event loop unless running in interactive mode.
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    
