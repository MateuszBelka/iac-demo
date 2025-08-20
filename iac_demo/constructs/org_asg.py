from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_kms as kms,
    aws_ssm as ssm,
    aws_iam as iam,
)


class ASG(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ):
        super().__init__(scope, construct_id)
        launch_template = self._create_ec2_launch_template()
        self.auto_scaling_group = self._create_auto_scaling_group(launch_template)

    def _create_auto_scaling_group(self, launch_template: ec2.LaunchTemplate):
        vpc_subnet_id_1 = ssm.StringParameter.from_string_parameter_name(
            self, "SubnetId", string_parameter_name="/org/vpc/private-subnet-1-id"
        ).string_value

        return autoscaling.CfnAutoScalingGroup(
            self,
            "AutoScalingGroup",
            auto_scaling_group_name="iac-demo-asg",
            desired_capacity="1",
            max_size="1",
            min_size="1",
            launch_template=autoscaling.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                version=launch_template.version_number,
                launch_template_id=launch_template.launch_template_id,
            ),
            availability_zones=cdk.Fn.get_azs(region=cdk.Aws.REGION),
            vpc_zone_identifier=[vpc_subnet_id_1],
        )

    def _create_ec2_launch_template(self):
        kms_key_arn = ssm.StringParameter.from_string_parameter_name(
            self,
            "EBSKeyParameter",
            string_parameter_name="/org_name/ebs/encryption-key-arn",
        ).string_value

        return ec2.LaunchTemplate(
            self,
            id="LaunchTemplate",
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=15,
                        encrypted=True,
                        kms_key=kms.Key.from_key_arn(
                            self, "EBSKey", key_arn=kms_key_arn
                        ),
                        delete_on_termination=True,
                    ),
                )
            ],
            instance_type=ec2.InstanceType("t3a.medium"),
            launch_template_name="iac-demo-asg-launch-template",
            machine_image=ec2.MachineImage.from_ssm_parameter(
                parameter_name="/org_name/hardenend-ami-id"
            ),
            role=iam.Role.from_role_name(
                self, "EC2Role", role_name="iac-demo-ec2-role"
            ),
            associate_public_ip_address=False,
        )
