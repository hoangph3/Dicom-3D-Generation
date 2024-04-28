import bpy
import os


def smooth(input_file, output_file, *args, **kwargs):
    default_smooth = {"factor": 0.5, "iterations": 40}

    # Import the STL file
    bpy.ops.import_mesh.stl(filepath=input_file)

    # Get the imported mesh object
    obj = bpy.context.object

    # Add a smooth modifier
    smooth_x = obj.modifiers.new(name="Smooth_X", type='SMOOTH')
    smooth_x.factor = kwargs.get("x", default_smooth).get("factor")
    smooth_x.iterations = kwargs.get("x", default_smooth).get("iterations")
    smooth_x.use_x = True
    smooth_x.use_y = False
    smooth_x.use_z = False

    smooth_y = obj.modifiers.new(name="Smooth_Y", type='SMOOTH')
    smooth_y.factor = kwargs.get("y", default_smooth).get("factor")
    smooth_y.iterations = kwargs.get("y", default_smooth).get("iterations")
    smooth_y.use_x = False
    smooth_y.use_y = True
    smooth_y.use_z = False

    smooth_z = obj.modifiers.new(name="Smooth_Z", type='SMOOTH')
    smooth_z.factor = kwargs.get("z", default_smooth).get("factor")
    smooth_z.iterations = kwargs.get("z", default_smooth).get("iterations")
    smooth_z.use_x = False
    smooth_z.use_y = False
    smooth_z.use_z = True

    # Apply the modifier
    bpy.ops.object.modifier_apply(modifier="Smooth_X")
    bpy.ops.object.modifier_apply(modifier="Smooth_Y")
    bpy.ops.object.modifier_apply(modifier="Smooth_Z")

    # Export the smoothed mesh as STL
    bpy.ops.export_mesh.stl(filepath=output_file, use_selection=True)

    # Delete the imported mesh object
    bpy.data.objects.remove(obj)
