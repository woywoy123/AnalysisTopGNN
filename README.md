# A Graph Neural Network Framework for High Energy Particle Physics

[![AnalysisG-Coverage-Action](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/woywoy123/6fee1eff8f987ac756a20133618659a1/raw/covbadge.json)]()
[![building-analysisG](https://github.com/woywoy123/AnalysisG/actions/workflows/AnalysisG_build.yml/badge.svg)](https://github.com/woywoy123/AnalysisG/actions/workflows/AnalysisG_build.yml)
[![building-pyc](https://github.com/woywoy123/AnalysisG/actions/workflows/pyc_build.yml/badge.svg)](https://github.com/woywoy123/AnalysisG/actions/workflows/pyc_build.yml)
[![Publish to PyPI](https://github.com/woywoy123/AnalysisG/actions/workflows/release.yaml/badge.svg)](https://github.com/woywoy123/AnalysisG/actions/workflows/release.yaml)
[![tox-testing-analysisG](https://github.com/woywoy123/AnalysisG/actions/workflows/test.yml/badge.svg)](https://github.com/woywoy123/AnalysisG/actions/workflows/test.yml)

## Getting Started:
The framework and tutorials are outlined within read the docs. [![Documentation Status](https://readthedocs.org/projects/analysisg/badge/?version=master)](https://analysisg.readthedocs.io/?badge=master)

## Introduction:
The aim of this package is to provide Particle Physicists with an intuitive interface to **Graph Neural Networks**, whilst remaining Analysis agnostic. 
Following a similar spirit to AnalysisTop, the physicist defines a custom event class and matches variables within ROOT files to objects that they are a representation of.
A simple example of this would be a particle, since these generally have some defining properties such as the four vector, mass, type, etc. 

From a technical point of view, the particle would be represented by some Python object, where attributes are matched to the ROOT leaf strings, such that framework can identify how variables are matched. 
A similar approach can be taken to construct event objects, where particle objects live within the event and are matched accordingly to any other particles e.g. particle truth matching. 
This hierarchical architecture allows for complex event definitions, first basic building blocks are defined and then matched according to some rule (see tutorial below).

To streamline the transition between ROOT and PyTorch Geometric (a Deep Learning framework for Graph Neural Networks), the framework utilizes event graph definitions.
These simply define which particles should be used to construct nodes on a PyTorch Geometric (PyG) Data object. Edge, Node and Graph features can be added separately as simple python functions (see tutorial below).
Post event graph construction, events are delegated to an optimization step, which trains a specified model with those graphs. 

To avoid having to deal with additional boiler plate book keeping code, the framework tracks the event to the originating ROOT file using a hashing algorithm. 
The hash is constructed by concatenating the directory, ROOT filename and event number into a single string and computing the associated hash. 
This ensures each event can be easily traced back to its original ROOT file. 

Or naviate to the tutorial folder, which outlines a few core concepts of this framework.
