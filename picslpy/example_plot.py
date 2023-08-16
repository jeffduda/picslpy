import SimpleITK as sitk
import numpy as np
import itk
import vtk
import utilities as util

def capture(r_win, f_name):
    writer=vtk.vtkPNGWriter()
    win2img = vtk.vtkWindowToImageFilter()
    win2img.SetInput(r_win)
    win2img.Update()
    #png_img = win2img.GetOutput()

    writer.SetInputConnection(win2img.GetOutputPort())
    writer.SetFileName(f_name)
    writer.Write()

img = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP.nii")
img = sitk.IntensityWindowing(img, -120, 180, 0.0, 255.0)

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


range = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/range.nii.gz")
v_range = util.image2vtk(range)
range_mesh = util.smooth_mesh(util.label2mesh(v_range, 1), relaxation=0.3)

liver = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_liver.nii.gz")
v_liver = util.image2vtk(liver)
liver_mesh = util.smooth_mesh(util.label2mesh(v_liver, 1), relaxation=0.5)
v_bounds = v_liver.GetBounds()
y_range = bounds[3]-bounds[2]

spleen = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_spleen.nii.gz")
v_spleen = util.image2vtk(spleen)
spleen_mesh = util.smooth_mesh(util.label2mesh(v_spleen, 1), relaxation=0.5)

fats = sitk.ReadImage("/Users/jtduda/53051586/processed/2_AX_NC_5_0_THICK_AP/2_AX_NC_5_0_THICK_AP_fats.nii.gz")

visceral = fats==1
subq = fats==2

v_visceral = util.image2vtk(visceral)
visceral_mesh = util.smooth_mesh(util.label2mesh(v_visceral, 1), relaxation=0.3)
v_subq = util.image2vtk(subq)
subq_mesh = util.smooth_mesh(util.label2mesh(v_subq, 1), relaxation=0.3)

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

visceral_mapper = vtk.vtkPolyDataMapper()
visceral_mapper.SetInputData(visceral_mesh)
visceral_mapper.ScalarVisibilityOff()
visceral_actor = vtk.vtkActor()
visceral_actor.SetMapper(visceral_mapper)
visceral_actor.GetProperty().SetColor(120/255,94/255,240/255)
visceral_actor.GetProperty().SetOpacity(0.3)

subq_mapper = vtk.vtkPolyDataMapper()
subq_mapper.SetInputData(subq_mesh)
subq_mapper.ScalarVisibilityOff()
subq_actor = vtk.vtkActor()
subq_actor.SetMapper(subq_mapper)
subq_actor.GetProperty().SetColor(254/255,176/255,1/255)
subq_actor.GetProperty().SetOpacity(0.3)


v_img = util.image2vtk(img)
v_bounds = v_img.GetBounds()
center = [bounds[0]+(bounds[1]-bounds[0])/2, 
          bounds[2]+(bounds[3]-bounds[2])/2, 
          bounds[4]+(bounds[5]-bounds[4])/2]
# Matrices for axial, coronal, sagittal, oblique view orientations
axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1, 0, 0, center[0],
                0, 1, 0, center[1],
                0, 0, 1, center[2],
                0, 0, 0, 1))

coronal = vtk.vtkMatrix4x4()
coronal.DeepCopy((1, 0, 0, center[0],
                  0, 0, 1, center[1],
                  0,-1, 0, center[2],
                  0, 0, 0, 1))

sagittal = vtk.vtkMatrix4x4()
sagittal.DeepCopy((0, 0,-1, center[0],
                   1, 0, 0, center[1],
                   0,-1, 0, center[2],
                   0, 0, 0, 1))


# Extract a slice in the desired orientation
reslice = vtk.vtkImageReslice()
reslice.SetInputData(v_img)
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(sagittal)
reslice.SetInterpolationModeToLinear()



#slice_actor = vtk.vtkImageActor()
#slice_actor.GetMapper().SetInputConnection(color.GetOutputPort())

print("Image Bounds")
print(v_img.GetBounds())
#print("Slice Bounds")
#print(slice_actor.GetBounds())

# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(0, 255) # image intensity range
#table.SetRange(-120,180)
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0.0) # no color saturation
table.SetRampToLinear()
table.Build()

color = vtk.vtkImageMapToColors()
color.SetLookupTable(table)
color.SetInputData(v_img)

vm = vtk.vtkImageSliceMapper()
vm.SetInputData(v_img)
#vm.SetInputConnection(color.GetOutputPort())
vm.SetOrientationToY()
vm.SetSliceNumber(img.GetSize()[1]//2)

slice_actor2 = vtk.vtkImageActor()
slice_actor2.SetMapper(vm)
slice_actor2.GetProperty().SetOpacity(0.0)



actors = [liver_actor, spleen_actor, visceral_actor, subq_actor, slice_actor2]

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()

renderWindow.AddRenderer(renderer)



for actor in actors:
    #actor.SetOrigin(center)
    #actor.RotateX(90)
    #actor.RotateY(180)
    #actor.RotateX(-2)

    renderer.AddActor(actor)

renderer.SetBackground(1, 1, 1)
renderer.ResetCamera()
cam = renderer.GetActiveCamera()
#cam.SetFocalPoint(center)
#cam.Zoom(2)

renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)


renderWindow.SetSize(512,512)
renderWindow.Render()
renderWindow.SetWindowName("JabbaAI Segmentation")

print("center")
print(center)

renderWindow.SetOffScreenRendering(0)
#renderWindowInteractor.Initialize()
cam.SetFocalPoint(center)
init_pos = cam.GetPosition()
print("Init Position")
print(init_pos)
print(cam.GetFocalPoint())

#renderWindowInteractor.Start()

print("Exit position")
print(cam.GetPosition())


renderWindow.SetOffScreenRendering(1)
renderer.ResetCamera()
cam.SetFocalPoint(center)
cam.Zoom(2)
cam_pos = center.copy()
cam_pos[2] = bounds[5] + 1400
cam_pos[1] = center[1] + 100

cam.SetPosition(cam_pos)
renderWindow.Render()
capture(renderWindow, "/Users/jtduda/test_above.png")
print("Above position")
print(cam.GetPosition())
print(cam.GetOrientation())

cam_pos[2] = bounds[5] - 1600
cam.SetPosition(cam_pos)
renderWindow.Render()
capture(renderWindow, "/Users/jtduda/test_below.png")
print("Below position")
print(cam.GetPosition())
print(cam.GetOrientation())

renderer.ResetCamera()
cam_pos = center.copy()
#cam_pos[2] = center[2] + 100
cam_pos[1] = bounds[2] - 1400
print("Set Position")
print(cam_pos)
cam.SetPosition(cam_pos)
cam.Zoom(1.5)
renderWindow.Render()

capture(renderWindow, "/Users/jtduda/test_back.png")
print("Back position")
print(cam.GetPosition())
print(cam.GetOrientation())

cam_pos[1] = bounds[3] + 1400
print("Set Position")
print(cam_pos)
cam.SetPosition(cam_pos)
cam.Roll(180)
renderWindow.Render()

capture(renderWindow, "/Users/jtduda/test_front.png")
print("Front position")
print(cam.GetPosition())
print(cam.GetOrientation())


#renderWindow.SetOffScreenRendering(0)
#renderWindowInteractor.Start()

#writer=vtk.vtkPNGWriter()
#win2img = vtk.vtkWindowToImageFilter()
##win2img.SetInput(renderWindow)
#win2img.Update()
#png_img = win2img.GetOutput()

#writer.SetInputConnection(win2img.GetOutputPort())
#writer.SetFileName("/Users/jtduda/test_above.png")
#writer.Write()



del renderWindowInteractor, renderWindow, renderer


# exec(open("example_plot.py").read())