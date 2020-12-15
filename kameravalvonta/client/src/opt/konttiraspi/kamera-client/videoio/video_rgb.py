### perustuu Vladimir Guzov:n kirjastoon videoio
## https://github.com/vguzov/videoio
##
##

import os
import numpy as np
import ffmpeg
from typing import Tuple, Dict

print("VIDEOIO")

def videosave(path: str, images: np.ndarray, lossless: bool = False, preset: str = 'slow', fps: float = None):
    """
    Saves the video with encoded with H.264 codec
    Args:
        path (str): Path to output video
        images (np.ndarray): NumPy array of video frames
        lossless (bool): Whether to apply lossless encoding.
            Be aware: lossless format is still lossy due to RGB to YUV conversion inaccuracy
        preset (str): H.264 compression preset
        fps (float): Target FPS. If None, will be set to ffmpeg's default
    """
    assert images[0].shape[2] == 3, "Alpha channel is not supported"
    #assert preset in H264_PRESETS, "Preset '{}' is not supported by libx264, supported presets are {}".\
    #    format(preset, H264_PRESETS)
    resolution = images[0].shape[:2][::-1]
    input_params = dict(format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(*resolution), loglevel='error')
    if fps is not None:
        input_params['framerate'] = fps
    ffmpeg_input = ffmpeg.input('pipe:', **input_params)
    encoding_params = {"c:v": "libx264", "preset": preset}
    if lossless:
        encoding_params['profile:v'] = 'high444'
        encoding_params['crf'] = 0

    ffmpeg_process = ffmpeg_input.output(path, pix_fmt='yuv444p' if lossless else 'yuv420p', **encoding_params)

    ffmpeg_process = ffmpeg_process.overwrite_output().run_async(pipe_stdin=True)
    for color_frame in images:
        if color_frame.dtype == np.float16 or color_frame.dtype == np.float32 or color_frame.dtype == np.float64:
            color_frame = (color_frame*255).astype(np.uint8)
        elif color_frame.dtype != np.uint8:
            raise NotImplementedError("Dtype {} is not supported".format(color_frame.dtype))
        ffmpeg_process.stdin.write(color_frame.tobytes())
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()



class VideoWriter:
    """
    Class for writing a video frame-by-frame
    """
    def __init__(self, path:str, resolution: Tuple[int, int], lossless: bool = False,
                 preset: str = 'slow', fps: float = None):
        """
        Args:
            path (str): Path to output video
            resolution (Tuple[int, int]): Resolution of the input frames and output video (width, height)
            lossless (bool): Whether to apply lossless encoding.
                Be aware: lossless format is still lossy due to RGB to YUV conversion inaccuracy
            preset (str): H.264 compression preset
            fps (float): Target FPS. If None, will be set to ffmpeg's default
        """
        #assert preset in H264_PRESETS, "Preset '{}' is not supported by libx264, supported presets are {}". \
        #    format(preset, H264_PRESETS)
        perusnimi=path.split(".")[0]
        self.resolution = resolution
        input_params = dict(format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(*resolution), loglevel='error')
        if fps is not None:
            input_params['framerate'] = fps
        ffmpeg_input = ffmpeg.input('pipe:', **input_params)
        encoding_params = {"c:v": "libx264", "preset": preset, "r" :fps, "g": 1, "f": "hls", "hls_time": 1, "hls_list_size": 0, "hls_flags": "append_list", "hls_segment_filename": perusnimi+"-%04d.ts"}
        if lossless:
            encoding_params['profile:v'] = 'high444'
            encoding_params['crf'] = 0

        self.ffmpeg_process = ffmpeg_input.output(path, pix_fmt='yuv444p' if lossless else 'yuv420p', **encoding_params)
        self.ffmpeg_process = self.ffmpeg_process.overwrite_output().run_async(pipe_stdin=True)

    def write(self, color_frame: np.ndarray):
        """
        Write next frame
        Args:
            color_frame (np.ndarray): RGB frame to write
        """
        assert color_frame.shape[2] == 3, "Alpha channel is not supported"
        assert all([self.resolution[i] == color_frame.shape[1-i] for i in range(2)]), \
            "Resolution of color frame does not match with video resolution – expected {}, got {}".\
            format(self.resolution, color_frame.shape[:2][::-1])
        if color_frame.dtype == np.float16 or color_frame.dtype == np.float32 or color_frame.dtype == np.float64:
            color_frame = (color_frame*255).astype(np.uint8)
        elif color_frame.dtype != np.uint8:
            raise NotImplementedError("Dtype {} is not supported".format(color_frame.dtype))
        self.ffmpeg_process.stdin.write(color_frame.tobytes())

    def close(self):
        """
        Finish video creation process and close video file
        """
        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
