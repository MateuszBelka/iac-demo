from constructs import Construct
import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild


class CICD(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        self.pipeline = self._create_pipeline()

    def _create_build_stage(self):
        pass

    def _create_pipeline(self):
        pass
