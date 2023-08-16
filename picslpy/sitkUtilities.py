
import numpy as np
import SimpleITK as sitk

# SimpleITK DICOMOrient seems to output the opposite of is expected
def reorient_image(img, orient):
    map={"R":"L", "L":"R", "A":"P", "P":"A", "I":"S", "S":"I"}
    sorient = "".join([ map[x] for x in orient ])
    return(sitk.DICOMOrient(img, sorient))

def largest_connected_component(img):
    components = sitk.ConnectedComponent(img)
    sorted_components = sitk.RelabelComponent(components, sortByObjectSize=True)
    largest_component = sorted_components == 1
    return(largest_component)    

def largest_connected_component_per_label(img):
    labels = np.unique(sitk.GetArrayViewFromImage(img))
    labels = labels[labels!=0]

    outImg = img*0
    for l in labels:
        mask = sitk.BinaryThreshold(img, lowerThreshold=int(l), upperThreshold=int(l), insideValue=1, outsideValue=0)
        mask = largest_connected_component(mask)
        mask = mask*int(l)
        outImg = sitk.Add(outImg, mask)

    return(outImg)

def region_mask(img, size, index):
    mask = sitk.Image(img.GetSize(), sitk.sitkUInt8)
    mask.CopyInformation(img)
    mask[index[0]:(index[0]+size[0]-1), index[1]:(index[1]+size[1]-1), index[2]:(index[2]+size[2]-1)] = 1
    return(mask)

def resize_to_reference( img, reference, interpolation="Linear"):
    out_sp=reference.GetSpacing()
    out_sz=reference.GetSize()
    out_origin=reference.GetOrigin()
    out_dir=reference.GetDirection()

    resample = sitk.ResampleImageFilter()
    resample.SetSize( out_sz )
    resample.SetOutputSpacing( out_sp )
    resample.SetOutputOrigin( out_origin )
    resample.SetOutputDirection( out_dir )
    resample.SetTransform( sitk.Transform() )
    resample.SetDefaultPixelValue( 0 )

    if interpolation not in ["Linear","BSpline","NearestNeighbor"]:
        print("ERROR: unknown interpolation type:"+str(interpolation))
        return(None)

    if interpolation=="BSpline":
        resample.SetInterpolator( sitk.sitkBSpline )
    if interpolation=="NearestNeighbor":
        resample.SetInterpolator( sitk.sitkNearestNeighbor )

    return(resample.Execute(img))

def resize_image( img, outSize, outSpacing=None, outOrigin=None, interpolation="Linear" ):
    Dimension = img.GetDimension()
    inSize = img.GetSize()
    inSpacing = img.GetSpacing()
    inOrigin = img.GetOrigin()

    if outSpacing is None:
        outSpacing = [ y*float(inSize[x])/float(outSize[x]) for x,y in enumerate(inSpacing) ]

    if outOrigin is None:
        outOrigin = inOrigin

    resample = sitk.ResampleImageFilter()
    resample.SetSize( outSize )
    resample.SetOutputSpacing( outSpacing )
    resample.SetOutputOrigin( outOrigin )
    resample.SetOutputDirection( img.GetDirection() )
    resample.SetTransform( sitk.Transform() )
    resample.SetDefaultPixelValue( img.GetPixelIDValue() )

    if interpolation not in ["Linear","BSpline","NearestNeighbor"]:
        print("ERROR: unknown interpolation type:"+str(interpolation))
        return(None)

    if interpolation=="BSpline":
        resample.SetInterpolator( sitk.sitkBSpline )
    if interpolation=="NearestNeighbor":
        resample.SetInterpolator( sitk.sitkNearestNeighbor )

    return(resample.Execute(img))

def shift_scale_image(img, shift=0, scale=1, masked=False):
    out_img = sitk.ShiftScale(img, shift=shift, scale=scale)

    if masked:
        out_img = out_img * (img>0)
        
    return(out_img)


def window_level_image(img, window, level, pix_type=sitk.sitkUInt8):
    filter = sitk.IntensityWindowingImageFilter()
    filter.SetWindowMinimum(level-window/2)
    filter.SetWindowMaximum(level+window/2)
    filter.SetOutputMinimum(0)
    filter.SetOutputMaximum(255)

    return(sitk.Cast(filter.Execute(img), pix_type))

def label_overlay(labels, feature, opacity=0.5, colormap=None):    
    #  LabelOverlay(Image image, Image labelImage, double opacity=0.5, double backgroundValue=0.0, VectorUInt8 colormap=std::vector< uint8_t >()) -> Image
    filter = sitk.LabelOverlayImageFilter()
    filter.SetOpacity(opacity)
    filter.SetBackgroundValue(0)
    filter.SetColormap(colormap)
    return(filter.Execute(feature, labels))


    overlayFilter.SetInput2(labels)
    overlayFilter.SetOpacity(opacity)

    if not colormap is None:
        overlayFilter.ResetColors()
        #colormap=[ (230,38,127), (220,97,1), (120,94,240), (254,176,1) ]
        for color in colormap:
            overlayFilter.AddColor(*color)

    overlayFilter.Update()
    return(overlayFilter.GetOutput())





