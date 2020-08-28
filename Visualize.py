# Simple Music Visualizer Script
# Create linear or radial visualizer with adjustable frequency range

# Written by Deepanshi Sharma for Blender 2.82

import bpy
import math

# Adjustable settings for user
# =============================================================================================
# =============================================================================================

filename = "Idfc.mp3"  # Supports all audio formats
fp = "/Users/deepanshisharma/Idfc.mp3"  # Replace "\" with "\\"
deleteExisting = True  # Delete the sound strip currently in the sequencer?
addSound = True  # Add this sound file to the sequencer?
startFrame = 1  # Start playing the sound at this frame

bars = 64  # Number of bars in the visualizer
height = 8.0  # Vertical scale of bars
width = 0.8  # Horizontal scale of bars

dist = 2.25  # Horizontal distance between bars for linear viz
radial = True  # Toggle option for linear or radial viz
radius = 20.0  # Only pertinent for radial viz

# =============================================================================================
# =============================================================================================

# Set context to video sequencer
bpy.context.area.type = 'SEQUENCE_EDITOR'

if deleteExisting:
    bpy.ops.sequencer.select_all(action='SELECT')
    bpy.ops.sequencer.delete()

if addSound:
    bpy.ops.sequencer.sound_strip_add(filepath=fp, frame_start=startFrame, channel=1)

# Set context to default 3D view
bpy.context.area.type = 'VIEW_3D'
bpy.data.scenes["Scene"].frame_current = startFrame
bpy.context.scene.cursor.location = (0, 0, 0)

# Approximate number of half steps each bar will cover
step = 120.0 / bars

# Twelfth root of 2
root = 2 ** (1.0 / 12.0)

# Starting frequencies
lowest = 0.0
highest = 16.0

for i in range(0, bars):
    # Add a plane centered on its edge
    bpy.ops.mesh.primitive_plane_add(location=(0, 1, 0))
    bpy.context.scene.cursor.location = bpy.context.active_object.location
    bpy.context.scene.cursor.location.y -= 1
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    pos = [0.0, 0.0, 0.0]

    # For a radial visualizer
    if radial:
        # Bars are placed at equal angles around a circle
        theta = -2 * i * math.pi / (bars)
        bpy.context.active_object.rotation_euler[2] = theta
        pos = [-math.sin(angle) * radius, math.cos(theta) * radius, 0]

    else:
        # Bars are placed equidistant on a line
        pos[0] = i * dist

    # Apply position changes
    bpy.context.active_object.location = (pos[0], pos[1], pos[2])
    bpy.context.scene.cursor.location = (pos[0], pos[1], pos[2])
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    # Scaling
    bpy.context.active_object.scale.x = width
    bpy.context.active_object.scale.y = height
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.anim.keyframe_insert_menu(type='Scaling')
    bpy.context.active_object.animation_data.action.fcurves[0].lock = True
    bpy.context.active_object.animation_data.action.fcurves[2].lock = True

    # Set context to graph editor
    bpy.context.area.type = 'GRAPH_EDITOR'

    # Determining the frequency range
    lowest = highest
    highest = lowest * (root ** step)

    # Bake sounds to f curve
    bpy.ops.graph.sound_bake(filepath=fp, low=(lowest), high=(highest))
    bpy.context.active_object.animation_data.action.fcurves[1].lock = True

    # Set context to script
    bpy.context.area.type = 'TEXT_EDITOR'

    # Set animation frames to song length
    bpy.context.scene.frame_end = bpy.context.scene.sequence_editor.sequences_all[filename].frame_final_duration + startFrame