#!/usr/bin/env python3
import aws_cdk as cdk

from iac_demo.iac_demo_stack import IacDemoStack


app = cdk.App()
IacDemoStack(
    app,
    "org-iac-demo",
    synthesizer=cdk.CliCredentialsStackSynthesizer(),
)

app.synth()
