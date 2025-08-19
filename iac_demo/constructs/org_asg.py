from constructs import Construct
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2


class ASG(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        self.auto_scaling_group = self._create_auto_scaling_group()

    def _create_auto_scaling_group(self):
        pass

    def _create_ec2_launch_template(self):
        pass
