#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robin.guerry
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import numpy as np
from h5py import Dataset, File, Group

from febus_optics_lib.computation import ComputeData


class BaseExceptionPlugin(Exception, BaseException):
    """Base class for Plugin exception."""

    def __init__(self, msg):
        super().__init__(msg)


class PluginInterface(ABC):
    """Interface for plugins."""

    @staticmethod
    @abstractmethod
    def get_h5py_dict(data_out):
        """Abstract Method to implement"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_attribut_dict(timestamp, hdf5_dict):
        """Abstract Method to implement"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def write_as_h5(data, param, template, new_file):
        """Abstract Method to implement"""
        raise NotImplementedError


def h5py_dict_constructor(data: Union[File, Group, Dataset], h5dict: Dict[str, Any]) -> None:
    """
    Analyse an hdf5 file-structure and modify on the go the h5dict object.
    Recursive function.

    Args:
        data (File | Group | Dataset): data to be analyzed
        h5dict (Dict[str, Any]): dict where the structure of the data is stored on the go

    Raises:
        BaseExceptionPlugin
    """

    idx = -1
    name = data.name.split("/")[idx:]
    while "/".join(name) in list(h5dict.keys()):
        if "/".join(name) == data.name:
            raise BaseExceptionPlugin("redundancy in keys : "+data.name)
        idx -= 1
        name = data.name.split("/")[idx:]

    attributes = {}
    if isinstance(data, Dataset):
        attributes = {
            "path": data.name,
            "type": str(type(data)),
            "parent": data.parent.name,  # type: ignore
            "attributes": {
                "shape": data.shape,
                "ndim": data.ndim,
                "size": data.size,
                "dtype": str(data.dtype),
                "chunks": list(data.chunks) if data.chunks is not None else None
            }
        }
    elif isinstance(data, (File, Group)):
        attributes = {
            "path": data.name,
            "type": str(type(data)),
            "parent": data.parent.name,
        }

    attributes.update(dict(data.attrs.items()))  # type: ignore

    for key, value in attributes.items():
        if isinstance(value, (np.bytes_, bytes)):
            attributes[key] = value.decode()

    h5dict.update({"/".join(name): attributes})

    if isinstance(data, Group):
        for value in data.values():  # type: ignore
            h5py_dict_constructor(value, h5dict)  # type: ignore


class PluginFebus(PluginInterface):
    """
    Plugin to enable the reading or writting of febus-hdf5 file
    """

    @staticmethod
    def get_h5py_dict(data_out):
        """
        Construct a dictionary representing the structure of the HDF5 file and extract the timestamp.

        This method utilizes the `h5py_dict_constructor` to build a dictionary that 
        represents the structure of the HDF5 file. It also extracts the timestamp 
        from the file based on the provided `data_out` parameter. If the timestamp 
        is a scalar (0-dimensional), it is reshaped to a 1-dimensional array.

        Args:
            data_out (File | Group | Dataset): The HDF5 object from which to extract the data.

        Returns:
            tuple: A tuple containing:
                - timestamp (ndarray): The extracted timestamp from the HDF5 data.
                - h5dict (dict): The dictionary representing the HDF5 structure.
        """
        h5dict = {}
        h5py_dict_constructor(data_out, h5dict)
        timestamp = np.array(
            data_out[h5dict["time"]["path"]], dtype=float)
        if timestamp.ndim == 0:
            timestamp = timestamp.reshape(1)

        return timestamp, h5dict

    @staticmethod
    def get_attribut_dict(timestamp, hdf5_dict):
        """
        Construct a dictionary with detailed attributes for each zone in the HDF5 data.

        This method processes the provided HDF5 dictionary to extract attributes related
        to each zone, including physical properties (such as distance, overlap) and temporal
        properties (such as timestamp start/end times). It also calculates derived properties 
        such as block time size and sampling rate.

        Args:
            timestamp (ndarray): The timestamp values.
            hdf5_dict (dict): The dictionary containing the structure and attributes of 
                              the HDF5 data.

        Returns:
            dict: A dictionary with attributes for each zone, including metadata 
                  like optical index, block rate, temporal information, and units.

        Raises:
            TypeError: If the HDF5 file structure is not as expected or a required 
                       key is missing in the data.
        """

        for value in hdf5_dict.values():
            if "FreqRes" in value:
                value["BlockRate"] = value.pop("FreqRes")

        list_zones = [
            key for key in hdf5_dict.keys() if "Zone" in key and "/" not in key]

        # create a list of dataset types, excluding the 'time' key
        data_type_list = [
            key for key, value in hdf5_dict.items() if "Dataset" in value["type"]]
        data_type_list.remove("time")

        if len(data_type_list) == 0:
            raise TypeError("file of unknown data_type")

        # Initialize ComputeData object to calculate date and time
        comp_time = ComputeData()
        comp_time.set_raw_data(np.array([timestamp[0], timestamp[-1]]))
        comp_time_dict = comp_time.get_computed_data(date=True, time=True)

        attribut_dict = {}
        try:
            # Process each zone and extract relevant attributes
            attribut_dict["list_zones"] = list_zones
            for nb, zone in enumerate(list_zones):

                zone_attr = hdf5_dict[zone]

                # Calculate distances based on attributes
                distance_start = zone_attr["Extent"][0] * \
                    zone_attr["Spacing"][0] + zone_attr["Origin"][0]
                distance_end = zone_attr["Extent"][1] * \
                    zone_attr["Spacing"][0] + zone_attr["Origin"][0]

                # Check for overlap or use a default value
                overlap = zone_attr.get(
                    "Overlap",
                    zone_attr.get(
                        "BlockOverlap",
                        [100]
                    )
                )[0]

                # Calculate block rate and temporal spacing
                block_rate_hz = zone_attr["BlockRate"][0] / 1000
                t_spacing_s = zone_attr["Spacing"][1]/1000
                block_time_size_wo = 1 + zone_attr["Extent"][3] - \
                    zone_attr["Extent"][2]

                # Determine the block time size with No Overlap (no) after considering overlap or block-rate
                if block_time_size_wo == 1:
                    block_time_size_no = 1
                else:
                    if zone_attr["Extent"][2] == 0:
                        # it means the redundancy as not been removed
                        block_time_size_no = int(
                            round(block_time_size_wo / (1+(overlap/100)), 0))
                    else:
                        block_time_size_no = int(
                            round(1 / (block_rate_hz * t_spacing_s), 0))

                # Build the param dictionary
                zone_dict = {
                    "data_type": data_type_list[nb],
                    "machine_name": zone_attr["Hostname"]
                    if "Hostname" in zone_attr else None,
                    "version": zone_attr["Version"]
                    if "Version" in zone_attr else None,
                    "optical_index": zone_attr["OpticalIndex"]
                    if "OpticalIndex" in zone_attr else 1.5,
                    "overlap": overlap,

                    "ampli_power": zone_attr["AmpliPower"][0]
                    if "AmpliPower" in zone_attr else None,
                    "derivation_time": zone_attr["DerivationTime"][0]
                    if "DerivationTime" in zone_attr else None,
                    "fiber_length": zone_attr["FiberLength"][0]
                    if "FiberLength" in zone_attr else None,
                    "gauge_length": zone_attr["GaugeLength"][0]
                    if "GaugeLength" in zone_attr else None,
                    "pulse_rate_freq": zone_attr["PulseRateFreq"][0] / 1000
                    if "PulseRateFreq" in zone_attr else None,
                    "pulse_width": zone_attr["PulseWidth"][0]
                    if "PulseWidth" in zone_attr else None,
                    "sampling_res": zone_attr["SamplingRes"][0]
                    if "SamplingRes" in zone_attr else None,

                    "extent": zone_attr["Extent"],
                    "origin": zone_attr["Origin"],
                    "spacing": zone_attr["Spacing"],

                    "distance_origin": zone_attr["Origin"][0],
                    "distance_spacing": zone_attr["Spacing"][0],
                    "distance_index_start": zone_attr["Extent"][0],
                    "distance_index_end": zone_attr["Extent"][1],
                    "distance_start": distance_start,
                    "distance_end": distance_end,
                    "distance_vect_size":  zone_attr["Extent"][1] - zone_attr["Extent"][0] + 1,

                    "timestamp_origin": timestamp[0],
                    "timestamp_spacing": block_rate_hz,
                    "timestamp_index_start": 0,
                    "timestamp_index_end": len(timestamp)-1,
                    "timestamp_start": timestamp[0],
                    "timestamp_end": timestamp[-1],
                    "timestamp_vect_size": len(timestamp),
                    "timestamp_position": "middle"
                    if "Version" in zone_attr else "start",

                    "utc_date_start": comp_time_dict["date"][0],
                    "utc_time_start": comp_time_dict["time"][0],
                    "utc_date_end": comp_time_dict["date"][1],
                    "utc_time_end": comp_time_dict["time"][1],

                    "block_rate": block_rate_hz,
                    "block_time_size_wo": block_time_size_wo,
                    "block_time_size_no": block_time_size_no,
                    "sampling_rate": 1 / t_spacing_s
                    if block_time_size_wo != 1 else None,
                    "nyquist": 1 / t_spacing_s / 2
                    if block_time_size_wo != 1 else None,
                    "temporal_spacing": t_spacing_s
                    if block_time_size_wo != 1 else None,
                }
                # Create the unit dictionary
                zone_unit_dict = {
                    "data_type": None,
                    "machine_name": None,
                    "version": None,
                    "optical_index": None,
                    "overlap": "%",

                    "ampli_power": "dBm",
                    "derivation_time": "ms",
                    "fiber_length": "m",
                    "gauge_length": "m",
                    "pulse_rate_freq": "Hz",
                    "pulse_width": "m",
                    "sampling_res": "cm",

                    "extent": ["index", "index", "index", "index", None, None],
                    "origin": ["m", "ms", None],
                    "spacing": ["m", "ms", None],

                    "distance_origin": "m",
                    "distance_spacing": "m",
                    "distance_index_start": "index",
                    "distance_index_end": "index",
                    "distance_start": "m",
                    "distance_end": "m",
                    "distance_vect_size": "points",

                    "timestamp_origin": "s",
                    "timestamp_spacing": "s",
                    "timestamp_index_start": "index",
                    "timestamp_index_end": "index",
                    "timestamp_start": "s",
                    "timestamp_end": "s",
                    "timestamp_vect_size": "points",
                    "timestamp_position": None,

                    "utc_date_start": "%Y-%b-%d",
                    "utc_time_start": "%H:%M:%S",
                    "utc_date_end": "%Y-%b-%d",
                    "utc_time_end": "%H:%M:%S",

                    "block_rate": "Hz",
                    "block_time_size_wo": "points",
                    "block_time_size_no": "points",
                    "sampling_rate": "Hz",
                    "nyquist": "Hz",
                    "temporal_spacing": "s",
                }

                # Add the param and unit dictionaries to the attribute dictionary
                attribut_dict[str(zone)] = zone_dict
                attribut_dict[str(zone) + "_units"] = zone_unit_dict

        except KeyError as ker:
            # Raise a TypeError if a key is missing in the HDF5 structure
            raise TypeError("Unable to parse HDF5 file") from ker
        else:
            return attribut_dict

    @staticmethod
    def set_attribut_dict(hdf5_dict, attribut_dict, data_dict, extracted_data):
        """
        Update the attributes in the HDF5 dictionary based on the provided zone data.

        This method modifies the `hdf5_dict` by updating the attributes such as `Overlap`, 
        `Spacing`, `Extent`, and `BlockRate` for each zone, using values from `attribut_dict`, 
        `data_dict`, and `extracted_data`. The updates are applied in-place to the `hdf5_dict`.

        Args:
            hdf5_dict (dict): The dictionary representing the HDF5 structure, with zone-level data.
            attribut_dict (dict): The dictionary containing the attributes for each zone (e.g., overlap, optical index).
            data_dict (dict): The dictionary containing index data for each zone (e.g., start/end index).
            extracted_data (dict): Contains the actual data for each zone, including redundancy and shape info.

        Returns:
            None: The function modifies the `hdf5_dict` in place and does not return a value.

        Notes:
            The method assumes the structure of the input dictionaries follows the expected format.
            The updates are made directly in the `hdf5_dict` for each zone based on conditional logic.
        """

        for zone in attribut_dict["list_zones"]:

            # ## TODO
            # # need to be implemented in the attibutes of the file at creation
            # hdf5_dict[zone]["OpticalIndex"] = np.array(
            #     attribut_dict[zone]["optical_index"], dtype=np.int32)

            # Determine the correct overlap key (Overlap or BlockOverlap)
            overlap_key = "Overlap" if "Overlap" in hdf5_dict[zone] else "BlockOverlap"

            # Check if redundancy has been removed for the zone and adjust overlap accordingly
            if extracted_data[zone]["remove_redundancy"]:
                hdf5_dict[zone][overlap_key] = np.array([0], dtype=np.int32)
            else:
                hdf5_dict[zone][overlap_key] = np.array(
                    [attribut_dict[zone]["overlap"]], dtype=np.int32)

            # Adjust the Spacing based on block time size and block rate
            if attribut_dict[zone]["block_time_size_wo"] == 1:
                hdf5_dict[zone]["Spacing"] = np.array([
                    hdf5_dict[zone]["Spacing"][0],
                    1000 / attribut_dict[zone]["block_rate"],
                    hdf5_dict[zone]["Spacing"][2],
                ], dtype=np.float64)

            # Adjust Extent and BlockRate based on the dimensionality of the data (3D or 2D)
            if extracted_data[zone]["data"].ndim == 3:
                hdf5_dict[zone]["Extent"] = np.array([
                    data_dict[zone]["index"][2],  # index start dist
                    data_dict[zone]["index"][3],  # index end dist
                    data_dict[zone]["index"][4],  # index start block-time
                    data_dict[zone]["index"][5],  # index end block-time
                    0,
                    0,
                ], dtype=np.int32)

            elif extracted_data[zone]["data"].ndim == 2:
                hdf5_dict[zone]["Extent"] = np.array([
                    data_dict[zone]["index"][2],  # index start dist
                    data_dict[zone]["index"][3],  # index end dist
                    0,  # index start concatenated block
                    extracted_data[zone]["data"].shape[0] - \
                        1,  # index end concatenated block
                    0,
                    0,
                ], dtype=np.int32)

                # Calculate and update BlockRate for 2D data
                # Formula:
                # block_rate = 1000/(time_data_shape * (spacing_ms / 1000))
                #            = (1000*1000) / (time_data_shape * spacing_ms)
                hdf5_dict[zone]["BlockRate"] = np.array([
                    1000000 /
                    extracted_data[zone]["data"].shape[0] /
                    hdf5_dict[zone]["Spacing"][1],
                ], dtype=np.float64)
