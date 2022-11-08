# Based on "Weaving patterns inspired by the pentagon snub subdivision scheme"
# Henriette Lipshutz, Ulrich Reitebuch, Martin Skrodzki & Konrad Polthier 
# https://www.tandfonline.com/doi/full/10.1080/17513472.2022.2069417

import math
add_library('svg')

class Mesh:
   
    def __init__(self):
        self.coords = []  # (x, y) values
        # self.lines = []   # (a, b) a and b are indices into self.coords
        self.poly = []    # A list of polygons.  Each is a list of vertices, given as coord index
        self.new_paths = {}
        self.middle_z = []
        
        # Maps edge (a, b) to a set of adjacent polygons 
        # Edge is specified as a list of to coord indices, with lowest value first.
        # Polygons are specified by index into self.poly.
        self.edge_to_poly = None 
        
        # Generated by self.combine()
        # self.octogons = []
        # self.edge_pentagons = [] 
                
    @classmethod
    def n_gon(cls, n_vertices=5):
        mesh = cls()
        
        mesh.coords = []  # (x, y) values
        # self.lines = []   # (a, b) a and b are indices into self.coords
        mesh.poly = []    # A list of coords (a, b) that are vertices
        
        for poly_id in range(1):
            vertices = []
            for n in range(n_vertices):
                theta = n * 2.0*math.pi/n_vertices
                x = cos(theta)
                y = sin(theta)
                mesh.coords.append((x, y))
                
                # self.lines.append((n, (n+1)%n_vertices))
                vertices.append(n)
                
            # Add this polygon to the set
            mesh.poly.append(vertices)

        return mesh  
    
    def fillpoly(self, poly):
        beginShape()
        for v in self.poly[poly]:
            vertex(self.coords[v][0], self.coords[v][1])
        endShape(CLOSE)     
 
    def draw(self):
        translate(width/2, height/2)
        scale(height/2.1, -height/2.1)
        strokeWeight(0.003)
        
        segments = {}  
    
        stroke(0xff000000)
        for poly in self.poly:
            n = 0
            x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
            last_vertex = 0
            for vrtx in poly:
                x2, y2 = self.coords[vrtx]
                if n > 1:
                    # Draw a line
                    # line(x1, y1, x2, y2)
                    
                    # Add a line to segments (maybe)
                    segments[(last_vertex, vrtx)] = True
                        
                n += 1
                x1 = x2
                y1 = y2
                last_vertex = vrtx
                
            # draw last line closing back to the start
            vrtx = poly[0]
            x2, y2 = self.coords[poly[0]]
            segments[(last_vertex, vrtx)] = True
            # line(x1, y1, x2, y2)

        seg_list = segments.keys()            
        seg_list.sort()
        for p1, p2 in seg_list:
            if ((p1, p2) not in self.middle_z) and ((p2, p1) not in self.middle_z):
                x1, y1 = self.coords[p1]
                x2, y2 = self.coords[p2]
                line(x1, y1, x2, y2)
            
        # stroke(0xffffffff)
        # for (p1, p2) in self.middle_z:
        #     x1, y1 = self.coords[p1]
        #     x2, y2 = self.coords[p2]
        #     line(x1, y1, x2, y2)
        #     # print("z center", x1, y1, x2, y2)
            
        # fill(0xff808080)
        
        # for p in range(4):
            # self.fillpoly(p)
            
    def write(self):
        pass
            
    def barycenter(self, poly):        
        # compute Barycenter
        n = 0
        cx = 0.0
        cy = 0.0
        for vertex in poly:
            n += 1
            cx += self.coords[vertex][0]
            cy += self.coords[vertex][1]
        cx /= n
        cy /= n
        return (cx, cy)
            
    # split line from p1 to p2 into three segments, with included angle theta
    def split_line(self, p1, p2, theta=2.0*math.pi/3.0):
        if (p1, p2) in self.new_paths:
            # It's already done!
            return
        
        # Get x, y of endpoints of this segment
        p1x, p1y = self.coords[p1]
        p2x, p2y = self.coords[p2]
        
        # len: distance from p1 to p2
        length = dist(p1x, p1y, p2x, p2y)
        # phi: orientation of line from p1 to p2
        phi = atan2(p2y-p1y, p2x-p1x)
        # len_seg: length of one of the three segments
        len_seg = math.sqrt(length*length/(5-4*math.cos(theta)))
        
        ratio = 2.0*math.sin(theta)/length
        alpha = math.asin(ratio*len_seg/2.0)
        dy = len_seg*math.sin(alpha)
        dx = len_seg*math.cos(alpha)
        
        p3x = p1x + dx*cos(phi) - dy*sin(phi)
        p3y = p1y + dx*sin(phi) + dy*cos(phi)
        p4x = p2x - dx*cos(phi) + dy*sin(phi)
        p4y = p2y - dx*sin(phi) - dy*cos(phi)
        
        self.coords.append((p3x, p3y))
        p3 = len(self.coords)-1
        self.coords.append((p4x, p4y))
        p4 = len(self.coords)-1
        
        (a, b, c, d) = (p1, p3, p4, p2)
        self.middle_z.append((b, c))
        # self.middle_z.append((c, b))

        # Store this new path and it's reverse
        self.new_paths[(p1, p2)] = (a, b, c, d)
        self.new_paths[(p2, p1)] = (d, c, b, a)   
    
    def smooth(self):
        # vertex index -> polygon's it is included in.
        neighbors = {}
        
        # For each face:
        for poly in self.poly:
            # Get barycenter of this polygon
            (cx, cy) = self.barycenter(poly)

            # For each vertex of this face, add this barycenter to it's list
            for v in poly:
                if v in neighbors:
                    neighbors[v].append((cx, cy))
                else:
                    neighbors[v] = [(cx, cy),]
                
        # For each coordinate / vertex
        for v in neighbors:
            # If degree three or higher, move to average of neighboring barycenters
            if len(neighbors[v]) >= 3:
                center = [sum(x)/len(x) for x in zip(*neighbors[v])]
                self.coords[v] = center
    
    def refine(self):
        # new_mesh = Mesh()
        self.middle_z = []
        
        # Now for each polygon, generate N new polygons, one for each
        # original side.
        
        new_poly = []
        for poly in self.poly:
            # print "Working with polygon: ", poly
            (cx, cy) = self.barycenter(poly)
            
            # Add new point for center
            self.coords.append((cx, cy))
            # self.coords.append((cx, cy))
            cn = len(self.coords)-1
            # print "Generated center at ", cn
            
            # From each line, generate two new points
            n = 0
            p1 = 0
            for vertex_n in poly:
                p2 = vertex_n
                if n >= 1:
                    self.split_line(p1, p2)
                p1 = p2
                n += 1
            p2 = poly[0]
            self.split_line(p1, p2)
            
            # Generate new polygons from this one
            num_vertices = len(poly)
            for n in range(num_vertices):
                vertex = poly[n]
                prior = poly[(n + num_vertices - 1) % num_vertices]
                next = poly[(n + 1) % num_vertices]
                # print "Prior, vertex, next: ", prior, vertex, next
                lead_in = self.new_paths[(prior, vertex)]
                lead_out = self.new_paths[(vertex, next)]
                a = lead_in[1]
                b = lead_in[2]
                c = vertex
                d = lead_out[1]
                e = cn
                new_poly.append( (e, a, b, c, d) )
                            
        self.poly = new_poly
        
        # Perform smoothing operation
        self.smooth()
        
    def gen_edge_to_poly(self):
        edge_to_poly = {}
        for poly_id in range(len(self.poly)):
            vertices = self.poly[poly_id]
            for n in range(-1, len(vertices)-1, 1):
                a = vertices[n]
                b = vertices[n+1]
                if a < b:
                    k = (a, b)
                else:
                    k = (b, a)
            
            if k in edge_to_poly:
                edge_to_poly[k].append(poly_id)
            else:
                edge_to_poly[k] = [poly_id,]
                    
        self.edge_to_poly = edge_to_poly                    
        
    def combine(self):
        # Generate octogons
        
        # create mapping of edges to polygons
        self.gen_edge_to_poly()

        # Go through all middle_z edges
        # If edge is shared between two pentagons, add an octogon
        # If edge is unique to one pentagon, add to edge pentagons.
        
        pass
        
m = Mesh.n_gon(5)
REFINEMENTS = 5
page_w = 11
page_h = 8.5
svg_ppi = 96
do_svg = False
if do_svg:
    w = int(svg_ppi*page_w)
    h = int(svg_ppi*page_h)
else:
    w = 2000
    h = 1500

def setup():
    # SVG output
    # size(w, h, SVG, "output/pentagon-4.svg")
    # Screen output
    size(w, h)

    for n in range(REFINEMENTS):
        m.refine()
        m.combine()
        
def draw():        
    m.draw()
    if do_svg:
        exit()
    
    # m.write()

    
