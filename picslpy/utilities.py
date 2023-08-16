import SimpleITK as sitk
import numpy as np
import itk
import vtk
from vtkmodules.util import vtkImageImportFromArray

def image2vtk(img, as_port=False):
    '''
    Convert an image from SimpleITK, ITK, or ANTs to a VTK image

    Inputs:
    img - SimpleITK image, ITK image, or ANTs image
    as_port - if True, return a VTK image port instead of a VTK image

    Outputs:
    VTK image or VTK port
    '''

    # SimpleITK -> VTK
    if isinstance(img, sitk.Image):
        return(sitk2vtk(img, as_port=as_port))

    # ITK -> VTK
    if isinstance(img, itk.Image):
        return(itk2vtk(img, as_port=as_port))

    # ANTs -> VTK


    raise TypeError("Input image must be one of: SimpleITK | ITK | ANTs")

def sitk2vtk(img: sitk.Image, as_port=False, rescale=False):
    '''
    Convert an image from SimpleITK

    Inputs:
    img - SimpleITK image
    as_port - if True, return a VTK image port instead of a VTK image

    Outputs:
    VTK image or VTK port
    '''

    uimg=None

    if rescale:
        uimg = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)
    else:
        uimg = sitk.Cast(img, sitk.sitkUInt8)

    data = sitk.GetArrayFromImage(uimg)
    imp = vtkImageImportFromArray.vtkImageImportFromArray()
    imp.SetArray(data)
    imp.SetDataSpacing(img.GetSpacing())
    imp.SetDataOrigin(img.GetOrigin())
    imp.Update()
    if as_port:
        return( imp.GetOutputPort() )

    # How to set when returning port?
    vimg = imp.GetOutput()
    vimg.SetDirectionMatrix(img.GetDirection())
    return(vimg)

# FIXME - switch to itk 
def itk2vtk(img: itk.Image, as_port=False):
    uimg = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)
    data = sitk.GetArrayFromImage(uimg)
    imp = vtkImageImportFromArray.vtkImageImportFromArray()
    imp.SetArray(data)
    imp.SetDataSpacing(img.GetSpacing())
    imp.SetDataOrigin(img.GetOrigin())
    
    imp.Update()
    if as_port:
        return( imp.GetOutputPort() )

    return( imp.GetOutput())

def label2mesh( img, label, as_port=False ):

    dmc = vtk.vtkDiscreteMarchingCubes()
    if isinstance(img, vtk.vtkImageData):
        dmc.SetInputData(img)
    else:
        dmc.SetInputConnection(img)

    dmc.GenerateValues(1, 1, 1)
    dmc.Update()

    if as_port:
        return(dmc.GetOutputPort())
    return(dmc.GetOutput())


def smooth_mesh(mesh, as_port=False, relaxation=0.1, iterations=50, feature_edge_smoothing=False, boundary_smoothing=True):

    smoother = vtk.vtkSmoothPolyDataFilter()
    if isinstance(mesh, vtk.vtkPolyData):
        smoother.SetInputData(mesh)
    else:
        smoother.SetInputConnection(mesh)

    smoother.SetNumberOfIterations(iterations)
    smoother.SetRelaxationFactor(relaxation)
    smoother.SetFeatureEdgeSmoothing(feature_edge_smoothing)
    smoother.SetBoundarySmoothing(boundary_smoothing)
    smoother.Update()
    
    if as_port:
        return(smoother.GetOutputPort())
    return(smoother.GetOutput())



