import bmesh
from bmesh.types import BMesh, BMVert, BMEdge, BMFace

'''
BMElemWrapper wraps BMverts, BMEdges, BMFaces to automagically handle
world-to-local and local-to-world transformations.

Must override any property that can be set (TODO: find more elegant
way to handle this!) and function that returns a BMVert, BMEdge, or
BMFace.  All functions and read-only properties are handled with
__getattr__().

user-writable properties:

    BMVert: co, normal
    BMEdge: seam, smooth
    BMFace: material_index, normal, smooth
    common: hide, index. select, tag

NOTE: RFVert, RFEdge, RFFace do NOT mark RFMesh as dirty!
'''


class BMElemWrapper:
    @staticmethod
    def wrap(rftarget):
        BMElemWrapper.rftarget   = rftarget
        BMElemWrapper.xform      = rftarget.xform
        BMElemWrapper.l2w_point  = rftarget.xform.l2w_point
        BMElemWrapper.w2l_point  = rftarget.xform.w2l_point
        BMElemWrapper.l2w_normal = rftarget.xform.l2w_normal
        BMElemWrapper.w2l_normal = rftarget.xform.w2l_normal
    
    def __init__(self, bmelem):
        self.bmelem = bmelem
    
    def __repr__(self):
        return '<BMElemWrapper: %s>' % repr(self.bmelem)
    def __hash__(self):
        return self.bmelem.__hash__()
    def __eq__(self, other):
        return other and self.bmelem == other.bmelem
    
    @property
    def hide(self): return self.bmelem.hide
    @hide.setter
    def hide(self, v): self.bmelem.hide = v
    
    @property
    def index(self): return self.bmelem.index
    @index.setter
    def index(self, v): self.bmelem.index = v
    
    @property
    def select(self): return self.bmelem.select
    @select.setter
    def select(self, v): self.bmelem.select = v
    
    @property
    def tag(self): return self.bmelem.tag
    @tag.setter
    def tag(self, v): self.bmelem.tag = v
    
    def __getattr__(self, k):
        if k in self.__dict__:
            return getattr(self, k)
        return getattr(self.bmelem, k)


class RFVert(BMElemWrapper):
    @property
    def co(self): return self.l2w_point(self.bmelem.co)
    @co.setter
    def co(self, co): self.bmelem.co = self.w2l_point(co)
    
    @property
    def normal(self): return self.l2w_normal(self.bmelem.normal)
    
    @normal.setter
    def normal(self, norm): self.bmelem.normal = self.w2l_normal(norm)
    
    @property
    def link_edges(self):
        return [RFEdge(bme) for bme in self.bmelem.link_edges]
    
    @property
    def link_faces(self):
        return [RFFace(bmf) for bmf in self.bmelem.link_faces]


class RFEdge(BMElemWrapper):
    @property
    def seam(self): return self.bmelem.seam
    @seam.setter
    def seam(self, v): self.bmelem.seam = v
    
    @property
    def smooth(self): return self.bmelem.smooth
    @smooth.setter
    def smooth(self, v): self.bmelem.smooth = v
    
    def other_vert(self, bmv):
        if type(bmv) is RFVert: bmv = bmv.bmelem
        o = self.bmelem.other_vert(bmv)
        if o is None: return None
        return RFVert(bmv)
    
    @property
    def verts(self):
        bmv0,bmv1 = self.bmelem.verts
        return (RFVert(bmv0), RFVert(bmv1))
    
    @property
    def link_faces(self):
        return [RFFace(bmf) for bmf in self.bmelem.link_faces]


class RFFace(BMElemWrapper):
    @property
    def material_index(self): return self.bmelem.material_index
    @material_index.setter
    def material_index(self, v): self.bmelem.material_index = v
    
    @property
    def normal(self): return self.l2w_normal(self.bmelem.normal)
    @normal.setter
    def normal(self, v): self.bmelem.normal = self.w2l_normal(v)
    
    @property
    def smooth(self): return self.bmelem.smooth
    @smooth.setter
    def smooth(self, v): self.bmelem.smooth = v
    
    @property
    def edges(self):
        return [RFEdge(bme) for bme in self.bmelem.edges]
    
    @property
    def verts(self):
        return [RFVert(bmv) for bmv in self.bmelem.verts]
