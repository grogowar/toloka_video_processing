import numpy as np
import pyFSDK


def pyfsdk_to_numpy(fsdk_image):
    """
    Function to convert from pyfsdk image to numpy image.
    """

    if fsdk_image.is_keeping_color_image():
        pixels = fsdk_image.get_color_image_data()
        data = np.frombuffer(pixels, dtype=np.uint8)
        return data.reshape(fsdk_image.height(), fsdk_image.width(), 3)

    else:
        pixels = fsdk_image.get_image_data()
        data = np.frombuffer(pixels, dtype=np.uint8)
        return data.reshape(fsdk_image.height(), fsdk_image.width())


def numpy_to_pyfsdk(np_array, ColorType):
    """
    Function to convert from numpy image to pyfsdk image.
    """

    return pyFSDK.containers.Image(bytearray(np_array.reshape(np_array.size)),
                                   np_array.shape[0], np_array.shape[1],
                                   ColorType,
                                   color_image=True,
                                   rotate=False,
                                   copy_data=True)