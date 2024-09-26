name = "blender"

version = "4.2.2"

authors = ["The Blender Foundation", "Leo Depoix (@piloegao)"]

description = """
    A blender rez package using the pre-build version.
    """

requires = ["python"]

uuid = "org.blender.blender"

build_command = "python {root}/build.py {install}"


def commands():
    executables = {
        "windows": {
            "blender": "blender.exe",
            "blender_oculus": "blender_oculus.cmd",
            "blender_factory_startup": "blender_factory_startup.cmd",
            "blender_debug_log": "blender_debug_log.cmd",
            "blender_debug_gpu": "blender_debug_gpu.cmd",
            "blender_debug_gpu_glitchworkaround": "blender_debug_gpu_glitchworkaround.cmd",
        },
        "osx": {
            "blender": "Blender.app/Contents/MacOS/Blender"
        },
        "linux": {},
    }

    for exec_command, executable_file in executables.get(system.platform).items():
        alias(exec_command, "{root}/blender/%s" % executable_file)
