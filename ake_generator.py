# Save by guido on 2021_12_08-09.13.33; build 6.14-2 2014_08_22-15.00.46 134497
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

# parameters
AKE_WIDTH = 80.6
AKE_LENGTH = 400
CORE_T = 2.50
SKIN_T = 0.5
Zmin = 334.7
Zmax = Zmin + AKE_WIDTH
Ymax = 95.6
Ymin = -12.4
Xmin = 12
Xmax = 273.4
small = 1

rivetCentre = [100.,-11.879769,375]
panelCorner = [73.375833,-12.379769,334.7]
def translate(offset):
    reference = [73.375833,-8.879769 - (2*SKIN_T + CORE_T) + offset,334.7]
    return tuple(reference)

mdb.openStep('C:/Users/guido/PycharmProjects/akeDamage/ULD Assembly_B40.step', 
    scaleFromFile=OFF)

mdl = mdb.models['Model-1']
mdl.PartFromGeometryFile(combine=False, dimensionality=
    THREE_D, geometryFile=mdb.acis, name='ER-1', type=DEFORMABLE_BODY)
mdl.PartFromGeometryFile(bodyNum=2, combine=False, 
    dimensionality=THREE_D, geometryFile=mdb.acis, name='ER-2', type=
    DEFORMABLE_BODY)

mdl.ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdl.sketches['__profile__'].rectangle(point1=(0.0, 0.0), point2=(80.6, 200.0))
mdl.Part(dimensionality=THREE_D, name='AKE_SKIN', type= DEFORMABLE_BODY)
mdl.parts['AKE_SKIN'].BaseSolidExtrude(depth=SKIN_T, sketch=
    mdl.sketches['__profile__'])
del mdl.sketches['__profile__']
mdl.ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdl.sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
                                        point2=(80.6, 200.0))
mdl.Part(dimensionality=THREE_D, name='AKE_CORE', type=DEFORMABLE_BODY)
mdl.parts['AKE_CORE'].BaseSolidExtrude(depth=CORE_T, sketch=
    mdl.sketches['__profile__'])
del mdl.sketches['__profile__']

mdl.rootAssembly.Instance(dependent=ON, name='ER-1', part= mdl.parts['ER-1'])
mdl.rootAssembly.Instance(dependent=ON, name='ER-2', part= mdl.parts['ER-2'])

mdl.rootAssembly.Instance(dependent=ON, name='AKE_CORE', part=mdl.parts['AKE_CORE'])
mdl.rootAssembly.Instance(dependent=ON, name='bAKE_SKIN', part=mdl.parts['AKE_SKIN'])
mdl.rootAssembly.Instance(dependent=ON, name='tAKE_SKIN', part=mdl.parts['AKE_SKIN'])

ra = mdl.rootAssembly
movable_instances = ['bAKE_SKIN','AKE_CORE','tAKE_SKIN']
offset_list = [0,SKIN_T,SKIN_T+CORE_T]
mdl.rootAssembly.DatumCsysByDefault(CARTESIAN)

def positionPart(inst, offset):
    mdl.rootAssembly.rotate(angle=-90.0,
                            axisDirection=(0.0, 1.0, 0.0),
                            axisPoint=(0.0, 0.0, 0.0),
                            instanceList=(inst, ))
    mdl.rootAssembly.rotate(angle=-90.0,
                            axisDirection=(0.0, 0.0, 1.0),
                            axisPoint=(0.0, 0.0, 0.0),
                            instanceList=(inst, ))
    mdl.rootAssembly.translate(instanceList=(inst, ),
                                vector=translate(offset))
d = dict(zip(movable_instances,offset_list))
for prt in d.items():
    print(prt)
    positionPart(prt[0], prt[1])
    mdl.rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
        mdl.rootAssembly.instances['ER-1'], ), instanceToBeCut=
        mdl.rootAssembly.instances[prt[0]], name=prt[0]+'_cut',
        originalInstances=SUPPRESS)
    mdl.rootAssembly.features['ER-1'].resume()

###################################
######## M A T E R I A L S ########

mdl.Material(name='aluminium 6061')
mdl.materials['aluminium 6061'].Density(table=((2700e-12, ), ))
mdl.materials['aluminium 6061'].Elastic(table=((70000.0, 0.3), ))
mdl.Material(name='steel')
mdl.materials['steel'].Density(table=((8000e-12, ), ))
mdl.materials['steel'].Elastic(table=((210000.0, 0.3), ))
mdl.Material(name='syntactic core')
mdl.materials['syntactic core'].Density(table=((1000e-12, ), ))
mdl.materials['syntactic core'].Elastic(table=((3500.0, 0.3), ))

mdl.Material(name='ake-ply')
mdl.materials['ake-ply'].Density(table=((2000e-12, ), ))
mdl.materials['ake-ply'].Elastic(table=((120000.0, 10000.0,
    5000.0, 0.3, 0.3, 0.3, 10000.0, 10000.0, 10000.0), ), type=
    ENGINEERING_CONSTANTS)
mdl.materials['ake-ply'].elastic.FailStress(table=((1000.0,
    600.0, 100.0, 200.0, 120.0, 1.0, 1000.0), ))
mdl.HomogeneousSolidSection(material='aluminium 6061', name='aluSec', thickness=None)
mdl.HomogeneousSolidSection(material='steel', name='steelSec', thickness=None)
mdl.HomogeneousSolidSection(material='syntactic core', name='syntacticSec', thickness=None)

mdl.parts['ER-1'].Set(cells=mdl.parts['ER-1'].cells, name='rivet')
mdl.parts['ER-2'].Set(cells=mdl.parts['ER-2'].cells, name='edgeRail')
mdl.parts['AKE_CORE_cut'].Set(cells=mdl.parts['AKE_CORE_cut'].cells, name='core')

mdl.parts['ER-1'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
                                                      region=mdl.parts['ER-1'].sets['rivet'],
                                                      sectionName='steelSec',
                                                      thicknessAssignment=FROM_SECTION)
mdl.parts['ER-2'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
                                                      region=mdl.parts['ER-2'].sets['edgeRail'],
                                                      sectionName='aluSec',
                                                      thicknessAssignment=FROM_SECTION)
mdl.parts['AKE_CORE_cut'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
                                                      region=mdl.parts['AKE_CORE_cut'].sets['core'],
                                                      sectionName='syntacticSec',
                                                      thicknessAssignment=FROM_SECTION)


#
# mdb.models['Model-1'].parts['bAKE_SKIN_cut'].CompositeLayup(description='',
#     elementType=CONTINUUM_SHELL, name='top_layup', symmetric=False)
# mdb.models['Model-1'].parts['bAKE_SKIN_cut'].compositeLayups['top_layup'].Section(
#     integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF,
#     temperature=GRADIENT, thicknessModulus=None, useDensity=OFF)
# mdb.models['Model-1'].parts['bAKE_SKIN_cut'].compositeLayups['top_layup'].ReferenceOrientation(
#     additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_2, fieldName='',
#     localCsys=None, orientationType=GLOBAL, stackDirection=STACK_3)
# mdb.models['Model-1'].parts['bAKE_SKIN_cut'].compositeLayups['top_layup'].CompositePly(
#     additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0
#     , axis=AXIS_3, material='ake-ply', numIntPoints=3, orientationType=
#     SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-1', region=Region(
#     cells=mdb.models['Model-1'].parts['bAKE_SKIN_cut'].cells.getSequenceFromMask(
#     mask=('[#1 ]', ), )), suppressed=False, thickness=1.0, thicknessType=
#     SPECIFY_THICKNESS)
# mdb.models['Model-1'].parts['bAKE_SKIN_cut'].compositeLayups['top_layup'].CompositePly(
#     additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0
#     , axis=AXIS_3, material='ake-ply', numIntPoints=3, orientationType=
#     SPECIFY_ORIENT, orientationValue=90.0, plyName='Ply-2', region=Region(
#     cells=mdb.models['Model-1'].parts['bAKE_SKIN_cut'].cells.getSequenceFromMask(
#     mask=('[#1 ]', ), )), suppressed=False, thickness=1.0, thicknessType=
#     SPECIFY_THICKNESS)
#
#
# mdb.models['Model-1'].parts['tAKE_SKIN_cut'].CompositeLayup(description='',
#     elementType=CONTINUUM_SHELL, name='top_layup', symmetric=False)
# mdb.models['Model-1'].parts['tAKE_SKIN_cut'].compositeLayups['top_layup'].Section(
#     integrationRule=SIMPSON, poissonDefinition=DEFAULT, preIntegrate=OFF,
#     temperature=GRADIENT, thicknessModulus=None, useDensity=OFF)
# mdb.models['Model-1'].parts['tAKE_SKIN_cut'].compositeLayups['top_layup'].ReferenceOrientation(
#     additionalRotationType=ROTATION_NONE, angle=0.0, axis=AXIS_2, fieldName='',
#     localCsys=None, orientationType=GLOBAL, stackDirection=STACK_3)
# mdb.models['Model-1'].parts['tAKE_SKIN_cut'].compositeLayups['top_layup'].CompositePly(
#     additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0
#     , axis=AXIS_3, material='ake-ply', numIntPoints=3, orientationType=
#     SPECIFY_ORIENT, orientationValue=90.0, plyName='Ply-1', region=Region(
#     cells=mdb.models['Model-1'].parts['tAKE_SKIN_cut'].cells.getSequenceFromMask(
#     mask=('[#1 ]', ), )), suppressed=False, thickness=1.0, thicknessType=
#     SPECIFY_THICKNESS)
# mdb.models['Model-1'].parts['tAKE_SKIN_cut'].compositeLayups['top_layup'].CompositePly(
#     additionalRotationField='', additionalRotationType=ROTATION_NONE, angle=0.0
#     , axis=AXIS_3, material='ake-ply', numIntPoints=3, orientationType=
#     SPECIFY_ORIENT, orientationValue=0.0, plyName='Ply-2', region=Region(
#     cells=mdb.models['Model-1'].parts['tAKE_SKIN_cut'].cells.getSequenceFromMask(
#     mask=('[#1 ]', ), )), suppressed=False, thickness=1.0, thicknessType=
#     SPECIFY_THICKNESS)
mdl.parts['bAKE_SKIN_cut'].Set(cells=
    mdl.parts['bAKE_SKIN_cut'].cells.getSequenceFromMask((
    '[#1 ]', ), ), name='bottomSet')

mdl.parts['tAKE_SKIN_cut'].Set(cells=
    mdl.parts['tAKE_SKIN_cut'].cells.getSequenceFromMask((
    '[#1 ]', ), ), name='topSet')
mdl.ExplicitDynamicsStep(name='Step-1', previous='Initial', timePeriod=0.05)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(timeInterval=
    0.0025)
minStepSize = 1e-7

mdb.models['Model-1'].steps['Step-1'].setValues(massScaling=((SEMI_AUTOMATIC, 
    mdb.models['Model-1'].rootAssembly.allInstances['ER-1'].sets['rivet'], 
    AT_BEGINNING, 0.0, minStepSize, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None),
    (SEMI_AUTOMATIC,mdb.models['Model-1'].rootAssembly.allInstances['ER-2'].sets['edgeRail'], 
    AT_BEGINNING, 0.0, minStepSize, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None),
    (SEMI_AUTOMATIC,mdb.models['Model-1'].rootAssembly.allInstances['AKE_CORE_cut-1'].sets['core'], 
    AT_BEGINNING, 0.0, minStepSize, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None),
    (SEMI_AUTOMATIC,mdb.models['Model-1'].rootAssembly.allInstances['tAKE_SKIN_cut-1'].sets['topSet'], 
    AT_BEGINNING, 0.0, minStepSize, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None),
    (SEMI_AUTOMATIC,mdb.models['Model-1'].rootAssembly.allInstances['bAKE_SKIN_cut-1'].sets['bottomSet'], 
    AT_BEGINNING, 0.0, minStepSize, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None), ))

mdl.CompositeShellSection(idealization=NO_IDEALIZATION,
    integrationRule=SIMPSON, layup=(SectionLayer(thickness=1.0,
    material='ake-ply', plyName='a'), SectionLayer(thickness=1.0,
    orientAngle=90.0, material='ake-ply', plyName='b')), name=
    'Composite SectionB', poissonDefinition=DEFAULT, preIntegrate=OFF,
    symmetric=False, temperature=GRADIENT, thicknessModulus=None,
    thicknessType=UNIFORM, useDensity=OFF)

mdl.parts['bAKE_SKIN_cut'].SectionAssignment(offset=0.0,
    offsetField='', offsetType=MIDDLE_SURFACE, region=
    mdl.parts['bAKE_SKIN_cut'].sets['bottomSet'], sectionName=
    'Composite SectionB', thicknessAssignment=FROM_SECTION)

mdl.CompositeShellSection(idealization=NO_IDEALIZATION,
    integrationRule=SIMPSON, layup=(SectionLayer(thickness=1.0,
    orientAngle=90.0, material='ake-ply', plyName='a'), SectionLayer(thickness=1.0,
    material='ake-ply', plyName='b')), name=
    'Composite SectionA', poissonDefinition=DEFAULT, preIntegrate=OFF,
    symmetric=False, temperature=GRADIENT, thicknessModulus=None,
    thicknessType=UNIFORM, useDensity=OFF)

mdl.parts['tAKE_SKIN_cut'].SectionAssignment(offset=0.0,
    offsetField='', offsetType=MIDDLE_SURFACE, region=
    mdl.parts['tAKE_SKIN_cut'].sets['topSet'], sectionName=
    'Composite SectionA', thicknessAssignment=FROM_SECTION)

##################################
############ T I E S #############

core_b_face_index = ra.instances['AKE_CORE_cut-1'].faces.findAt((panelCorner[0]+small,
                                                                     panelCorner[1]+SKIN_T,
                                                                     panelCorner[2]+small),).index
core_t_face_index = ra.instances['AKE_CORE_cut-1'].faces.findAt((panelCorner[0]+small,
                                                                     panelCorner[1]+CORE_T+SKIN_T,
                                                                     panelCorner[2]+small),).index
b_skin_t_face_index = ra.instances['bAKE_SKIN_cut-1'].faces.findAt((panelCorner[0]+small,
                                                                     panelCorner[1]+SKIN_T,
                                                                     panelCorner[2]+small),).index
t_skin_b_face_index = ra.instances['tAKE_SKIN_cut-1'].faces.findAt((panelCorner[0]+small,
                                                                     panelCorner[1]+CORE_T+SKIN_T,
                                                                     panelCorner[2]+small),).index


core_b_face = ra.Set(faces=ra.instances['AKE_CORE_cut-1'].faces[core_b_face_index:core_b_face_index+1],
                           name='core_b_face')
core_t_face = ra.Set(faces=ra.instances['AKE_CORE_cut-1'].faces[core_t_face_index:core_t_face_index+1],
                           name='core_t_face')
b_skin_t_face = ra.Set(faces=ra.instances['bAKE_SKIN_cut-1'].faces[b_skin_t_face_index:b_skin_t_face_index+1],
                             name='b_skin_t_face')
t_skin_b_face = ra.Set(faces=ra.instances['tAKE_SKIN_cut-1'].faces[t_skin_b_face_index:t_skin_b_face_index+1],
                             name='t_skin_b_face')


ra.Surface(name='core_b_surface', side1Faces=core_b_face.faces)
ra.Surface(name='core_t_surface', side1Faces=core_t_face.faces)
ra.Surface(name='b_skin_t_surface', side1Faces=b_skin_t_face.faces)
ra.Surface(name='t_skin_b_surface', side1Faces=t_skin_b_face.faces)


mdl.Tie(adjust=ON, master=ra.surfaces['core_b_surface'], name=
    'Constraint-1', positionToleranceMethod=COMPUTED, slave=
    ra.surfaces['b_skin_t_surface'], thickness=ON,
    tieRotations=ON)

mdl.Tie(adjust=ON, master=ra.surfaces['core_t_surface'], name=
    'Constraint-2', positionToleranceMethod=COMPUTED, slave=
    ra.surfaces['t_skin_b_surface'], thickness=ON,
    tieRotations=ON)

ra.regenerate()

###################################
#### B O U N D A R Y C O N D S ####
ra.Set(faces=ra.instances['ER-2'].faces.getByBoundingBox(
    Xmin-small, Ymin - small, Zmin-small,
        Xmax + small, Ymax+small, Zmin + small
    ), name='z min side ER-2')
ra.Set(faces=ra.instances['AKE_CORE_cut-1'].faces.getByBoundingBox(
    Xmin-small, Ymin - small, Zmin-small,
        Xmax + small, Ymax+small, Zmin + small
    ), name='z min side core')
ra.Set(faces=ra.instances['ER-2'].faces.getByBoundingBox(
    Xmin-small, Ymin - small, Zmax-small,
        Xmax + small, Ymax+small, Zmax + small
    ), name='z max side ER-2')
ra.Set(faces=ra.instances['AKE_CORE_cut-1'].faces.getByBoundingBox(
    Xmin-small, Ymin - small, Zmax-small,
        Xmax + small, Ymax+small, Zmax + small
    ), name='z max side core')


for set in mdl.rootAssembly.sets.items():
    if ('z max' in set[0] and "ER" in set[0]) or ('z min' in set[0] and "ER" in set[0]):
        mdl.ZsymmBC(createStepName='Initial', localCsys=None, name=
        'symmBC_{}'.format(set[0]), region=set[1])

ra.regenerate()

ra.Set(edges=
    ra.instances['ER-2'].edges.getSequenceFromMask(
    ('[#0:5 #8000 ]', ), ), name='Set-5')
mdl.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'BC-5', region=ra.sets['Set-5'], u1=0.0,
    u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=0.0)
mdb.models['Model-1'].rootAssembly.Set(faces=
    mdb.models['Model-1'].rootAssembly.instances['ER-2'].faces.getSequenceFromMask(
    ('[#0:2 #4 ]', ), ), name='Set-11')
mdb.models['Model-1'].boundaryConditions['BC-5'].setValues(region=
    mdb.models['Model-1'].rootAssembly.sets['Set-11'], ur1=0.0, ur2=0.0)
ra.regenerate()
mdb.models['Model-1'].TabularAmplitude(data=((0.0, 0.0), (0.01, 1.0)), name=
    'Amp-1', smooth=SOLVER_DEFAULT, timeSpan=STEP)
ra.regenerate()

endFace = ra.instances['AKE_CORE_cut-1'].faces.getByBoundingBox(
    273.37-small, -100, 375-AKE_WIDTH/2-small,
    273.37+small,  100,  375+AKE_WIDTH/2+small)
mdb.models['Model-1'].rootAssembly.Set(faces=
    endFace, name='coreEnd')
mdb.models['Model-1'].DisplacementBC(amplitude='Amp-1', createStepName='Step-1'
    , distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'disp', region=mdb.models['Model-1'].rootAssembly.sets['coreEnd'], u1=UNSET
    , u2=5.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET)

###################################
######### C O N T A C T S #########
mdb.models['Model-1'].ContactProperty('IntProp')
mdb.models['Model-1'].interactionProperties['IntProp'].TangentialBehavior(
    formulation=FRICTIONLESS)
mdb.models['Model-1'].interactionProperties['IntProp'].NormalBehavior(
    allowSeparation=ON, constraintEnforcementMethod=DEFAULT, 
    pressureOverclosure=HARD)
mdb.models['Model-1'].ContactExp(createStepName='Initial', name='GeneralContact')
mdb.models['Model-1'].interactions['GeneralContact'].includedPairs.setValuesInStep(
    stepName='Initial', useAllstar=ON)
mdb.models['Model-1'].interactions['GeneralContact'].contactPropertyAssignments.appendInStep(
    assignments=((GLOBAL, SELF, 'IntProp'), ), stepName='Initial')
###################################
######### M E S H I N G ###########
ra.regenerate()
mdl.parts['ER-1'].setMeshControls(elemShape=TET, regions=
    mdl.parts['ER-1'].cells, technique=FREE)
mdl.parts['ER-1'].setElementType(elemTypes=(ElemType(
    elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15,
    elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)),
    regions=(mdl.parts['ER-1'].cells,))

mdl.parts['ER-2'].PartitionCellByExtrudeEdge(cells=
    mdl.parts['ER-2'].cells.getSequenceFromMask(('[#1 ]', ),
    ), edges=(mdl.parts['ER-2'].edges[134], ), line=
    mdl.parts['ER-2'].edges[148], sense=REVERSE)

mdl.parts['ER-2'].setMeshControls(elemShape=TET, regions=
    mdl.parts['ER-2'].cells.getSequenceFromMask(('[#2 ]', ),
    ), technique=FREE)
mdl.parts['ER-2'].setElementType(elemTypes=(ElemType(
    elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15,
    elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)),
    regions=(mdl.parts['ER-2'].cells.getSequenceFromMask((
    '[#2 ]', ), ), ))
ra.regenerate()
mdl.parts['AKE_CORE_cut'].PartitionCellBySweepEdge(cells=
    mdl.parts['AKE_CORE_cut'].cells.getSequenceFromMask((
    '[#1 ]', ), ), edges=(mdl.parts['AKE_CORE_cut'].edges[0],
    ), sweepPath=mdl.parts['AKE_CORE_cut'].edges[8])
mdl.parts['AKE_CORE_cut'].setMeshControls(elemShape=TET,
    regions=
    mdl.parts['AKE_CORE_cut'].cells.getSequenceFromMask((
    '[#2 ]', ), ), technique=FREE)
mdl.parts['AKE_CORE_cut'].setElementType(elemTypes=(ElemType(
    elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15,
    elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)),
    regions=(
    mdl.parts['AKE_CORE_cut'].cells.getSequenceFromMask((
    '[#2 ]', ), ), ))
mdl.parts['AKE_CORE_cut'].seedPart(deviationFactor=0.1,
    minSizeFactor=0.1, size=1.0)
ra.regenerate()
parts_to_mesh = ["tAKE_SKIN_cut", "bAKE_SKIN_cut", "ER-2", "ER-1","AKE_CORE_cut"]
refineCoeff = 2
mdl.parts["ER-1"].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=3/refineCoeff)
mdl.parts["ER-2"].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=3/refineCoeff)
mdl.parts["bAKE_SKIN_cut"].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=5/refineCoeff)
mdl.parts["tAKE_SKIN_cut"].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=5/refineCoeff)
mdl.parts["AKE_CORE_cut"].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=8/refineCoeff)

mdl.parts['ER-1'].setElementType(elemTypes=(ElemType(
    elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT), ElemType(
    elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT), ElemType(elemCode=C3D10M,
    elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, distortionControl=DEFAULT)),
    regions=(mdl.parts['ER-1'].cells.getSequenceFromMask((
    '[#1 ]', ), ), ))

mdl.parts['ER-2'].setElementType(elemTypes=(ElemType(
    elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT), ElemType(
    elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT), ElemType(elemCode=C3D10M,
    elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, distortionControl=DEFAULT)),
    regions=(mdl.parts['ER-2'].cells.getSequenceFromMask((
    '[#2 ]', ), ), ))

mdl.parts['AKE_CORE_cut'].setElementType(elemTypes=(ElemType(
    elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT), ElemType(
    elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT), ElemType(elemCode=C3D10M,
    elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, distortionControl=DEFAULT)),
    regions=(
    mdl.parts['AKE_CORE_cut'].cells.getSequenceFromMask((
    '[#2 ]', ), ), ))

mdl.parts['bAKE_SKIN_cut'].setElementType(elemTypes=(
    ElemType(elemCode=SC8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF,
    hourglassControl=DEFAULT), ElemType(elemCode=SC6R, elemLibrary=EXPLICIT),
    ElemType(elemCode=UNKNOWN_TET, elemLibrary=EXPLICIT)), regions=(
    mdl.parts['bAKE_SKIN_cut'].cells.getSequenceFromMask((
    '[#1 ]', ), ), ))

mdl.parts['tAKE_SKIN_cut'].setElementType(elemTypes=(
    ElemType(elemCode=SC8R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF,
    hourglassControl=DEFAULT), ElemType(elemCode=SC6R, elemLibrary=EXPLICIT),
    ElemType(elemCode=UNKNOWN_TET, elemLibrary=EXPLICIT)), regions=(
    mdl.parts['tAKE_SKIN_cut'].cells.getSequenceFromMask((
    '[#1 ]', ), ), ))
for prt in parts_to_mesh:
    print('Generating {}'.format(prt[0]))
    mdl.parts[prt].generateMesh()
    ra.regenerate()


# mdl.rootAssembly.InstanceFromBooleanMerge(domain=MESH,
#     instances=(mdl.rootAssembly.instances['bAKE_SKIN_cut-1'],
#     mdl.rootAssembly.instances['AKE_CORE_cut-1'],
#     mdl.rootAssembly.instances['tAKE_SKIN_cut-1']),
#     mergeNodes=ALL, name='basepanel', nodeMergingTolerance=1e-04,
#     originalInstances=SUPPRESS)


mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF,
    description='', echoPrint=OFF, explicitPrecision=SINGLE, historyPrint=OFF,
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF,
    multiprocessingMode=DEFAULT, name='Job-1', nodalOutputPrecision=SINGLE,
    numCpus=10, numDomains=10, parallelizationMethodExplicit=DOMAIN, queue=None
    , resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='',
    waitHours=0, waitMinutes=0)

mdb.jobs['Job-1'].submit(consistencyChecking=OFF)



mdb.saveAs(pathName='C:/Users/guido/PycharmProjects/akeDamage/wd/testbed.cae')
