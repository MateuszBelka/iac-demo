#!/usr/bin/env python3
import aws_cdk as cdk

from iac_demo.iac_demo_stack import IacDemoStack
from iac_demo.iac_demo_pipeline import IacDemoPipelineStack


app = cdk.App()
IacDemoStack(
    app,
    "org-iac-demo",
    synthesizer=cdk.CliCredentialsStackSynthesizer(),
)
IacDemoPipelineStack(
    app,
    "org-iac-demo-pipeline",
    synthesizer=cdk.CliCredentialsStackSynthesizer(),
)

app.synth()
