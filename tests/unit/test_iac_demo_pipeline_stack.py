import aws_cdk as core
import aws_cdk.assertions as assertions

from iac_demo.iac_demo_pipeline import IacDemoPipelineStack


def test_snapshot(snapshot):
    app = core.App()
    stack = IacDemoPipelineStack(app, "org-iac-demo-pipeline")
    template = assertions.Template.from_stack(stack)
    assert template.to_json() == snapshot
