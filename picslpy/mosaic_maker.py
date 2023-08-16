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
    print(img_size)

    # Get number of rows
    slices = int(img_size[2])
    rows = int(slices / columns) + 1

    # Create output image
    out_size = [size[0] * columns, size[1] * rows]

    out = None
    if image.GetNumberOfComponentsPerPixel() == 3:
        out = sitk.Image(out_size, sitk.sitkVectorUInt8, 3)
    else:
        out = sitk.Image(out_size, sitk.sitkUInt8)

    max_dim = img_size[0]
    if img_size[1] > max_dim:
        max_dim = img_size[1]

    tile_scale = size[0] / max_dim

    out_size = [int(img_size[0] * tile_scale), int(img_size[1] * tile_scale)]
    out_spacing = [image.GetSpacing()[0] / tile_scale, image.GetSpacing()[1] / tile_scale]
    out_origin = [image.GetOrigin()[0], image.GetOrigin()[1]]

    print(size)
    print(out_size)

    for i in range(slices):
        # Get slice
        islice = image[:,:,i]

        # Resample
        pix_type=sitk.sitkUInt8
        if islice.GetNumberOfComponentsPerPixel() > 1:
            pix_type=sitk.sitkVectorUInt8
            islice = sitk.Cast(islice, pix_type)        
        
        sitk.WriteImage(islice, "slice_"+str(i)+".png")

        resample = sitk.Resample(islice, out_size, sitk.Transform(), sitk.sitkLinear, out_origin, out_spacing, islice.GetDirection(), 0.0, pix_type)

        # Copy to output
        out_index = [int(i % columns) * size[0], int(i / columns) * size[1]]

        out[out_index[0]:(out_index[0]+out_size[0]), out_index[1]:(out_index[1]+out_size[1])]=resample

    print(out.GetNumberOfComponentsPerPixel())

    return out          


def main():
    parser = argparse.ArgumentParser(prog='mosaic_maker', description='Tile volume slices')
    parser.add_argument('-o', '--output', help='Input filename', required=True)
    parser.add_argument('-s', '--size', help='Size of each slice', nargs=2, required=False, type=int, default=[128,128])
    parser.add_argument('-c', '--columns', help='Number of columns', required=False, default=0, type=int)
    parser.add_argument('-w', '--window_level', help="Intensity window and level", nargs=2, required=False, default=None)
    parser.add_argument('-m', '--minmax', help="Intensity scale using min and max", required=False, default=False, action='store_true')
    parser.add_argument('-a', '--align', help="Set voxel ordering", required=False, default='')
    parser.add_argument('-H', '--html', help="Create html file", required=False, default='')
    parser.add_argument('input', nargs='+', help='Input filename')
    args = parser.parse_args()

    # Check for inputs
    if len(args.input) == 0:
        print('No input files specified')
        sys.exit(1)

    png_list=[]

    # Load images
    out_image=True
    for f in args.input:

        out_base = os.path.basename(f)
        file_base = out_base.split(".")[0]

        out_dir = args.output
        out_name = os.path.join(out_dir, file_base+'.png')

        try:
            img = sitk.ReadImage(f)
        except:
            print("skipping "   + f + " as it is not a valid image")
            continue
        
        img_list=[]
        if img.GetDimension() == 3:
            img_list.append(img)

        if img.GetDimension() == 4:
            for i in range(img.GetSize()[3]):
                img_list.append(img[:,:,:,i])

        if img.GetDimension() > 4:
            print("skipping "   + f + " as it is not 3D or 4D")
            continue            

        #if img.GetDimension() < 3:
        #    print("skipping "   + f + " as it is not 3D or 4D")
        #    continue            

        col = args.columns
        if col == 0:
            col = img.GetSize()[2]
            col = int(np.sqrt(col)) + 1

        wmin=0
        wmax=1

        idx=0
        for img3 in img_list:

            idx_str=""
            if len(img_list) > 1:
                idx_str="_"+str(idx)
            out_name = os.path.join(out_dir, file_base+idx_str+'.png')
            idx += 1

            iscaled = img3
            print(img3.GetNumberOfComponentsPerPixel())

            if img3.GetNumberOfComponentsPerPixel() == 1:

                if args.window_level is None:
                    minmax = sitk.MinimumMaximumImageFilter()
                    minmax.Execute(img3)
                    wmax = minmax.GetMaximum()
                    wmin = minmax.GetMinimum()
                else:
                    wmax = args.window_level[1]+args.window_level[0]/2
                    wmin = args.window_level[1]-args.window_level[0]/2

                if args.minmax or args.window_level is not None:
                    ifilter = sitk.IntensityWindowingImageFilter()
                    ifilter.SetWindowMinimum(wmin)
                    ifilter.SetWindowMaximum(wmax)
                    ifilter.SetOutputMinimum(0)
                    ifilter.SetOutputMaximum(255)
                    iscaled = ifilter.Execute(img3)

            if img3.GetNumberOfComponentsPerPixel()==3:
                print("Input is RGB, no intensity scaling applied")

            if args.align != '':
                iscaled =  sitk.DICOMOrient(iscaled, args.align)
                sitk.WriteImage(iscaled, args.align+".nii.gz")

            tile = image_to_tiles(iscaled, args.size, col)
            if out_image:
                sitk.WriteImage(tile, out_name)
                png_list.append(out_name)

    if args.html != '':
        make_html(png_list, args.html)

if __name__ == "__main__":
    main()

