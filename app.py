# %%
from arkitekt import easy, register
from arkitekt.tqdm import tqdm
from mikro.api.schema import RepresentationFragment, VideoFragment

from mikro.api.schema import upload_video
import numpy as np
from matplotlib import cm
from typing import Iterator, Optional
from pathlib import Path

import matplotlib.animation as ani
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os


def write_animation(
    itr: Iterator[np.array],
    out_file: Path,
    dpi: int = 50,
    fps: int = 30,
    title: str = "Animation",
    comment: Optional[str] = None,
    writer: str = "ffmpeg",
) -> None:
    """Function that writes an animation from a stream of input tensors.

    Args:
        itr: The image iterator, yielding images with shape (H, W, C).
        out_file: The path to the output file.
        dpi: Dots per inch for output image.
        fps: Frames per second for the video.
        title: Title for the video metadata.
        comment: Comment for the video metadata.
        writer: The Matplotlib animation writer to use (if you use the
            default one, make sure you have `ffmpeg` installed on your
            system).
    """

    first_img = itr[0]

    print(first_img.shape)
    height, width, _ = first_img.shape
    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi))

    # Ensures that there's no extra space around the image.
    fig.subplots_adjust(
        left=0,
        bottom=0,
        right=1,
        top=1,
        wspace=None,
        hspace=None,
    )

    # Creates the writer with the given metadata.
    writer_cls = ani.writers[writer]
    metadata = {
        "title": title,
        "artist": __name__,
        "comment": comment,
    }
    mpl_writer = writer_cls(
        fps=fps,
        metadata={k: v for k, v in metadata.items() if v is not None},
    )

    with mpl_writer.saving(fig, out_file, dpi=dpi):
        im = ax.imshow(first_img, interpolation="nearest")
        mpl_writer.grab_frame()

        for img in tqdm(itr):
            im.set_data(img)
            mpl_writer.grab_frame()


@register
def render_video(image: RepresentationFragment, fps: int = 2) -> VideoFragment:
    """Render Video

    Render a video from a zstack.

    Args:
        image (RepresentationFragment): The image
        fps (int, optional): The frames per stack. Defaults to 2.

    Returns:
        VideoFragment: The video
    """
    zstack = image.data.sel(t=0, c=0).transpose(*list("zyx")).compute()
    max = zstack.max()
    min = zstack.min()
    image_data = np.interp(zstack, (min, max), (0, 255)).astype(np.uint8)
    zstack = cm.viridis(image_data)
    zsize, x, y, c = zstack.shape
    print(zstack.shape)
    frames = []
    for i in range(zsize):
        frames.append(zstack[i, :, :, :])

    filename = f"{uuid.uuid4()}.mp4"

    write_animation(frames, filename, fps=fps)

    video = upload_video(filename, representations=[image.id])
    os.remove(filename)
    return video

