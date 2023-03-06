from setuptools import Extension, setup
import Cython.Build
import subprocess
import sys

setup(
        name = "AnalysisTopGNN", 
        version = "2.0", 

        packages = [
            "AnalysisTopGNN", 
            "AnalysisTopGNN.Notification", 
            "AnalysisTopGNN.Samples", 
            "AnalysisTopGNN.Tools", 
            
            "AnalysisTopGNN.Model", 
            "AnalysisTopGNN.Templates", 
            "AnalysisTopGNN.Particles", 
            "AnalysisTopGNN.Events",
            "AnalysisTopGNN.Deprecated",
            
            "AnalysisTopGNN.Features",  
            "AnalysisTopGNN.Features.TruthJet",
            "AnalysisTopGNN.Features.TruthTop",
            "AnalysisTopGNN.Features.TruthTopChildren",

            "AnalysisTopGNN.IO",
            "AnalysisTopGNN.Generators",
            "AnalysisTopGNN.Plotting", 
            "AnalysisTopGNN.Submission", 
            "AnalysisTopGNN.Statistics", 
            "AnalysisTopGNN.Vectors",
        ],
        package_dir = {
            "AnalysisTopGNN": "src",
            "AnalysisTopGNN.Notification" : "src/Notification",
            "AnalysisTopGNN.Samples" : "src/Samples", 
            "AnalysisTopGNN.Tools" : "src/Tools",
            
            "AnalysisTopGNN.Model" : "src/Model", 
            "AnalysisTopGNN.Templates" : "src/EventTemplates/Templates", 
            "AnalysisTopGNN.Particles" : "src/EventTemplates/Particles",
            "AnalysisTopGNN.Events" : "src/EventTemplates/Events",
            "AnalysisTopGNN.Deprecated" : "src/EventTemplates/Deprecated", 
            
            "AnalysisTopGNN.Features" : "src/Features", 
            "AnalysisTopGNN.Features.TruthJet" : "src/Features/TruthJet",
            "AnalysisTopGNN.Features.TruthTop" : "src/Features/TruthTop",
            "AnalysisTopGNN.Features.TruthTopChildren" : "src/Features/TruthTopChildren",

            "AnalysisTopGNN.IO" : "src/IO",
            "AnalysisTopGNN.Plotting" : "src/Plotting",
            "AnalysisTopGNN.Statistics" : "src/Statistics", 
            "AnalysisTopGNN.Generators" : "src/Generators", 
            "AnalysisTopGNN.Submission" : "src/Submission", 
        },

        ext_modules = [
                Extension("AnalysisTopGNN.Vectors", sources = ["src/Vectors/Lorentz.pyx"]),
        ],

        cmdclass = {
                "build_ext" : Cython.Build.build_ext, 
        }, 
        long_description = open("README.md").read(), 
    )
