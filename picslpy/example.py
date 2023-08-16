import SimpleITK as sitk
import numpy as np
import itk
import vtk
import utilities as util
from vtkmodules.vtkCommonColor import vtkNamedColors

img = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP.nii")
#sitk.WriteImage(img, "/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/orig.mha")

min_bounds = img.TransformIndexToPhysicalPoint((0,0,0))
max_bounds = img.TransformIndexToPhysicalPoint((img.GetWidth()-1,img.GetHeight()-1,img.GetDepth()-1))
bounds = [min_bounds[0], max_bounds[0], min_bounds[1], max_bounds[1], min_bounds[2], max_bounds[2]]

arr = sitk.GetArrayFromImage(img)
fimg = sitk.GetImageFromArray(np.flip(arr,1))
fimg.SetSpacing(img.GetSpacing())
og = list(img.GetOrigin())
og[1] = min([min_bounds[1], max_bounds[1]])
fimg.SetOrigin(og)
fimg.SetDirection(img.GetDirection())
#sitk.WriteImage(fimg, "/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/flipped.mha")


range = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/range.nii.gz")
v_range = util.image2vtk(range)
range_mesh = util.smooth_mesh(util.label2mesh(v_range, 1), relaxation=0.3)

liver = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_liver.nii.gz")
v_liver = util.image2vtk(liver)
liver_mesh = util.smooth_mesh(util.label2mesh(v_liver, 1), relaxation=0.3)
v_bounds = v_liver.GetBounds()
y_range = bounds[3]-bounds[2]

spleen = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_spleen.nii.gz")
v_spleen = util.image2vtk(spleen)
spleen_mesh = util.smooth_mesh(util.label2mesh(v_spleen, 1), relaxation=0.3)

fats = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_fats.nii.gz")
visceral = fats==1
subq = fats==2

v_visceral = util.image2vtk(visceral)
visceral_mesh = util.smooth_mesh(util.label2mesh(v_visceral, 1), relaxation=0.3)
v_subq = util.image2vtk(subq)
subq_mesh = util.smooth_mesh(util.label2mesh(v_subq, 1), relaxation=0.3)

#writer = vtk.vtkPolyDataWriter()
#writer.SetInputData(liver_mesh)
#writer.SetFileName("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/liver_mesh_new.vtk")
#writer.Write()

#writer.SetInputData(spleen_mesh)
#writer.SetFileName("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/spleen_mesh_new.vtk")
#writer.Write()

#writer.SetInputData(visceral_mesh)
#writer.SetFileName("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/visceral_mesh_new.vtk")
#writer.Write()

#writer.SetInputData(subq_mesh)
#writer.SetFileName("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/subq_mesh_new.vtk")
#writer.Write()

#writer.SetInputData(range_mesh)
#writer.SetFileName("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/range_mesh.vtk")
#writer.Write()

colors = vtkNamedColors()

liver_mapper = vtk.vtkPolyDataMapper()
liver_mapper.SetInputData(liver_mesh)
liver_mapper.ScalarVisibilityOff()
liver_actor = vtk.vtkActor()
liver_actor.SetMapper(liver_mapper)
liver_actor.GetProperty().SetColor(230/255,38/255,127/255)

spleen_mapper = vtk.vtkPolyDataMapper()
spleen_mapper.SetInputData(spleen_mesh)
spleen_mapper.ScalarVisibilityOff()
spleen_actor = vtk.vtkActor()
spleen_actor.SetMapper(spleen_mapper)
spleen_actor.GetProperty().SetColor(220/255,97/255,1/255)

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.SetWindowName("JabbaAI Segmentation")
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

renderer.AddActor(liver_actor)
renderer.AddActor(spleen_actor)
renderer.SetBackground(1, 1, 1)
renderWindow.Render()
renderWindowInteractor.Start()
