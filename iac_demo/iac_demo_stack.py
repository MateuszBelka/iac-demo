from aws_cdk import (
    Stack,
)
from constructs import Construct

from .constructs.org_asg import ASG
from .constructs.org_standards.org_no_publicip import NoPublicIP


class IacDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ASG(self, construct_id="AutoScalingGroup")

        NoPublicIP(self, construct_id="NoPublicIPConfigRule")
