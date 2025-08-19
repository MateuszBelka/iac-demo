from constructs import Construct
import aws_cdk as cdk
from aws_cdk import aws_config as config


class NoPublicIP(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        self.no_public_ip_rule = self._create_config_rule()

    def _create_config_rule(self):
        pass
