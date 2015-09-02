from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

from mccompton import runMC

class ComptonDisplay(QtGui.QWidget):
    def __init__(self):
        super(ComptonDisplay,self).__init__()
        self.layout = QtGui.QGridLayout()
        self.setLayout( self.layout )


        self.vis = gl.GLViewWidget()
        self.layout.addWidget( self.vis, 0, 0 )
        self.layout.setRowMinimumHeight( 0, 400 )
        self.vis.opts['distance'] = 200.0
        #vis.show()
        #self.vis.setWindowTitle('compton scattering')
        # define grid
        g = gl.GLGridItem()
        g.setSize( x=500, y=500, z=0 )
        g.setSpacing( x=10, y=10, z=10 )
        self.vis.addItem(g)

        # inputs
        self.buttonlayout = QtGui.QGridLayout()
        self.layout.addLayout( self.buttonlayout, 1, 0 )
        
        self.nthrows = QtGui.QLineEdit("1000")
        self.naidist = QtGui.QLineEdit("50.0")
        self.naiangle = QtGui.QLineEdit("30.0")
        self.sourcedist = QtGui.QLineEdit( "50.0" )
        self.sourceangle = QtGui.QLineEdit("20.0")
        self.pmtplanedist = QtGui.QLineEdit("25.0")

        self.sim = QtGui.QPushButton("Simulate!")
        self.buttonlayout.addWidget( QtGui.QLabel("nthrows"), 0, 0 )
        self.buttonlayout.addWidget( self.nthrows, 0, 1 )
        self.buttonlayout.addWidget( QtGui.QLabel("NaI dist"), 0, 2 )
        self.buttonlayout.addWidget( self.naidist, 0, 3 )
        self.buttonlayout.addWidget( QtGui.QLabel("NaI angle (deg)"), 0, 4 )
        self.buttonlayout.addWidget( self.naiangle, 0, 5 )
        self.buttonlayout.addWidget( QtGui.QLabel("Source dist"), 0, 6 )
        self.buttonlayout.addWidget( self.sourcedist, 0, 7 )
        self.buttonlayout.addWidget( QtGui.QLabel("Source angle (deg)"), 0, 8 )
        self.buttonlayout.addWidget( self.sourceangle, 0, 9 )
        self.buttonlayout.addWidget( QtGui.QLabel("PMT dist"), 0, 10 )
        self.buttonlayout.addWidget( self.pmtplanedist, 0, 11 )
        self.buttonlayout.addWidget(self.sim,0,12)

        self.sim.clicked.connect( self.runMCcompton )

        # visualization items
        self.gnai = gl.GLScatterPlotItem()
        self.gvial = gl.GLScatterPlotItem()
        self.gsrc = gl.GLScatterPlotItem()
        self.vis.addItem( self.gnai )
        self.vis.addItem( self.gvial )
        self.vis.addItem( self.gsrc )        

        self.gedir = gl.GLLinePlotItem()
        self.vis.addItem( self.gedir )
        self.gring = gl.GLScatterPlotItem()
        self.vis.addItem( self.gring )

        self.plt_pmtplane = gl.GLLinePlotItem()
        self.vis.addItem( self.plt_pmtplane )

        self.runMCcompton()
        
    def runMCcompton( self ):
        nthrows = int(self.nthrows.text())
        naidist = float(self.naidist.text())
        naiangle = float(self.naiangle.text())
        sourcedist = float(self.sourcedist.text())
        sourceangle = float(self.sourceangle.text())
        pmtplanedist = float(self.pmtplanedist.text())

        eventData = runMC( nthrows, naidist, naiangle, sourcedist, sourceangle, pmtplanedist, vis=self.vis )
        self.drawEvent( eventData )

    def drawVial( self ):
        self.vialpts = np.zeros( (24,3) )
        # top

    def drawEvent( self, data ):
        
        # draw hits in vial and NaI detector
        self.gnai.setData( pos=data.NaIhit, color=(1,1,1,.3), size=0.5, pxMode=False )
        self.gvial.setData( pos=data.vialhit, color=(1,1,1,.3), size=0.2, pxMode=False)
        
        # draw source
        sourcedist = float(self.sourcedist.text())
        sourceangle = float(self.sourceangle.text())
        csrc = np.cos( sourceangle*np.pi/180.0 )
        ssrc = np.sin( sourceangle*np.pi/180.0 )
        srcpos = np.asarray( ( csrc*sourcedist, -ssrc*sourcedist, 0.0  ), dtype=np.float )
        srcarr = np.empty( (1,3) )
        srcarr[0,:] = srcpos[:]
        self.gsrc.setData( pos=srcarr, color=(0,1,0,1), size=2.0, pxMode=False)
        
        # generate points on cherenkov ring
        pmtplanedist = float(self.pmtplanedist.text())
        pmtplanewidth = 2.54*10.0
        ptsperring = 20
        ringpts = np.zeros( (100*data.nthrows,3) )
        lines = np.zeros( (2*data.nthrows,3) )
        zdir = np.asarray( (0.0, 0.0, 1.0), dtype=np.float )
        me = 511.0 # mass of electron, keV
        for n in range(0,data.nthrows):
            lines[2*n,:] = data.vialhit[n,:]
            lines[2*n+1,:] = data.vialhit[n,:] + 2.0*data.electron_dir[n,:]

            beta = 0.5*np.sqrt(data.electron_energy[n]*data.electron_energy[n] - me*me)/me
            costheta = 1.0/beta/1.5
            sinth = np.sqrt(1.0-costheta*costheta)
            #print "Electron ",n,": E=",Ee[n]," beta=",beta
            for pt in range(0,ptsperring):
                # throw phi
                phi = np.random.random()*2.0*np.pi
                # define coordinates of cherenkov cone
                # globalz+ = x+
                e1 = data.electron_dir[n]
                j = np.cross( e1, zdir ) # y+
                # calc cherenkov photon dir
                cdir = costheta*e1 + (sinth*np.cos(phi))*zdir + (sinth*np.sin(phi))*j
                # calc intersection with plane
                if cdir[0]!=0.0:
                    s1 = (-pmtplanedist-data.vialhit[n,0])/cdir[0]
                    ringpts[ptsperring*n+pt,:] = data.vialhit[n,:] + s1*cdir
        self.gedir.setData( pos=lines,color=(0,0,255,255),width=1.0,mode='lines' )
        self.gring.setData( pos=ringpts, color=(1,0,0,1), size=0.1, pxMode=False)

        # draw pmtplane
        pmtplanepts = np.zeros( (5,3) )
        pmtplanepts[0,:] = np.asarray( (-pmtplanedist,pmtplanewidth,pmtplanewidth) )
        pmtplanepts[1,:] = np.asarray( (-pmtplanedist,pmtplanewidth,-pmtplanewidth) )
        pmtplanepts[2,:] = np.asarray( (-pmtplanedist,-pmtplanewidth,-pmtplanewidth) )
        pmtplanepts[3,:] = np.asarray( (-pmtplanedist,-pmtplanewidth,pmtplanewidth) )
        pmtplanepts[4,:] = np.asarray( (-pmtplanedist,pmtplanewidth,pmtplanewidth) )
        self.plt_pmtplane.setData( pos=pmtplanepts,color=(255,255,255,255),width=1.0 )

