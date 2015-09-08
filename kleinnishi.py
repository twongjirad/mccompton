import os,sys

alpha = 1.0/137.04
rc = 0.38616 # pm
me = 511.0 # keV

def getDiffXsec( energy_kev, costh ):

    Pratio = 1.0/( 1 + (energy_kev/m)*(1-costh) )
    dsigmadomega = alpha*alpha*rc*rc*Pratio*Pratio*( Pratio + 1.0/Pratio - 1.0 + costh*costh )/2.0

    return dsigmadomega # units of pm^2 = 10^-24
