import argparse
import os
import sys
import SimpleITK as sitk
import numpy as np

def make_html(png_list, filename):

    header = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bootstrap Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</head>
<body>

<div class="jumbotron text-center">
  <h1>Mosaic Maker Results</h1>
  <p>Images to review</p> 
</div>
  
<div class="container">
"""
    with open(filename,"w") as file:
        file.write(header)

        for png in png_list:
            file.write('<div class="row">')
            file.write('<div class="col-sm-12">')
            file.write('<p>'+png+'</p>')
            file.write('</div>')
            file.write('</div>')
            file.write('<div class="row">')
            file.write('<div class="col-sm-12">')
            file.write('<img src="'+png+'" alt="image" width="100%">')
            file.write('</div>')
            file.write('</div>')

        file.write("</div>")
        file.write("</body>")
        file.write("</html>")

        file.close()

def image_to_tiles(image, size, columns):
    # Get image size
    img_size = image.GetSize()

    # Get number of rows
    slices = int(img_size[2])
    rows = int(slices / columns) + 1

    # Create output image
    out_size = [size[0] * columns, size[1] * rows]

    out = None
    if image.GetNumberOfComponentsPerPixel() > 1:
        out = sitk.Image(out_size, sitk.sitkVectorUInt8)
    else:
        out = sitk.Image(out_size, sitk.sitkUInt8)

    max_dim = img_size[0]
    if img_size[1] > max_dim:
        max_dim = img_size[1]

    tile_scale = size[0] / max_dim

    out_size = [int(img_size[0] * tile_scale), int(img_size[1] * tile_scale)]
    out_spacing = [image.GetSpacing()[0] / tile_scale, image.GetSpacing()[1] / tile_scale]
    out_origin = [image.GetOrigin()[0], image.GetOrigin()[1]]

    for i in range(slices):
        # Get slice
        islice = image[:,:,i]

        # Resample
        pix_type=sitk.sitkUInt8
        if islice.GetNumberOfComponentsPerPixel() > 1:
            pix_type=sitk.sitkVectorUInt8
            islice = sitk.Cast(islice, pix_type)        

        resample = sitk.Resample(islice, out_size, sitk.Transform(), sitk.sitkLinear, out_origin, out_spacing, islice.GetDirection(), 0.0, pix_type)

        # Copy to output
        out_index = [int(i % columns) * size[0], int(i / columns) * size[1]]

        out[out_index[0]:(out_index[0]+out_size[0]), out_index[1]:(out_index[1]+out_size[1])]=resample

    return out          


def main():
    parser = argparse.ArgumentParser(prog='mosaic_maker', description='Tile volume slices')
    parser.add_argument('-i', '--input', help="Input filename", required=True, type=str)
    parser.add_argument('-o', '--output', help='Input filename', required=True, type=str)
    parser.add_argument('-l', '--labels', help="Image labels", required=False, default=None)
    parser.add_argument('-a', '--alpha', help="Alpha is opacity value [0.0-1.0] for labels", required=False, default=0.3 )
    parser.add_argument('-w', '--window_level', help="Intensity window and level", nargs=2, required=False, default=None)
    parser.add_argument('-m', '--minmax', help="Intensity scale using min and max", required=False, default=False, action='store_true')
    parser.add_argument('-c', '--colormap', help="Vector for rgb values, 3 per label [0,255]", nargs='+', required=False, default=None, type=int)
    args = parser.parse_args()
    print(args)

    # Check for inputs
    if not os.path.exists(args.input):
        print('Input not found')
        sys.exit(1)

    try:
        in_img = sitk.ReadImage(args.input)
    except:
        print('Failed to read input image')
        sys.exit(1)

    # Adjust input intensity
    minmax = sitk.MinimumMaximumImageFilter()
    minmax.Execute(in_img)
    in_max = minmax.GetMaximum()
    in_min = minmax.GetMinimum()

    # auto adjust if needed
    if args.window_level is None:
        if not args.minmax:
            if in_max > 255 or in_min < 0:
                args.minmax=True

    ifilter = sitk.IntensityWindowingImageFilter()
    ifilter.SetOutputMinimum(0)
    ifilter.SetOutputMaximum(255)

    if args.window_level is not None:
        if args.minmax:
            print("Use window and level or minmax, not both")
            sys.exit(1)
        ifilter.SetWindowMinimum(args.window_level[1]-args.window_level[0]/2)
        ifilter.SetWindowMaximum(args.window_level[1]+args.window_level[0]/2)
        in_img = ifilter.Execute(in_img)
    
    if args.minmax:
        ifilter.SetWindowMinimum(in_min)
        ifilter.SetWindowMaximum(in_max)        
        in_img = ifilter.Execute(in_img)
    
    in_img = sitk.Cast(in_img, sitk.sitkUInt8)


    if args.labels is not None:
        try:
            label_img = sitk.ReadImage(args.labels, sitk.sitkUInt8)
        except:
            print('Failed to read label image')
            sys.exit(1)

        filter = sitk.LabelOverlayImageFilter()
        filter.SetOpacity(args.alpha)
        filter.SetBackgroundValue(0)
        if args.colormap is not None:
            filter.SetColormap(args.colormap)
        overlay = filter.Execute(in_img, label_img)

        try:
            sitk.WriteImage(overlay, args.output)
        except:
            print('Failed to write output image')
            sys.exit(1)

        
if __name__ == "__main__":
    main()

