#!/usr/bin/env python

"""Tests for `shipflowmotionshelpers` package."""

import pytest
from shipflowmotionshelpers import shipflowmotionshelpers as helpers
import shipflowmotionshelpers.tests as tests
import os
import pandas as pd

def test_load_time_series_file():
    file_path = os.path.join(tests.path_test_project_1,'test_project_1_TS.csv')
    helpers._load_time_series(file_path=file_path)

def test_extract_parameters_from_file_input():
    
    file_path = os.path.join(tests.path_test_project_1,'test_project_1')
    parameters = helpers.extract_parameters_from_file(file_path=file_path)
    assert parameters['titl']=="M5030-01-A"
    assert parameters['b4l'] == 0.0
    assert parameters['kyy'] == 43.12

def test_extract_parameters_from_file_output():
    
    file_path = os.path.join(tests.path_test_project_1,'test_project_1_OUTPUT')
    parameters = helpers.extract_parameters_from_file(file_path=file_path)
    assert parameters['title']=="M5030-01-A"
    assert parameters['lpp'] == 154
    assert parameters['V'] == 18972.748
    assert parameters['IYZ'] == 2921.811


def test_load_parameters_one():

    file_path = os.path.join(tests.path_test_project_1,'test_project_1')
    parameters = helpers._load_parameters(file_path=file_path)
    
    assert parameters['title']=="M5030-01-A"

def test_load_parameters_many_one():

    file_path = os.path.join(tests.path_test_project_1,'test_project_1')
    parameters = helpers.load_parameters(file_path=file_path)
    
    assert parameters.loc['test_project_1']['title']=="M5030-01-A"

def test_load_time_series():

    file_path = os.path.join(tests.path_test_project_1,'test_project_1')
    df_parameters = helpers.load_parameters(file_path=file_path)

    time_series = helpers.load_time_series(df_parameters=df_parameters)

    assert isinstance(time_series, dict)
    name = df_parameters.iloc[0].name
    assert  name in time_series
    assert isinstance(time_series[name], pd.DataFrame)





