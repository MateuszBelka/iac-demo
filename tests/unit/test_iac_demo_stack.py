import aws_cdk as core
import aws_cdk.assertions as assertions

from iac_demo.iac_demo_stack import IacDemoStack


def test_snapshot(snapshot):
    app = core.App()
    stack = IacDemoStack(app, "org-iac-demo")
    template = assertions.Template.from_stack(stack)
    assert template.to_json() == snapshot
