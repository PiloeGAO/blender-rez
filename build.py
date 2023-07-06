import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile

DOWNLOAD_URL = "https://download.blender.org/release/Blender{MAJOR}.{MINOR}/{filename}"

FILE_NAME = "blender-{MAJOR}.{MINOR}.{PATCH}-{os}-{arch}.{ext}"

DOWNLOAD_TYPES = {"windows": "zip", "macos": "dmg", "linux": "tar.xz"}


def get_os_information():
    """Get the os name and the architecture.

    Returns:
        tuple: OS name and architecture.
    """
    os_names = {
        "Windows": "windows",
        "Darwin": "macos",
    }
    architectures = {"AMD64": "x64", "arm64": "arm64"}
    os_platform = platform.system()
    os_architecture = platform.machine()

    return (
        os_names.get(os_platform, "linux"),
        architectures.get(os_architecture, "x64"),
    )


def build(source_path, build_path, install_path, targets):
    """Build/Install function.

    Args:
        source_path (str): Path to the rez package root.
        build_path (str): Path to the rez build directory.
        install_path (str): Path to the rez install directory.
        targets (str): Target run by the command, i.e. `build`, `install`...

    Raises:
        RuntimeError: Your current OS is not supported.
    """
    os_name, arch = get_os_information()
    package_major, package_minor, package_patch = os.environ.get(
        "REZ_BUILD_PROJECT_VERSION", "0.0.0"
    ).split(".")

    if os_name == "linux":
        raise RuntimeError(f"Your current OS is not supported ({os_name}).")

    blender_archive = FILE_NAME.format(
        MAJOR=package_major,
        MINOR=package_minor,
        PATCH=package_patch,
        os=os_name,
        arch=arch,
        ext=DOWNLOAD_TYPES.get(os_name),
    )
    download_url = DOWNLOAD_URL.format(
        MAJOR=package_major, MINOR=package_minor, filename=blender_archive
    )

    def _build():
        """Build the package locally."""
        archive_path = os.path.join(build_path, blender_archive)

        if not os.path.isfile(archive_path):
            print(f"Downloading Blender archive from: {download_url}")
            with open(archive_path, "wb") as file:
                with urllib.request.urlopen(download_url) as request:
                    file.write(request.read())

        print("Extracting the archive.")
        match os_name:
            case "windows":
                with zipfile.ZipFile(archive_path) as archive_file:
                    archive_file.extractall(build_path)
            case "macos":
                mac_mountpoint = "/Volumes/Blender"
                subprocess.run(["hdiutil", "attach", archive_path])
                shutil.copytree(os.path.join(mac_mountpoint, "Blender.app"), os.path.join(build_path, "Blender.app"))
                subprocess.run(["hdiutil", "detach", mac_mountpoint])
            case _:
                pass

    def _install():
        """Install the package."""
        print("Installing the package.")
        extracted_archive_path = os.path.join(
            build_path, os.path.splitext(blender_archive)[0]
        )
        install_directory = os.path.join(install_path, "blender")

        if os.path.isdir(install_directory):
            shutil.rmtree(install_directory)
        os.mkdir(install_directory)

        match os_name:
            case "windows":
                for element in os.listdir(extracted_archive_path):
                    element_path = os.path.join(extracted_archive_path, element)
                    shutil.move(element_path, install_directory)
            case "macos":
                shutil.move(
                    os.path.join(build_path, "Blender.app"),
                    os.path.join(install_directory, "Blender.app"),
                )
            case _:
                pass

    _build()

    if "install" in (targets or []):
        _install()


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
