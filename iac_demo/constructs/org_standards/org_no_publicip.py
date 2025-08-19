from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_config as config,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
    aws_ssm as ssm,
    Duration,
)


class NoPublicIP(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        self.no_public_ip_rule = self._create_config_rule()

    def _create_config_rule(self):
        remediation_lambda_role = iam.Role.from_role_name(
            self,
            "PublicIPRemediationRole",
            role_name="iac-demo-nopublicip-remediation-lambda-role",
        )

        log_group = logs.LogGroup(
            self,
            "PublicIPRemediationLogGroup",
            log_group_name="/aws/lambda/public-ip-remediation",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        remediation_function = _lambda.Function(
            self,
            "PublicIPRemediationFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="service.index.lambda_handler",
            role=remediation_lambda_role,
            timeout=Duration.minutes(1),
            log_group=log_group,
            code=_lambda.Code.from_asset("src/public_ip_remediation"),
        )

        config_rule = config.ManagedRule(
            self,
            "EC2NoPublicIPRule",
            identifier="EC2_INSTANCE_NO_PUBLIC_IP",
            description="Checks whether Amazon EC2 instances have a public IP association",
            config_rule_name="ec2-instance-no-public-ip",
        )

        remediation_ssm_role = iam.Role.from_role_name(
            self,
            "PublicIPRemediationSSMRole",
            role_name="iac-demo-nopublicip-remediation-ssm-role",
        )

        ssm_document = ssm.CfnDocument(
            self,
            "NoPublicIPRemediationDocument",
            name="demo-iac-no-public-ip-remediation-document",
            document_type="Automation",
            version_name="1",
            content={
                "schemaVersion": "0.3",
                "description": "Invoke lambda function for remediating public ip",
                "assumeRole": "{{AutomationAssumeRole}}",
                "parameters": {
                    "AutomationAssumeRole": {
                        "type": "String",
                        "description": "Role that allows ssm automation to trigger remediation lambda",
                        "default": remediation_ssm_role.role_arn,
                    },
                    "ResourceId": {
                        "type": "String",
                        "description": "The ID of the non-compliant resource",
                    },
                },
                "mainSteps": [
                    {
                        "name": "invokeLambdaFunction",
                        "action": "aws:invokeLambdaFunction",
                        "maxAttempts": "1",
                        "timeoutSeconds": "120",
                        "onFailure": "Abort",
                        "inputs": {
                            "FunctionName": remediation_function.function_arn,
                            "Payload": '{"ResourceId": "{{ResourceId}}"}',
                        },
                        "isEnd": True,
                    }
                ],
            },
        )

        remediation = config.CfnRemediationConfiguration(
            self,
            "DirectLambdaRemediationConfig",
            config_rule_name=config_rule.config_rule_name,
            target_type="SSM_DOCUMENT",
            target_id=ssm_document.name,
            target_version="1",
            parameters={
                "AutomationAssumeRole": {
                    "StaticValue": remediation_ssm_role.role_arn,
                },
                "ResourceId": {"ResourceValue": {"Value": "RESOURCE_ID"}}
            },
            automatic=True,
            maximum_automatic_attempts=2,
        )

        # Add dependencies to ensure proper resource creation order
        remediation.add_dependency(config_rule.node.default_child)
        remediation.add_dependency(remediation_function.node.default_child)

        return config_rule
