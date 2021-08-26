import bpy

from ..Utils.SFR_TestRender import TestRender

from bpy.types import (
    Operator
)
from .. import SFR_Settings

try:
    from skimage import io
except ImportError:
    print("Error loading scikit-image. Please go to the addon preferences and click Install Dependencies.")
    io = None


class SFR_Benchmark_cy(Operator):
    bl_idname = "render.superfastrender_benchmark"
    bl_label = "BENCHMARK"
    bl_description = "Tests your scene to detect the best optimization settings."

    def execute(self, context):

        if not io:
            self.report(
                {'ERROR'}, "Please install dependencies from addon preferences!")
            return {'CANCELLED'}
            
        #####################
        ### SET LOW VALUE ###
        #####################

        context = bpy.context
        scene = context.scene
        settings: SFR_Settings = scene.sfr_settings

        # return {'FINISHED'}
        prefs = bpy.context.preferences.addons['cycles'].preferences

        for device_type in prefs.get_device_types(bpy.context):
            prefs.get_devices_for_type(device_type[0])

        if prefs.get_devices_for_type == 'OPTIX':
            scene.render.tile_x = 512
            scene.render.tile_y = 512
        elif prefs.get_devices_for_type == 'CUDA':
            scene.render.tile_x = 256
            scene.render.tile_y = 256
        elif prefs.get_devices_for_type == 'OPENCL':
            scene.render.tile_x = 256
            scene.render.tile_y = 256
        elif prefs.get_devices_for_type == 'CPU':
            scene.render.tile_x = 32
            scene.render.tile_y = 32

        scene.cycles.debug_use_spatial_splits = True
        scene.cycles.debug_use_hair_bvh = True
        scene.render.use_persistent_data = True
        scene.render.use_save_buffers = True

        # set adaptive samples
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.samples = 50000
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.adaptive_min_samples = 64

        # set max bounces
        scene.cycles.max_bounces = 64  # done
        scene.cycles.diffuse_bounces = 0  # done
        scene.cycles.glossy_bounces = 0  # done
        scene.cycles.transparent_max_bounces = 0  # done
        scene.cycles.transmission_bounces = 0  # done
        scene.cycles.volume_bounces = 0  # done
        scene.cycles.light_sampling_threshold = 0.1

        # set clamps to reduce fireflies
        scene.cycles.sample_clamp_direct = 0
        scene.cycles.sample_clamp_indirect = 1  # done

        # set caustic settings
        scene.cycles.caustics_reflective = False  # done
        scene.cycles.caustics_refractive = False  # done
        scene.cycles.blur_glossy = 10

        # change volume settings
        scene.cycles.volume_step_rate = 5
        scene.cycles.volume_preview_step_rate = 5
        scene.cycles.volume_max_steps = 256

        # simplfy the scene
        scene.render.use_simplify = True
        # viewport
        scene.render.simplify_subdivision = 2
        scene.render.simplify_child_particles = 0.2
        scene.cycles.texture_limit = '2048'
        scene.cycles.ao_bounces = 2
        # render
        scene.render.simplify_subdivision_render = 4
        scene.render.simplify_child_particles_render = 1
        scene.cycles.texture_limit_render = '4096'
        scene.cycles.ao_bounces_render = 4
        # culling
        scene.cycles.use_camera_cull = True
        scene.cycles.use_distance_cull = True
        scene.cycles.camera_cull_margin = 0.1
        scene.cycles.distance_cull_margin = 50

        ##################
        ### INITIALIZE ###
        ##################

        ### old settings ###
        oldCompositing = scene.render.use_compositing
        oldSequencer = scene.render.use_sequencer
        oldResX = scene.render.resolution_x
        oldResY = scene.render.resolution_y
        oldPercent = scene.render.resolution_percentage

        scene.render.use_compositing = False
        scene.render.use_sequencer = False

        ### set settings ###
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'

        path = settings.inputdir

        iteration = 0
        repeat = TestRender(path, iteration, settings)

        ### DIFFUSE ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.diffuse_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.diffuse_bounces -= 1

        iteration = 0
        repeat = True

        ### GLOSS1 ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.glossy_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.glossy_bounces -= 1

        iteration = 0
        repeat = True

        ### TRANSMISSION2 ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.transmission_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.transmission_bounces -= 1

        iteration = 0
        repeat = True

        ### GLOSS2 ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.glossy_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.glossy_bounces -= 1

        iteration = 0
        repeat = True

        ### TRANSMISSION1 ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.transmission_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.transmission_bounces -= 1

        iteration = 0
        repeat = True

        ### TRANSPARENT ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.transparent_max_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.transparent_max_bounces -= 1

        iteration = 0
        repeat = True

        ### VOLUME ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.volume_bounces += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.volume_bounces -= 1

        ### TOTAL ###
        scene.cycles.max_bounces = scene.cycles.diffuse_bounces + scene.cycles.glossy_bounces + \
            scene.cycles.transmission_bounces + scene.cycles.volume_bounces

        iteration = 0
        repeat = True

        ### INDIRECT ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.sample_clamp_indirect += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.sample_clamp_indirect -= 1

        iteration = 0
        repeat = True

        ### CAUSTIC BLUR ###
        while repeat:
            # start first render
            TestRender(path, iteration, settings)
            # set settings
            scene.cycles.blur_glossy += 1
            # set next
            iteration += 1
            print("Iteration: ", iteration)
            # start second render
            repeat = TestRender(path, iteration, settings)
        scene.cycles.blur_glossy -= 1

        iteration = 0
        repeat = True

        ### CAUSTIC REFL ###
        # start first render
        TestRender(path, iteration, settings)
        # set settings
        scene.cycles.caustics_reflective = True
        # start second render
        scene.cycles.caustics_reflective = TestRender(
            path, iteration, settings)

        iteration = 0
        repeat = True

        ### CAUSTIC REFR ###
        # start first render
        TestRender(path, iteration, settings)
        # set settings
        scene.cycles.caustics_refractive = True
        # start second render
        scene.cycles.caustics_refractive = TestRender(
            path, iteration, settings)


        ### get old settings ###
        scene.render.use_compositing = oldCompositing
        scene.render.use_sequencer = oldSequencer
        scene.render.resolution_x = oldResX
        scene.render.resolution_y = oldResY
        scene.render.resolution_percentage = oldPercent

        self.report({'INFO'}, "Benchmark complete")

        return {'FINISHED'}
