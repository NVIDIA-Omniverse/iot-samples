import random
from pxr import Usd, Gf, UsdGeom, Sdf, UsdShade


class LiveCube:
    def __init__(self, stage: Usd.Stage):
        points = [
            (50, 50, 50),
            (-50, 50, 50),
            (-50, -50, 50),
            (50, -50, 50),
            (-50, -50, -50),
            (-50, 50, -50),
            (50, 50, -50),
            (50, -50, -50),
        ]
        faceVertexIndices = [0, 1, 2, 3, 4, 5, 6, 7, 0, 6, 5, 1, 4, 7, 3, 2, 0, 3, 7, 6, 4, 2, 1, 5]
        faceVertexCounts = [4, 4, 4, 4, 4, 4]

        cube = stage.GetPrimAtPath("/World/cube")
        if not cube:
            cube = stage.DefinePrim("/World/cube", "Cube")

        if not cube:
            raise Exception("Could load the cube: /World/cube.")

        self.mesh = stage.GetPrimAtPath("/World/cube/mesh")
        if not self.mesh:
            self.mesh = UsdGeom.Mesh.Define(stage, "/World/cube/mesh")
            self.mesh.CreatePointsAttr().Set(points)
            self.mesh.CreateFaceVertexIndicesAttr().Set(faceVertexIndices)
            self.mesh.CreateFaceVertexCountsAttr().Set(faceVertexCounts)
            self.mesh.CreateDoubleSidedAttr().Set(False)
            self.mesh.CreateSubdivisionSchemeAttr("bilinear")
            self.mesh.CreateDisplayColorAttr().Set([(0.463, 0.725, 0.0)])
            self.mesh.AddTranslateOp().Set(Gf.Vec3d(0.0))
            self.mesh.AddScaleOp().Set(Gf.Vec3f(0.8535))
            self.mesh.AddTransformOp().Set(Gf.Matrix4d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
            texCoords = UsdGeom.PrimvarsAPI(self.mesh).CreatePrimvar(
                "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.varying
            )
            texCoords.Set([(0, 0), (1, 0), (1, 1), (0, 1)])

        self._rotationIncrement = Gf.Vec3f(
            random.uniform(-1.0, 1.0) * 10.0, random.uniform(-1.0, 1.0) * 10.0, random.uniform(-1.0, 1.0) * 10.0
        )

        material = UsdShade.Material.Define(stage, '/World/Looks/Plastic_Yellow_A')
        if material:
            self.mesh.GetPrim().ApplyAPI(UsdShade.MaterialBindingAPI)
            UsdShade.MaterialBindingAPI(self.mesh).Bind(material)

        self._rotateXYZOp = None
        self._scale = None
        self._translate = None
        self.cube = UsdGeom.Xformable(cube)
        for op in self.cube.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
                self._rotateXYZOp = op
            if op.GetOpType() == UsdGeom.XformOp.TypeScale:
                self._scale = op
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                self._translate = op

        if self._rotateXYZOp is None:
            self._rotateXYZOp = self.cube.AddRotateXYZOp()
        self._rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        self._rotateXYZOp.Set(self._rotation)

    def translate(self, value: Gf.Vec3f):
        if self._translate is None:
            self._translate = self.cube.AddTranslateOp()
        self._translate.Set(value)

    def scale(self, value: Gf.Vec3f):
        if self._scale is None:
            self._scale = self.cube.AddScaleOp()
        self._scale.Set(value)

    def rotate(self):
        if abs(self._rotation[0] + self._rotationIncrement[0]) > 360.0:
            self._rotationIncrement[0] *= -1.0
        if abs(self._rotation[1] + self._rotationIncrement[1]) > 360.0:
            self._rotationIncrement[1] *= -1.0
        if abs(self._rotation[2] + self._rotationIncrement[2]) > 360.0:
            self._rotationIncrement[2] *= -1.0

        self._rotation[0] += self._rotationIncrement[0]
        self._rotation[1] += self._rotationIncrement[1]
        self._rotation[2] += self._rotationIncrement[2]
        self._rotateXYZOp.Set(self._rotation)
