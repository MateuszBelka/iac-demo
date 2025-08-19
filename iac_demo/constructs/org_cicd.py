from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_iam as iam,
    aws_codecommit as codecommit,
)


class CICD(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        source_output = codepipeline.Artifact(artifact_name="source-output")
        build_output = codepipeline.Artifact(artifact_name="build-output")

        source_stage = self._create_source_stage(source_output)
        build_stage = self._create_build_stage(source_output, build_output)
        deploy_stage = self._create_deploy_stage(build_output)

        self.pipeline = self._create_pipeline(source_stage, build_stage, deploy_stage)

    def _create_source_stage(self, source_output: codepipeline.Artifact):
        source_action = actions.CodeCommitSourceAction(
            action_name="source",
            repository=codecommit.Repository.from_repository_name(
                self, "Repository", repository_name="iac-demo"
            ),
            branch="main",
            output=source_output,
            role=iam.Role.from_role_name(
                self, "SourceRole", role_name="codecommit-source-pipeline-role"
            ),
        )

        return codepipeline.StageProps(stage_name="Source", actions=[source_action])

    def _create_build_stage(
        self, build_input: codepipeline.Artifact, build_output: codepipeline.Artifact
    ):
        build_action = actions.CodeBuildAction(
            action_name="build",
            project=codebuild.PipelineProject(
                self, "BuildProject", project_name="iac-demo-build-project"
            ),
            input=build_input,
            outputs=[build_output],
        )

        return codepipeline.StageProps(stage_name="Build", actions=[build_action])

    def _create_deploy_stage(self, deploy_input: codepipeline.ArtifactPath):
        stack_name = "iac-demo"
        change_set_name = stack_name
        role = iam.Role.from_role_name(
            self, "DeploymentRole", role_name="cloudformation-deployment-role"
        )

        deploy_action_create = actions.CloudFormationCreateReplaceChangeSetAction(
            action_name="ias-demo-create",
            stack_name=stack_name,
            change_set_name=change_set_name,
            template_path=deploy_input.at_path("template_iac-demo.yml"),
            role=role,
            admin_permissions=False,
        )

        deploy_action_execute = actions.CloudFormationExecuteChangeSetAction(
            action_name="iac-demo-execute",
            stack_name=stack_name,
            change_set_name=change_set_name,
            role=role,
        )

        return codepipeline.StageProps(
            stage_name="Deploy", actions=[deploy_action_create, deploy_action_execute]
        )

    def _create_pipeline(self, *stages: codepipeline.StageProps):
        return codepipeline.Pipeline(
            self, "Pipeline", pipeline_name="iac-demo-pipeline", stages=[*stages]
        )
