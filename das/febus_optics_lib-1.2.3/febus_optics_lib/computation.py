#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robin.guerry
"""
import copy
import datetime
from typing import Any, Callable, Dict, Tuple

import numpy as np


class BaseExceptionCompute(Exception, BaseException):
    """Base class for compute exception."""

    def __init__(self, msg, mode=None):

        if mode is not None:
            error_msg = f"Error during computing of {mode} data.\nErrormsg: {msg}"
            super().__init__(error_msg)
        else:
            super().__init__(msg)

class ComputeData:
    """
    Class for computation of data.
    """

    def __init__(self) -> None:
        """
        Initialise the ComputationData class.
        """
        self.data: np.ndarray = np.array([])
        self.c_axis: int = 0
        self.comp_data: Dict[str, Any] = {}
        self.compute_parser: Dict[str, Tuple[type, Callable]] = {
            "date": (bool, self.__second_2_date),
            "time": (bool, self.__second_2_date),
        }
        self.__reshaped = False

    def set_raw_data(self, data: np.ndarray, axis: int = 0) -> None:
        """
        Set raw data to be computed and check it as at least a size of 1

        Args:
            data (np.ndarray): raw data to be computed

        Raises:
            BaseExceptionCompute
        """
        if data.size == 0:
            raise BaseExceptionCompute(
                "Error during initialisation of DAS computation : empty data"
            )
        else:
            self.data = data
            self.c_axis = axis

    def get_computed_data(self, **kwargs) -> dict:
        """
        Compute the data with the given parameters.

        Parameters
        ----------
        date : boolean, optional
            If True get {'date':['datestring', 'datestring', ...]}.
            The default is False.
        time : boolean, optional
            If True get {'time':['timestring', 'timestring', ...]}.
            The default is True.

        Raises
        ------
        BaseExceptionCompute
            Raised if :
                wrong datatype input
                catch a TemporalSamplingError or RmsInputError.
                catch another exception

        Returns
        -------
        dictionnary
            possible keys : 'date'
                     and/or 'time'

        """
        comp_val = None
        try:
            if self.data.ndim == 2:
                self.data = self.data.reshape(
                    (1, self.data.shape[0], self.data.shape[1]))
                self.c_axis += 1

                self.__reshaped = True

            for key, value in kwargs.items():
                if key in self.compute_parser:

                    control_type = self.compute_parser[key][0]
                    if not isinstance(value, control_type):
                        raise BaseExceptionCompute(
                            f"Wrong input for {key} -> {type(value)} instead of {control_type}",
                            mode="DAS")

                    callable_fct = self.compute_parser[key][1]
                    
                    comp_val = callable_fct()
                    if key == "date" and value:
                        self.comp_data.update({key: comp_val[0]})
                    elif key == "time" and value:
                        self.comp_data.update({key: comp_val[1]})
                    else:
                        self.comp_data.update({key: value})
                        if self.__reshaped:
                            self.comp_data.update(
                                {key+"_data": np.squeeze(comp_val)})
                        else:
                            self.comp_data.update({key+"_data": comp_val})

            return copy.deepcopy(self.comp_data)

        except BaseExceptionCompute as bec:
            raise bec
        except Exception as exc:
            raise BaseExceptionCompute(exc, mode="DAS") from exc

    def __second_2_date(self):
        """Transform list of time(s) in strings 'date' and 'time'."""
        time_string = []
        date_string = []
        for _s in self.data:
            inpt_str_time = datetime.datetime.fromtimestamp(_s, tz=datetime.timezone.utc).strftime(
                "%Y/%b/%d/%H/%M/%S"
            )
            inpt_str_time = inpt_str_time.split("/")
            str_time_disp_time = (
                inpt_str_time[3]
                + ":"
                + inpt_str_time[4]
                + ":"
                + inpt_str_time[5][:2]
            )
            str_time_disp_date = (
                inpt_str_time[0] + "/" +
                inpt_str_time[1] + "/" + inpt_str_time[2]
            )
            time_string.append(str_time_disp_time)
            date_string.append(str_time_disp_date)
        return np.array(date_string), np.array(time_string)
