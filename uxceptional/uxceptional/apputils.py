from pathlib import Path
from typing import Union
import subprocess
import asyncio
from PIL import Image
import OpenGL.GL as gl
from xdg import IconTheme
# This can / should be overridden
resources_dir = None

def set_resource_dir(new_dir):
    global resources_dir
    resources_dir = new_dir

def event(path, name):
    """
    Print an event to stdout
    """
    print(f"{path}.{name}")

def load_icon(icon_name, icon_size):
    path = IconTheme.getIconPath(icon_name, icon_size)
    return load_texture(path)

def load_texture(path):
    """From an image path, return an opengl texture

    Args:
        path (str): Path to icon

    Returns:
        int: OpenGL texture ID
    """
    with Image.open(path) as im:
        convert = im.convert("RGBA")
        textureData = convert.tobytes()
        width = im.width
        height = im.width

    tex = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        textureData,
    )

    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)  # cleanup
    return tex

def loadimg(resource_name):
    """
    Load image as OpenGL texture. Return that texture ID
    """
    global resources_dir
    return load_texture(Path(resources_dir) / resource_name)



def run(
    command: Union[list[str], str], shell=False
) -> subprocess.CompletedProcess:
    """
    Run a process with arguments. 
    Optionally, as a shell command
    returns CompletedProcess.
    """
    args = command

    result = subprocess.run(
        args,
        capture_output=True,
        shell=shell,
        errors="surrogateescape",
        encoding="utf-8",
    )
    return result

async def run_async(
    command: Union[list[str], str], shell=False
) -> subprocess.CompletedProcess:
    """
    Run a process with arguments asynchronously
    Optionally, as a shell command
    returns CompletedProcess.
    """
    args = command
    if shell:
        proc = await asyncio.create_subprocess_shell(args,stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return subprocess.CompletedProcess(args, proc.returncode, stdout.decode("utf-8", errors="surrogateescape"), stderr.decode("utf-8", errors="surrogateescape"))
    else:
        proc = await asyncio.create_subprocess_exec(args,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return subprocess.CompletedProcess(args, proc.returncode, stdout.decode("utf-8", errors="surrogateescape"), stderr.decode("utf-8", errors="surrogateescape"))

def vec_color(hex) -> tuple[float, float, float, float]:
    """
    Convert hex color to a vector array
    """
    hex = hex.replace("#", "")
    r = int(hex[0:2], 16) / 255.0
    g = int(hex[2:4], 16) / 255.0
    b = int(hex[4:6], 16) / 255.0
    if len(hex) == 8:
        a = int(hex[6:8], 16) / 255.0
    else:
        a = 1.0
    return r, g, b, a
