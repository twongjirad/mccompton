import numpy as np

def drawFromVial( center, height, width ):
    """
    vial modeled as box. this generates a random position inside the box
    """
    z = height*2.0*(np.random.random()-0.5) + center[2]
    x = width*2.0*(np.random.random()-0.5) + center[0]
    y = width*2.0*(np.random.random()-0.5) + center[1]
    return np.asarray( (x,y,z), dtype=np.float )
    

def drawFromNaI( center_dist, radius, thickness, angle ):
    """
    NaI detector modeled as cylinder. 
    generates point inside detector via sampling in box and keeping only that within bounds.
    local coordinates: starts on x+ facing x- of global coordinates
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

