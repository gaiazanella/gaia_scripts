#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robin.guerry
"""
import psutil
import tracemalloc
import copy
import datetime
import os
from pathlib import Path
from typing import Dict, Optional, Union, List, Tuple

import h5py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates

import numpy as np

from febus_optics_lib.plugins_das import PluginFebus


class BaseExceptionReader(Exception, BaseException):
    """Base class for exceptions specific to the Reader."""

    def __init__(self, msg):
        super().__init__(msg)

##
# monitoring part


@staticmethod
def monitoring_start():
    tracemalloc.start()


@staticmethod
def monitoring_stop():
    tracemalloc.stop()

# Function to display memory usage


@staticmethod
def display_memory(step_name):
    current, peak = tracemalloc.get_traced_memory()
    print(
        f"[{step_name}] Current: {current / 1024 ** 2:.2f} MB; Peak: {peak / 1024 ** 2:.2f} MB")
##


class H5ReaderDas:
    """
    Reader class for Febus Optics DAS (Distributed Acoustic Sensing) data files.
    """

    def __init__(self, file: str, source: str = "febus") -> None:
        """
        Initializes reading of a DAS data file and sets up parameters.
        Checks the existence of the file and extracts the necessary parameters.

        Args:
            file (str): Absolute path to the hdf5 file.
            source (str, optional): Source of the file, typically the plugin name.
                Defaults to "febus".
                Recognized plugin name: "febus".

        Raises:
            BaseExceptionReader: If the source is unknown or the file cannot be accessed.
        """
        self._file: str = ""
        # Initialize private attribute
        self.__initialize_attributes()

        if source == "febus":
            self.source = PluginFebus
        else:
            raise BaseExceptionReader(f"Unknown source: {source}")

        if file is not None:
            self.file = file  # This will call the setter method

    @property
    def file(self) -> str:
        """Safe getter for _file."""
        return self._file  # Getter method to access the private attribute

    @file.setter
    def file(self, filepath: str) -> None:
        """
        Validates and sets the file path, resetting internal parameters.

        Args:
            filepath (str): Absolute path to the hdf5 file.

        Raises:
            BaseExceptionReader: If the file path is invalid or the file cannot be accessed.
        """
        if filepath and not Path(filepath).is_file():
            raise BaseExceptionReader(
                f"Unable to access file with path {filepath}")

        self._file = filepath  # Set the private attribute
        self.__initialize_attributes()
        self._set_param()

    @property
    def data_dict(self) -> dict:
        """Safe getter for _data_dict."""
        return copy.deepcopy(self._data_dict)

    @property
    def param_dict(self) -> dict:
        """Safe getter for _param_dict."""
        return copy.deepcopy(self._param_dict)

    @property
    def hdf5_dict(self) -> dict:
        """Safe getter for _hdf5_dict."""
        return copy.deepcopy(self._hdf5_dict)

    @property
    def list_zones(self) -> list:
        """Safe getter for _list_zones."""
        return self._list_zones.copy()

    @property
    def data_type(self) -> str:
        """Safe getter for _data_type."""
        return self._data_type

    @property
    def user_parameters_dict(self) -> dict:
        """Safe getter for _user_parameters_dict."""
        return copy.deepcopy(self._user_parameters_dict)

    @property
    def extracted_parameters_dict(self) -> dict:
        """Safe getter for _extracted_parameters_dict."""
        return copy.deepcopy(self._extracted_parameters_dict)

    def _set_param(self):
        """
        Reads the file parameters and zones, storing them internally.
        The parameters are saved in "param_dict" and the zones in "list_zones".

        Generates a data types (e.g., "StrainRate") present in the file.
        It contains the actual name of the Dataset in the file that contains the data.

        Raises:
            OSError: If an I/O-related error occurs.
            BaseExceptionReader: If an error occurs during file reading.
        """
        if not self.file:
            raise ValueError("No file specified")

        try:
            self.__extract_attribut()
            setattr(self, "_list_zones", self._param_dict["list_zones"])
            setattr(self, "_data_type",
                    self._param_dict[self._list_zones[0]]['data_type'])

        except OSError as ose:
            raise ose
        except (KeyError, ValueError, IndexError, TypeError, BaseExceptionReader) as cust_e:
            raise BaseExceptionReader(
                f"Unable to get the parameters of file {self.file}") from cust_e

    def extract_blocks(
            self,
            from_time: Optional[float] = None,
            to_time: Optional[float] = None,
            time_type: str = "timestamp",
            from_dist: Optional[float] = None,
            to_dist: Optional[float] = None,
            dist_type: str = "meter",
            remove_redundancy: bool = True,
            offset_compensation: bool = False,
            zones: Union[str, list] = "all") -> Dict:
        """
        Extract blocks of data from the file and return them in a dictionary.
        For strain data, the block offsets can be adjusted.

        Depending on the time_type:
        - ("timestamp"): Retrieve the blocks between (inclusive) the block 
            containing 'from_time' and the block containing 'to_time'.
        - ("relative"): Like for "timestamp", but "from_time" and "to_time"
            are defined relatively to the timestamp of the first block of the file
        - ("index"): Extracts blocks between (inclusive) the indexes
            “from_time” and “to_time” in the list of all timestamps.

        Depending on the dist_type:
        - ("meter"): Cut the blocks between (inclusive) 2 distances
            in meter after recreating the distance_vector.
        - ("index"): Cut the blocks between (inclusive) 2 channels.


        Args:
            from_time (float, optional): Start time for extraction.
                If None, start at the timestamp of the first block.
                Defaults to None.
            to_time (float, optional): End time for extraction.
                If None, end at the timestamp of the last block.
                Defaults to None.
            time_type (str, optional): Mode for interpreting from_time and to_time values.
                Options are "timestamp", "index" or "relative".
                Defaults to "timestamp".
            from_dist (float, optional): Start distance for extraction.
                If None, start at the first distance value.
                Defaults to None.
            to_dist (float, optional): End distance for extraction.
                If None, end at the last distance value.
                Defaults to None.
            dist_type (str, optional): Mode for interpreting distance values.
                Options are "meter" or "index".
                Defaults to "meter".
            remove_redundancy (bool, optional): Whether to remove redundancy in the data.
                Defaults to True.
            offset_compensation (bool, optional): Whether to compensate for the
                offset of "strain" data.
                If False, no compensation is applied.
                If data_type is not "strain", no compensation is applied.
                If True, if the data_type is "strain", an offset will be applied to the values.
                The offset vector is saved in data_dict.
                Defaults to False.
            zones (str | list, optional): Zone(s) to extract data from.
                If "all", all zones will be read. Available zones can be found in list_zones.
                Defaults to "all".

        Raises:
            TypeError: If any input is of the wrong type.
            ValueError: If any input is invalid (e.g., start block < 0).
            OSError: If an I/O-related error occurs.
            MemoryError: If the size of would not nit in the RAM space.
            BaseExceptionReader: If the function cannot retrieve data.

        Returns:
            dict:
                keys:
                    - "data": a 3D numpy.ndarray,
                    - "distance_vect": a 1D numpy.ndarray,
                    - "timestamp_vect": a 1D numpy.ndarray,
                    - "remove_redundancy": bool,
                    - "offset_compensation": bool
        """
        user_inputs = {
            "from_time": (from_time, type(None)),
            "to_time": (to_time, type(None)),
            "time_type": (time_type, str),
            "from_dist": (from_dist, type(None)),
            "to_dist": (to_dist, type(None)),
            "dist_type": (dist_type, str),
            "remove_redundancy": (remove_redundancy, bool),
            "offset_compensation": (offset_compensation, bool),
            "concatenate": (False, bool),
            "zones": (zones, str),
        }
        # checking of the inputs
        try:
            if not self.file:
                raise ValueError("No file specified")
            self.__check_parameters(**user_inputs)
        except (ValueError, TypeError) as check_error:
            raise check_error
        if zones == "all":
            zones_to_set = self._list_zones
        else:
            if isinstance(zones, str):
                zones = [zones]
            zones_to_set = zones

        final_res = {}

        for zone in self._list_zones:
            if zone in zones_to_set:

                # update od user_parameters_dict
                user_inputs.pop("zones")
                user_parameters = {
                    key: val[0] for key, val in user_inputs.items()
                }
                self._user_parameters_dict.update(
                    {zone: user_parameters})

                try:
                    # setting of the indexes in self._data_dict
                    self.__set_indexes(
                        zone,
                        from_time=from_time,
                        to_time=to_time,
                        time_type=time_type,
                        from_dist=from_dist,
                        to_dist=to_dist,
                        dist_type=dist_type,
                    )

                    # checking shape to prevent memory failure
                    future_shape = (
                        self._data_dict[zone]["extracted_timestamp"].shape[0],
                        self._param_dict[zone]["block_time_size_wo"],
                        self._data_dict[zone]["extracted_distance"].shape[0])
                    if not self.__can_allocate_array(future_shape, dtype=np.float32):
                        raise MemoryError(
                            "Insufficient memory for the extraction. Allocation would fail.")

                    # extraction of the blocks
                    extracted_data, offset_matrix = self.__extract_block(
                        zone, remove_redundancy=remove_redundancy,
                        offset_compensation=offset_compensation)
                    if not extracted_data or extracted_data is None:
                        raise TypeError("Extracted data is empty")
                    self._data_dict[zone].update(
                        {"offset_matrix": offset_matrix})

                except OSError as ose:
                    raise ose
                except (KeyError, ValueError, IndexError, TypeError, BaseExceptionReader) as cust_e:
                    raise BaseExceptionReader("Unable to get the data from file " +
                                              str(self.file)) from cust_e

                # update of the extracted parameters with the actual values
                self._extracted_parameters_dict.update(
                    {zone: {
                        "from_time": extracted_data["timestamp_vect"][0],
                        "to_time": extracted_data["timestamp_vect"][-1],
                        "time_type": "timestamp",
                        "from_dist": extracted_data["distance_vect"][0],
                        "to_dist": extracted_data["distance_vect"][-1],
                        "dist_type": "meter",
                        "remove_redundancy": remove_redundancy,
                        "offset_compensation": offset_compensation,
                        "concatenate": False,
                    }})

                # formatting of the final result
                final_res.update({zone: extracted_data})

        return final_res

    def extract_concat(
            self,
            from_time: Optional[float] = None,
            to_time: Optional[float] = None,
            time_type: str = "timestamp",
            from_dist: Optional[float] = None,
            to_dist: Optional[float] = None,
            dist_type: str = "meter",
            offset_compensation: bool = True,
            zones: Union[str, list] = "all") -> Dict:
        """
        Extracts and concatenates data from the file between selected values.
        Redundancy is automatically removed before concatenation.
        Returns the 'data' as a 2D concatenated matrix.
        A 'time_vect' is generated. It's the vector of the timestamps associated to each 'data'.
        This vector is calculated based on the timestamp of the first point, and the 'temporal_spacing'. 

        Depending on the time_type:
        - ("timestamp"): Extracts and concatenates data between (inclusive)
            specified unix-time (timestamp).
            Enable intra-block cutting.
        - ("relative"): Like for "timestamp", but "from_time" and "to_time"
            are defined relatively to the timestamp of the first block of the file.
            Enable intra-block cutting.
        - ("index"): Extracts and concatenates blocks between (inclusive)
            the indexes “from_time” and “to_time” in the list of all timestamps.
            Does NOT enable intr-block cutting.

        Depending on the dist_type:
        - ("meter"): Cut the data between (inclusive) 2 distance
            in meter after recreating the distance_vector.
        - ("index"): Cut the data between (inclusive) 2 channels.

        Args:
            from_time (float, optional): Start time for extraction.
                If None, start at the timestamp of the first block.
                Defaults to None.
            to_time (float, optional): End time for extraction.
                If None, end at the timestamp of the last block.
                Defaults to None.
            time_type (str, optional): Mode for interpreting from_time and to_time values.
                Options are "timestamp", "index" or "relative".
                Defaults to "timestamp".
            from_dist (float, optional): Start distance for extraction.
                If None, start at the first distance value.
                Defaults to None.
            to_dist (float, optional): End distance for extraction.
                If None, end at the last distance value.
                Defaults to None.
            dist_type (str, optional): Mode for interpreting distance values.
                Options are "meter" or "index".
                Defaults to "meter".
            offset_compensation (bool, optional): Whether to compensate for the
                offset of "strain" data.
                If False, no compensation is applied.
                If data_type is not "strain", no compensation is applied.
                If True, if the data_type is "strain", an offset will be applied to the values.
                The offset vector is saved in data_dict.
                Defaults to True.
            zones (str | list, optional): Zone(s) to extract data from.
                If "all", all zones will be read. Available zones can be found in list_zones.
                Defaults to "all".

        Raises:
            TypeError: If any input is of the wrong type.
            ValueError: If any input is invalid (e.g., to_time < from_time).
            OSError: If an I/O-related error occurs.
            MemoryError: If the size of would not nit in the RAM space.
            BaseExceptionReader: If the function cannot retrieve data.

        Returns:
            dict:
                keys:
                    - "data": a 2D numpy.ndarray,
                    - "distance_vect": a 1D numpy.ndarray,
                    - "time_vect": a 1D numpy.ndarray,
                    - "timestamp_vect": a 1D numpy.ndarray,
                    - "remove_redundancy": bool,
                    - "offset_compensation": bool,
        """
        user_inputs = {
            "from_time": (from_time, type(None)),
            "to_time": (to_time, type(None)),
            "time_type": (time_type, str),
            "from_dist": (from_dist, type(None)),
            "to_dist": (to_dist, type(None)),
            "dist_type": (dist_type, str),
            "remove_redundancy": (True, bool),
            "offset_compensation": (offset_compensation, bool),
            "concatenate": (True, bool),
            "zones": (zones, str),
        }
        # checking of the inputs
        try:
            if not self.file:
                raise ValueError("No file specified")
            self.__check_parameters(**user_inputs)
        except (ValueError, TypeError) as check_error:
            raise check_error
        if zones == "all":
            zones_to_set = self._list_zones
        else:
            if isinstance(zones, str):
                zones = [zones]
            zones_to_set = zones

        final_res = {}

        for zone in self._list_zones:
            if zone in zones_to_set:

                # update od user_parameters_dict
                user_inputs.pop("zones")
                user_parameters = {
                    key: val[0] for key, val in user_inputs.items()
                }
                self._user_parameters_dict.update(
                    {zone: user_parameters})

                try:
                    # setting of the indexes in self._data_dict
                    self.__set_indexes(
                        zone,
                        from_time=from_time,
                        to_time=to_time,
                        time_type=time_type,
                        from_dist=from_dist,
                        to_dist=to_dist,
                        dist_type=dist_type,
                    )

                    # checking shape to prevent memory failure
                    future_shape = (
                        self._data_dict[zone]["extracted_timestamp"].shape[0],
                        self._param_dict[zone]["block_time_size_wo"],
                        self._data_dict[zone]["extracted_distance"].shape[0])
                    if not self.__can_allocate_array(future_shape, dtype=np.float32):
                        raise MemoryError(
                            "Insufficient memory for the extraction. Allocation would fail.")

                    # extraction of the blocks
                    extracted_data, offset_matrix = self.__extract_block(
                        zone, remove_redundancy=True, offset_compensation=offset_compensation)
                    if not extracted_data or extracted_data is None:
                        raise TypeError("Extracted data is empty")
                    self._data_dict[zone].update(
                        {"offset_matrix": offset_matrix})

                    # concatenation and cutting of the blocks
                    concatenated_data = self.__cut_and_concatenate(
                        zone,
                        extracted_data,
                        from_time=from_time,
                        to_time=to_time,
                        time_type=time_type)
                    if not concatenated_data or concatenated_data is None:
                        raise TypeError("Extracted data is empty")
                    concatenated_data.update({
                        "remove_redundancy": True,
                        "offset_compensation": offset_compensation,
                    })

                except OSError as ose:
                    raise ose
                except (KeyError, ValueError, IndexError, TypeError, BaseExceptionReader) as cust_e:
                    raise BaseExceptionReader("Unable to get the data from file " +
                                              str(self.file)) from cust_e

                # update of the extracted parameters with the actual values
                self._extracted_parameters_dict.update(
                    {zone: {
                        "from_time": concatenated_data["time_vect"][0],
                        "to_time": concatenated_data["time_vect"][-1],
                        "time_type": "timestamp",
                        "from_dist": concatenated_data["distance_vect"][0],
                        "to_dist": concatenated_data["distance_vect"][-1],
                        "dist_type": "meter",
                        "remove_redundancy": True,
                        "offset_compensation": offset_compensation,
                        "concatenate": True,
                    }})

                # formatting of the final result
                final_res.update({zone: concatenated_data})

        return final_res

    def quick_view(
            self,
            extracted_data: dict,
            param_dict: dict,
            data_dict: dict,
            rotate: bool = False,
            cmap: Optional[str] = None,
            cmap_min_max: Optional[List[Union[float, int]]] = None,
            block: bool = True) -> None:
        """
        Display the extracted data in a window for a quick overview.
        Blocks of data will be displayed as an animation.

        Args:
            extracted_data (dict): The dictionnary returned by 'extract_blocks' or 'extract_concat'
            param_dict (dict): The parameter dictionnary variable ('instance.param_dict').
            data_dict (dict): The data dictionnary variable ('instance.data_dict').
            rotate (bool, optional): If True, transpose the data before displaying it.
                An auto-identification of the axis is done based on their shape.
                Defaults to False.
            cmap (Optional[str], optional): The registered colormap name used to map scalar data to colors.
                If None, the default cmap will be used ('viridis').
                Defaults to None.
            cmap_min_max (Optional[List[Union[float, int]]], optional): Define the data range that the colormap covers.
                By default (None), the colormap covers the [5%-95%] value range of the supplied data.
                Defaults to None.
            block (bool, optional): Whether to wait for the figure to be closed before returning.
                If True block and run the GUI main loop until all figure windows are closed.
                If False ensure that all figure windows are displayed and return immediately.
                In this case, you are responsible for ensuring that the event loop is running to have responsive figures
                Defaults to True.

        Raises:
            TypeError: If any input is of the wrong type.
            ValueError: If any input is invalid (e.g., start block < 0).
        """
        user_inputs = {
            "extracted_data": (extracted_data, None),
            "param_dict": (param_dict, None),
            "data_dict": (data_dict, None),
            "rotate": (rotate, bool),
            "cmap": (cmap, type(None)),
            "cmap_min_max": (cmap_min_max, type(None)),
            "block": (block, bool),
        }
        try:
            self.__check_parameters(**user_inputs)
        except (ValueError, TypeError) as check_error:
            raise check_error

        for zone in extracted_data:
            figure_title = param_dict[zone]["data_type"]

            array_2_disp = extracted_data[zone]["data"]
            if array_2_disp.ndim == 3:
                block_format = True
                time_vect = extracted_data[zone]["timestamp_vect"]
            elif array_2_disp.ndim == 2:
                block_format = False
                time_vect = extracted_data[zone]["time_vect"]
                array_2_disp = np.expand_dims(array_2_disp, axis=0)
            else:
                raise TypeError(
                    f"Expected array of dimension 2 or 3, and not dimension {array_2_disp.ndim}.")

            dist_vect = extracted_data[zone]["distance_vect"]

            if cmap_min_max is not None:
                vmin, vmax = cmap_min_max
            else:
                vmin, vmax = None, None

            fig, ax = plt.subplots()
            plt.title(figure_title)

            ims = []
            for idx in np.arange(array_2_disp.shape[0]):
                if vmin is None and vmax is None:
                    vmin, vmax = np.percentile(array_2_disp[idx], [5, 95])

                if rotate:
                    data_2_disp = np.transpose(array_2_disp[idx])
                else:
                    data_2_disp = array_2_disp[idx]

                xaxis = "distance" if data_2_disp.shape[1] == dist_vect.shape[0] else "time"

                extent = [None, None, None, None]

                if block_format:
                    time_0 = 0
                    time_1 = round(1/param_dict[zone]["block_rate"], 3)
                    title = f"Relative Time (s)"
                else:
                    time_0 = datetime.datetime.fromtimestamp(
                        time_vect[0], tz=datetime.timezone.utc)
                    time_1 = datetime.datetime.fromtimestamp(
                        time_vect[-1], tz=datetime.timezone.utc)
                    title = f"Absolute Time (utc) : {time_0.strftime('%Y/%b/%d')}"
                    if time_0.date() != time_1.date():
                        title += f" - {time_1.strftime('%Y/%b/%d')}"

                if xaxis == "distance":
                    extent[0] = dist_vect[0]
                    extent[1] = dist_vect[-1]
                    extent[2] = time_1
                    extent[3] = time_0
                    plt.xlabel('Distance (m)')
                    plt.ylabel(title)
                else:
                    extent[2] = dist_vect[-1]
                    extent[3] = dist_vect[0]
                    extent[0] = time_0
                    extent[1] = time_1
                    plt.xlabel(title)
                    plt.ylabel('Distance (m)')

                imshow_params = {
                    "cmap": cmap,
                    "alpha": 1,  # opaque
                    "vmin": vmin,
                    "vmax": vmax,
                    "extent": extent,
                    "origin": "upper",  # {'upper', 'lower'}
                    "aspect": "auto",  # {'equal', 'auto'} or float or None
                    # "norm": "linear",
                    # "interpolation": "lanczos",  # {'none', 'auto', 'nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos', 'blackman'}
                    # "interpolation_stage": "auto",  # {'auto', 'data', 'rgba'}
                    # "filterrad": 4.0,  # float > 0, default: 4.0 -> filter radius for filters that have a radius parameter {'sinc', 'lanczos' or 'blackman'}
                    # "resample": False,  # When True, use a full resampling method. When False, only resample when the output image is larger than the input image.
                }

                im = ax.imshow(data_2_disp, **imshow_params)

                if not block_format:
                    if xaxis == "distance":
                        ax.yaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M:%S\n(ms: %f)'))
                    else:
                        ax.xaxis.set_major_formatter(
                            mdates.DateFormatter('%H:%M:%S\n(ms: %f)'))
                        for label in ax.get_xticklabels(which='major'):
                            label.set(rotation=30, horizontalalignment='right')

                ims.append([im])

            if block_format is True:
                ani = animation.ArtistAnimation(
                    fig, ims, interval=500, blit=True, repeat_delay=1500)
            plt.show(block=block)

    def write_extracted(
            self,
            path_name: str,
            extracted_data: dict,
            hdf5_dict: dict,
            param_dict: dict,
            data_dict: dict,
            chunk_shape: Optional[tuple] = None) -> bool:
        """
        Allows the writing of extracted data as hdf5 file, respecting the FEBUS Optics standard.
        This function writes data using the blocks approach.
        If the extracted data is concatenated, it will be written as a single block.
        The attributes of the file are extracted from the original file, and some of them are modified to correspond to the extracted data.

        Args:
            path_name (str): Absolute path to the **NEW** hdf5 file.
            extracted_data (dict): The dictionnary returned by 'extract_blocks' or 'extract_concat'
            hdf5_dict (dict): Dict where the structure of the hdf5 file is stored ('instance.hdf5_dict').
            param_dict (dict): The parameter dictionnary variable ('instance.param_dict').
            data_dict (dict): The data dictionnary variable ('instance.data_dict').
            chunk_shape (tuple, optional): Chunk shape as a tuple, or None to enable auto-chunking.
                See the h5py documentation for more informations.
                Defaults to None.

        Raises:
            TypeError: If any input is of the wrong type.
            ValueError: If any input is invalid (e.g., already existing file).
            OSError: OS-related error during writing of data (e.g., write permissions not granted).
            BaseExceptionReader: If the function is unable to write the data.

        Returns:
            bool: True if the writing was succesful
        """
        user_inputs = {
            "extracted_data": (extracted_data, None),
            "hdf5_dict": (hdf5_dict, None),
            "param_dict": (param_dict, None),
            "data_dict": (data_dict, None),
            "chunk_shape": (chunk_shape, type(None)),
        }
        try:
            self.__check_parameters(**user_inputs)
        except (ValueError, TypeError) as check_error:
            raise check_error

        if os.path.isabs(path_name):
            new_path = Path(path_name)
        else:
            new_path = Path(os.path.abspath(path_name))
        new_dir = new_path.parent

        if new_path.is_file():
            raise ValueError("Already existing file")
        if not new_dir.exists() or not new_dir.is_dir():
            raise ValueError(
                f"Parent directory does not exist or is not a directory:\n{new_dir}")
        if not os.access(new_dir, os.W_OK):
            raise OSError(
                f"Write permissions are not granted for the directory:\n{new_dir}")

        chunk_size = []
        for zone in extracted_data:
            if chunk_shape is None:
                _chunk = (
                    1,
                    extracted_data[zone]["data"].shape[-2],
                    extracted_data[zone]["data"].shape[-1])
                num_elements = np.prod(_chunk)
                dtype_size = np.dtype(np.float32).itemsize
                # required_memory
                if not 10000 < num_elements * dtype_size < 10000000:
                    _chunk = True

                chunk_size.append(_chunk)

            else:
                chunk_size.append(chunk_shape)

        try:
            new_hdf5_dict = copy.deepcopy(hdf5_dict)

            self.__write_as_h5(
                new_path,
                extracted_data,
                new_hdf5_dict,
                param_dict,
                data_dict,
                chunk_size,
            )
            return os.path.isfile(new_path)

        except (FileExistsError, FileNotFoundError) as fer:
            raise BaseExceptionReader(
                f"Unable to write {str(new_path)} as hdf5 file.") from fer
        except OSError as ose:
            raise ose

    def __initialize_attributes(self):
        """
        Initialize the attibutes or restore them to their "blank" state
        """
        self._hdf5_dict: Dict = {}
        self._param_dict: Dict = {}
        self._data_dict: Dict = {}
        self._list_zones: list = []
        self._data_type = None
        self._user_parameters_dict: Dict = {}
        self._extracted_parameters_dict: Dict = {}

    @staticmethod
    def __type_checking(**kwargs):
        """
        Check the type of the arguments.

        Raises:
            TypeError
        """
        types_dict = {
            "from_dist": (Union[float, int, np.integer, np.floating]),
            "to_dist": (Union[float, int, np.integer, np.floating]),
            "from_time": (Union[float, int, np.integer, np.floating]),
            "to_time": (Union[float, int, np.integer, np.floating]),
            "dist_type": (str),
            "time_type": (str),
            "remove_redundancy": (bool),
            "offset_compensation": (bool),
            "concatenate": (bool),
            "zones": (Union[str, list]),
            "data": (np.ndarray),
            "distance_vect": (np.ndarray),
            "time_vect": (np.ndarray),
            "timestamp_vect": (np.ndarray),
            "extracted_data": (dict),
            "chunk_shape": (tuple),
            "hdf5_dict": (dict),
            "param_dict": (dict),
            "data_dict": (dict),
            "rotate": (bool),
            "cmap": (str),
            "cmap_min_max": (list),
            "block": (bool),
        }
        for obj, (val, default_type) in kwargs.items():
            valid_types = types_dict[obj]
            if default_type is not None and isinstance(val, default_type):
                continue

            if not isinstance(val, valid_types):
                raise TypeError(
                    f"Wrong type {type(val)} detected for {obj}. \
                    \nAccepeted type are {valid_types}.")

    def __check_parameters(self, **kwargs) -> None:
        """
        Check the validity of the parameters.
        Checking the type, and if needed the values.

        Parameterrs that can be checked:
            "from_dist"
            "to_dist"
            "from_time"
            "to_time"
            "dist_type"
            "time_type"
            "remove_redundancy"
            "offset_compensation"
            "concatenate"
            "zones"
            "data"
            "distance_vect"
            "time_vect"
            "timestamp_vect"
            "extracted_data"
            "chunk_shape"
            "hdf5_dict"
            "param_dict"
            "data_dict"

        Raises:
            ValueError
            TypeError
        """
        # checking for types:
        self.__type_checking(**kwargs)

        # checking for wrong values
        if "from_dist" in kwargs and "to_dist" in kwargs:
            from_dist = kwargs["from_dist"][0]
            to_dist = kwargs["to_dist"][0]
            if isinstance(from_dist, bool):
                raise TypeError(
                    f"Wrong type {type(from_dist)} detected for from_dist.\nBoolean not accepeted.")
            if isinstance(to_dist, bool):
                raise TypeError(
                    f"Wrong type {type(to_dist)} detected for to_dist.\nBoolean not accepeted.")
            if None not in [from_dist, to_dist] and from_dist > to_dist:
                raise ValueError(
                    f"from_dist > to_dist: {from_dist} > {to_dist}")
        if "from_time" in kwargs and "to_time" in kwargs:
            from_time = kwargs["from_time"][0]
            to_time = kwargs["to_time"][0]
            if isinstance(from_time, bool):
                raise TypeError(
                    f"Wrong type {type(from_time)} detected for from_time.\nBoolean not accepeted.")
            if isinstance(to_time, bool):
                raise TypeError(
                    f"Wrong type {type(to_time)} detected for to_time.\nBoolean not accepeted.")
            if None not in [from_time, to_time] and from_time > to_time:
                raise ValueError(
                    f"from_time > to_time: {from_time} > {to_time}")
        if "dist_type" in kwargs:
            dist_type = kwargs["dist_type"][0]
            if dist_type not in ["meter", "index"]:
                raise ValueError(
                    f"Wrong value {dist_type} detected for dist_type. \
                    \nAccepeted values are meter or index.")
        if "time_type" in kwargs:
            time_type = kwargs["time_type"][0]
            if time_type not in ["timestamp", "index", "relative"]:
                raise ValueError(
                    f"Wrong value {time_type} detected for time_type. \
                    \nAccepeted values are timestamp, index or relative.")
        if "zones" in kwargs:
            zones = kwargs["zones"][0]
            if zones != "all":
                if isinstance(zones, str):
                    zones = [zones]
                if any(zone not in self._list_zones for zone in zones):
                    raise ValueError(
                        f"Inappropriate zones names: {zones}.\nShould be in: {self._list_zones}")

    def __extract_attribut(self) -> None:
        """
        Extract attributs and save them to self._param_dict.
        Then return h5dict and timestamp vect.

        Raises:
            BaseExceptionReader: If unable to extract attributes
        """
        try:
            with h5py.File(self.file, "r") as data_out:
                timestamp, h5dict = self.source.get_h5py_dict(data_out)

            if h5dict is None:
                raise TypeError("h5dict is None")
            setattr(self, "_hdf5_dict", h5dict.copy())

            if timestamp is None:
                raise TypeError("timestamp is None")
            self._data_dict["timestamp"] = timestamp.copy()

            _param_dict = self.source.get_attribut_dict(timestamp, h5dict,)

            if self._param_dict is None:
                raise TypeError("_param_dict is None")
            setattr(self, "_param_dict", _param_dict.copy())

            for zone in _param_dict["list_zones"]:
                extent = _param_dict[zone]["extent"]
                spacing = _param_dict[zone]["spacing"]
                origin = _param_dict[zone]["origin"]
                dist_vect = np.linspace(
                    start=extent[0]*spacing[0]+origin[0],
                    stop=extent[1]*spacing[0]+origin[0],
                    num=extent[1]-extent[0]+1,
                    endpoint=True,
                    dtype=np.float32
                )
                self._data_dict[f"distance_{zone}"] = dist_vect.copy()
                self._data_dict[zone] = {}

        except (KeyError, TypeError, ValueError, IndexError) as cer:
            raise BaseExceptionReader("Unable to extract attributes") from cer
        except OSError as ose:
            raise BaseExceptionReader("Unable to open file") from ose

    def __set_indexes(
        self,
        zone: str,
        from_time: Optional[float] = None,
        to_time: Optional[float] = None,
        time_type: Optional[str] = "timestamp",
        from_dist: Optional[float] = None,
        to_dist: Optional[float] = None,
        dist_type: Optional[str] = "meter",
    ) -> None:
        """
        Internal setting of the reading parameters

        Args:
            zone (str): Zone to set the reader.
            from_time (float, optional): Start time to read.
                If None, start at the first time value. Defaults to None.
            to_time (float, optional): End time to read.
                If None, end at the last time value. Defaults to None.
            time_type (str, optional): Setting mode for the from_time and to_time values.
                Between "timestamp"(absolute=epoch-time), "index"(block)
                and "relative" (relative-time in sec).
                Defaults to "timestamp".
            from_dist (float, optional): Start distance to read.
                If None, start at the first distance value. Defaults to None.
            to_dist (float, optional): End distance to read.
                If None, end at the last distance value. Defaults to None.
            dist_type (str, optional): Setting mode for the from_dist and to_dist values.
                Options are "meter" (absolute) and "index" (channel).
                Defaults to "meter".

        Raises:
            ValueError: from_time must not be None
        """
        dist_vect = self._data_dict[f"distance_{zone}"]

        idx_from_dist = self.__find_in_array(
            nparray=dist_vect, value=from_dist, vtype=dist_type, start=True)
        idx_to_dist = self.__find_in_array(
            nparray=dist_vect, value=to_dist, vtype=dist_type, start=False)

        tstp_vect = self._data_dict["timestamp"].copy()

        block_time_size_wo = self.param_dict[zone]["block_time_size_wo"]
        block_time_size_no = self.param_dict[zone]["block_time_size_no"]
        temporal_spacing = self.param_dict[zone]["temporal_spacing"]

        if temporal_spacing is not None:
            if self._param_dict[zone]["timestamp_position"] == "start":
                shift_from_overlap = (
                    (block_time_size_wo-block_time_size_no) * temporal_spacing * 0.5)
            elif self._param_dict[zone]["timestamp_position"] == "middle":
                shift_from_overlap = (
                    - block_time_size_no * temporal_spacing * 0.5)

            tstp_vect += shift_from_overlap

        idx_from_time = self.__find_in_array(
            nparray=tstp_vect, value=from_time, vtype=time_type, start=True)

        if temporal_spacing is not None:
            tstp_vect += (block_time_size_no - 1) * temporal_spacing

        idx_to_time = self.__find_in_array(
            nparray=tstp_vect, value=to_time, vtype=time_type, start=False)

        self._data_dict[zone]["extracted_distance"] = dist_vect[
            idx_from_dist: idx_to_dist + 1]
        self._data_dict[zone]["extracted_timestamp"] = self._data_dict["timestamp"][
            idx_from_time: idx_to_time + 1]
        self._data_dict[zone]["index"] = [
            idx_from_time,
            idx_to_time,
            idx_from_dist,
            idx_to_dist,
            0,
            block_time_size_wo-1,
        ]

    def __extract_block(
            self,
            zone: str,
            remove_redundancy: bool,
            offset_compensation: bool) -> Tuple[dict, np.ndarray]:
        """
        Internal function to extract blocks of data in dict.

        Args:
            zone (str): Zone to read from.
            remove_redundancy (bool)
            offset_compensation (bool)

        Raises:
            ValueError

        Returns:
            tuple: (extracted_data, offset_matrix)
                dict: extracted_data
                    keys: "data", "distance_vect", "timestamp_vect", "remove_redundancy", "offset_compensation"
                Union[numpy.ndarray, bool]: offsetted_data or False
        """

        data_index = self._data_dict[zone]["index"]

        data_type = self._param_dict[zone]["data_type"]
        data_path = self._hdf5_dict[data_type]["path"]

        with h5py.File(self._file, "r") as data_out:  # type: ignore

            # block_extraction
            extracted_data_blocks = data_out[data_path][
                data_index[0]: data_index[1]+1,
                data_index[4]: data_index[5]+1,
                data_index[2]: data_index[3]+1,]

            if extracted_data_blocks.ndim != 3:
                raise ValueError(
                    f"Expected 3 dim for dataset, get {extracted_data_blocks.ndim} dim")

        if offset_compensation:
            # check for gauge_length, derivation_time and shape to know if it is Strain data
            if (
                self._param_dict[zone]["gauge_length"] is not None and
                self._param_dict[zone]["derivation_time"] is None and
                extracted_data_blocks.shape[1] != 1 and
                self._param_dict[zone]["block_time_size_no"] != self._param_dict[zone]["block_time_size_wo"]
            ):
                extracted_data_blocks, offset_matrix = self.__strain_offset_removal(
                    extracted_data_blocks, zone)
            else:
                offset_matrix = False
        else:
            offset_matrix = False

        if remove_redundancy:
            np_pts_in_block = extracted_data_blocks.shape[1]
            idx_rmv_st, idx_rmv_nd = self.__nb_pts_to_remove(
                zone, np_pts_in_block)
            extracted_data_blocks = extracted_data_blocks[:,
                                                          idx_rmv_st: idx_rmv_nd, :]
            self._data_dict[zone]["index"][4] = idx_rmv_st
            self._data_dict[zone]["index"][5] = idx_rmv_nd-1

        extracted_data = {
            "data": extracted_data_blocks,
            "distance_vect": self._data_dict[zone]["extracted_distance"],
            "timestamp_vect": self._data_dict[zone]["extracted_timestamp"],
            "remove_redundancy": remove_redundancy,
            "offset_compensation": offset_compensation,
        }
        return extracted_data, offset_matrix

    def __cut_and_concatenate(
            self,
            zone: str,
            extracted_blocks: dict,
            from_time: Optional[float],
            to_time: Optional[float],
            time_type: str) -> dict:
        """
        Concatenate the data and cut at the milliseconde.

        Args:
            zone (str): Zone to read from.
            extracted_blocks (dict): Result from "get_data".
                keys : "data", "distance_vect", "timestamp_vect", "remove_redundancy"
            from_time (Union[float, None]): Start time to read.
                If None, start at the first time value.
            to_time (Union[float, None]): End time to read.
                If None, end at the last time value.
            time_type (str): Setting mode for the from_time and to_time values.
                Between "timestamp"(absolute=epoch-time), "index"(block)
                and "relative" (relative-time in sec).

        Returns:
            dict: extracted_data
                keys: "data", "distance_vect", "time_vect", "timestamp_vect"
        """
        data = extracted_blocks["data"]
        timestamp_vect = extracted_blocks["timestamp_vect"]
        distance_vect = extracted_blocks["distance_vect"]

        block_time_size_no = self._param_dict[zone]["block_time_size_no"]
        temporal_spacing = self._param_dict[zone]["temporal_spacing"]
        timestamp_position = self._param_dict[zone]["timestamp_position"]

        index = self._data_dict[zone]["index"]

        data = np.reshape(
            data, (data.shape[0]*data.shape[1], data.shape[2]))

        # creation of militime_vect:
        militime_vect = self.__create_time_vector(
            data, extracted_blocks["timestamp_vect"], zone)

        # init
        idx_from_time = 0 if from_time is None else None
        idx_to_time = militime_vect.shape[0]-1 if to_time is None else None

        if time_type == "index":

            if from_time is not None:
                # tstp of idx "from_time"
                from_time = self._data_dict["timestamp"][from_time]

                if temporal_spacing is not None:
                    if timestamp_position == "middle":
                        # tstp middle - half a block to be at the start the block
                        from_time -= (block_time_size_no * temporal_spacing/2)
                    else:
                        # index[4] : start_index for cutting block redundancy
                        from_time += index[4] * temporal_spacing

            if to_time is not None:
                # tstp of idx "to_time"
                to_time = self._data_dict["timestamp"][to_time]

                if temporal_spacing is not None:
                    if timestamp_position == "middle":
                        # tstp "middle" + half a block to be at the start the block
                        to_time += (block_time_size_no - 1) * \
                            temporal_spacing * 0.5
                    else:
                        # index[5] : end_index for cutting block redundancy
                        to_time += (index[5] - 1) * temporal_spacing

            # now corresponding to timestamp
            time_type = "timestamp"

        elif time_type == "relative":
            # relative to the start of the file
            start_of_file = self._data_dict["timestamp"][0]

            if temporal_spacing is not None:
                if timestamp_position == "middle":
                    # tstp middle -> remove half a block to be at the start the block
                    start_of_file -= (block_time_size_no * temporal_spacing/2)
                else:
                    # index[4] : start_index for cutting block redundancy
                    start_of_file += index[4] * temporal_spacing

            if from_time is not None:
                from_time += start_of_file
            if to_time is not None:
                to_time += start_of_file
            # now corresponding to timestamp
            time_type = "timestamp"

        # seek index of from_time and to_time in militime_vect if needed
        if idx_from_time is None:
            idx_from_time = self.__find_in_array(
                nparray=militime_vect, value=from_time, vtype=time_type, start=True)
        if idx_to_time is None:
            idx_to_time = self.__find_in_array(
                nparray=militime_vect, value=to_time, vtype=time_type, start=False)

        extracted_data = {
            "data": data[
                idx_from_time:idx_to_time+1, :],
            "distance_vect": distance_vect,
            "time_vect": militime_vect[
                idx_from_time:idx_to_time+1],
            "timestamp_vect": timestamp_vect[
                idx_from_time//block_time_size_no: idx_to_time//block_time_size_no+1],
        }

        return extracted_data

    def __create_time_vector(
            self,
            data: np.ndarray,
            timestamp_vect: np.ndarray,
            zone: str) -> np.ndarray:
        """
        Create the vector of timestamp associated with each time-value of data.

        Args:
            data (numpy.ndarray): The reshaped 2D-matrixof data of the extracted blocks
            timestamp_vect (numpy.ndarray): The timestamp_vect from the extracted blocks
            zone (str): Zone to read from.

        Returns:
            numpy.ndarray: array of 'num' equally spaced timestamps in the closed interval ['start', 'stop']
        """

        block_size_wo = self._param_dict[zone]["block_time_size_wo"]
        idx_rmv_st = self._data_dict[zone]["index"][4]

        frst_tstp = timestamp_vect[0]
        nb_time_pts = data.shape[0]

        if block_size_wo == 1:
            spacing = 1/self._param_dict[zone]["block_rate"]
            frst_time = frst_tstp
        else:
            spacing = self._param_dict[zone]["temporal_spacing"]
            if self._param_dict[zone]["timestamp_position"] == "start":
                frst_time = frst_tstp + spacing * idx_rmv_st
            else:
                # if timestamp_position = "start" -> from middle to edge then same
                frst_time = frst_tstp - \
                    (block_size_wo*spacing/2) + spacing * idx_rmv_st

        last_time = frst_time + (nb_time_pts-1) * spacing

        return np.linspace(
            start=frst_time, stop=last_time, num=nb_time_pts, dtype=np.float64)

    def __strain_offset_removal(self, data: np.ndarray, zone: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select and remove the strain_offset for each block (except the first one).
        The offsets are calculated by removing the first redundancy of the
        previous block to the first data of the block the strain_offset is calculated on.

        Block structuration:
        -----||||||||||-----
                  -----||||||||||-----
                            -----||||||||||-----

        -----||||||||||-----
             ^         ^
           first     first
           data     redundancy

        Args:
            data (numpy.ndarray): extracted_data_blocks.
            zone (str): Zone to read from.

        Returns:
            tuple: (data, offsetted_data)
                numpy.ndarray: data
                numpy.ndarray: offsetted_data
        """

        # redundancy of blocks
        np_pts_in_block = data.shape[1]
        idx_rmv_st, idx_rmv_nd = self.__nb_pts_to_remove(zone, np_pts_in_block)

        # offsetted_data = data.copy()
        first_data_of_block = data[1:, idx_rmv_st:idx_rmv_st+1, :]
        first_redu_of_block = data[:-1, idx_rmv_nd-1:idx_rmv_nd, :]

        offsets = first_data_of_block - first_redu_of_block
        offsets = np.concatenate(
            (np.zeros((1, 1, offsets.shape[2]), dtype=np.float32), offsets), axis=0)

        offsets_sum = np.cumsum(offsets, axis=0)

        np.subtract(data, offsets_sum, out=data)

        return data, offsets_sum

    def __nb_pts_to_remove(self, zone: str, nb_pts_in_block: int) -> Tuple[int, int]:
        """
        Compute the number of points to remove from a block to remove the redundancy.

        Args:
            zone (str): Zone to read from.
            nb_pts_in_block (int): time-length of a block.

        Raises:
            BaseExceptionReader: Shape inconsistency between block and parameters

        Returns:
            (int, int): first and last indexes to use to remove the redundancy.
        """
        # wo = with overlapp, no = no overlapp
        block_time_size_wo = self._param_dict[zone]["block_time_size_wo"]
        block_time_size_no = self._param_dict[zone]["block_time_size_no"]
        if nb_pts_in_block not in [block_time_size_wo, block_time_size_no]:
            raise BaseExceptionReader(
                f"Incoherent data time shape. Expect {block_time_size_wo} \
                    but actual size is {nb_pts_in_block}")

        to_remove = block_time_size_wo - block_time_size_no
        if block_time_size_wo == block_time_size_no:
            to_remove_st = 0
            to_remove_nd = 0
        else:
            # index of timestamp shifted to the left in case of even number
            # | - - - t - - - -|  original -> need to remove 3
            # | # - - t - - # #|  removing 1 from the left and 2 from the right
            to_remove_st = max(
                0, int((block_time_size_wo - block_time_size_no)/2))
            to_remove_nd = to_remove - to_remove_st

        return to_remove_st, block_time_size_wo - to_remove_nd

    @staticmethod
    def __find_in_array(
            nparray: np.ndarray,
            value: Optional[Union[int, float]] = None,
            vtype: str = "index",
            start: bool = True) -> int:
        """
        Find the index of a given value in an array.

        Args:
            nparray (numpy.ndarray): array to search in
            value (Union[int, float], optional): what to search.
                                                 Defaults to None.
            vtype (str, optional): type of the value. Can be "index", "relative" or "absolute".
                                   Defaults to "index".
            start (bool, optional): True if it's the "from" value, False if it's the "to".
                                    Defaults to True.

        Returns:
            int: index of the value.
        """

        if value is None:
            if start:
                idx = 0
            else:
                idx = len(nparray)-1
            return idx

        if vtype == "index":
            return int(value)

        if vtype == "relative":
            value += nparray[0]

        idx = int(np.searchsorted(nparray, value))

        idx = min(idx, len(nparray) - 1)

        if start and nparray[idx] > value:
            idx -= 1

        return max(0, idx)

    @staticmethod
    def __can_allocate_array(shape: tuple, dtype: np.dtype = np.float32) -> bool:
        """
        Check if a numpy array of the given shape and data type can be allocated in memory.

        This function calculates the memory required for a numpy array with the specified
        shape and data type. It compares the required memory to the available system memory
        to determine if allocation is possible.

        Args:
            shape (tuple): The shape of the array, specified as a tuple of integers.
            dtype (numpy.dtype, optional): The desired data type of the array. Defaults to np.float32.

        Returns:
            bool: True if the memory required for the array is available in memory,
              False otherwise.
        """
        # Calculate the memory required for the array
        num_elements = np.prod(shape)
        dtype_size = np.dtype(dtype).itemsize
        required_memory = num_elements * dtype_size  # Total memory in bytes

        # Check available memory
        available_memory = psutil.virtual_memory().available  # Available memory in bytes
        return 1.4*required_memory < available_memory

    def __write_as_h5(
            self,
            new_path: str,
            extracted_data: dict,
            hdf5_dict: dict,
            param_dict: dict,
            data_dict: dict,
            chunk_size: List[Union[tuple, bool]],) -> None:
        """
        TODO

        Args:
            new_path (str): Absolute path to the **NEW** hdf5 file.
            extracted_data (dict): The dictionnary returned by 'extract_blocks' or 'extract_concat'
            hdf5_dict (dict): Dict where the structure of the hdf5 file is stored ('instance.hdf5_dict').
            param_dict (dict): The parameter dictionnary variable ('instance.param_dict').
            data_dict (dict): The data dictionnary variable ('instance.data_dict').
            chunk_shape (Optional[tuple], optional): Chunk shape or True to enable auto-chunking.
                The the h5py documentation for more informations

        Raises:
            ValueError
        """
        root = [key for key, value in hdf5_dict.items()
                if "File" in value["type"]][0]

        device = [key for key, value in hdf5_dict.items() if
                  hdf5_dict[root]["path"]+key == value["path"]
                  and "File" not in value["type"]][0]

        source = [key for key, value in hdf5_dict.items() if
                  hdf5_dict[device]["path"]+"/"+key == value["path"]][0]

        zones = [key for key, value in hdf5_dict.items() if
                 hdf5_dict[source]["path"]+"/"+key == value["path"] and
                 "Zone" in key and "/" not in key]

        data_names = [key for key, value in hdf5_dict.items() if
                      "Dataset" in value["type"]]
        data_names.remove("time")

        if not len(data_names) == len(zones) == len(chunk_size):
            raise ValueError(
                f"No coherent number of elements.\
                    \ndata_type_list:{len(data_names)}, \
                    zones: {len(zones)}, \
                    chunk_size: {chunk_size}")

        with h5py.File(new_path, "w") as my_file:

            # device group
            my_device = my_file.create_group(
                hdf5_dict[device]["path"].split("/")[-1]
            )
            # source group
            my_source = my_device.create_group(
                hdf5_dict[source]["path"].split("/")[-1])
            # source attributs
            for key, value in hdf5_dict[source].items():
                if key not in ["path", "parent", "type", "attributes"]:
                    my_source.attrs[key] = value

            time_data = None
            to_save_data = None

            for counter, zone in enumerate(zones):
                # zone group
                my_zone = my_source.create_group(
                    hdf5_dict[zone]["path"].split("/")[-1]
                )  # zone attributes

                self.source.set_attribut_dict(
                    hdf5_dict, param_dict, data_dict, extracted_data)

                for key, value in hdf5_dict[zone].items():
                    if key not in ["path", "parent", "type", "attributes"]:
                        my_zone.attrs[key] = value

                if extracted_data[zone]["data"].ndim == 3:
                    time_data = extracted_data[zone]["timestamp_vect"]
                    to_save_data = extracted_data[zone]["data"]

                elif extracted_data[zone]["data"].ndim == 2:
                    # check for the version
                    if "Version" not in my_zone.attrs:
                        # older than 2.3 -> timestamp at the start (no modif needed)
                        time_data = np.array(
                            [extracted_data[zone]["time_vect"][0]])
                    else:
                        # newer than 2.3 -> put the timestamp at the middle of the block
                        time_data = np.array(
                            [(extracted_data[zone]["time_vect"][0] +
                              extracted_data[zone]["time_vect"][-1] +
                                hdf5_dict[zone]["Spacing"][1]/1000)/2])
                    # force the 2D matrix to shape of a single 3D block
                    to_save_data = np.expand_dims(
                        extracted_data[zone]["data"], axis=0)

                if hdf5_dict[zone]["path"] in hdf5_dict[data_names[counter]]["path"]:
                    my_zone.create_dataset(
                        name=data_names[counter],
                        data=to_save_data,
                        chunks=chunk_size[counter])

            my_source.create_dataset(
                "time", data=time_data, chunks=(1))
