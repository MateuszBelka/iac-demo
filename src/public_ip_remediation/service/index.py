import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")
config = boto3.client("config")


def lambda_handler(event, _):
    logger.info("Received event: " + json.dumps(event, indent=2))

    instance_id = event["ResourceId"]

    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response["Reservations"][0]["Instances"][0]
    instance_state = instance.get("State", {}).get("Name", "unknown")

    if instance_state == "terminated":
        logger.info(f"Instance {instance_id} is terminated, skipping remediation")
        return {
            "Status": "SUCCESS",
            "Message": f"Instance {instance_id} is terminated - no remediation needed",
        }

    public_ip = instance.get("PublicIpAddress")
    if not public_ip:
        logger.info(f"Instance {instance_id} does not have a public IP")
        return {
            "Status": "SUCCESS",
            "Message": f"Instance {instance_id} does not have a public IP - already compliant",
        }

    network_interfaces = instance.get("NetworkInterfaces", [])
    if not network_interfaces:
        logger.error(f"No network interfaces found for instance {instance_id}")
        return {"Status": "FAILED", "Message": "No network interfaces found"}

    primary_eni = network_interfaces[0]["NetworkInterfaceId"]
    logger.info(f"Primary ENI: {primary_eni}")

    association = network_interfaces[0].get("Association", {})
    if association and association.get("AssociationId"):
        association_id = association["AssociationId"]
        allocation_id = association.get("AllocationId")

        logger.info(f"Disassociating Elastic IP from instance {instance_id}")
        ec2.disassociate_address(AssociationId=association_id)

        return {
            "status": "SUCCESS",
            "message": f"Successfully Disassociated Elastic IP from instance {instance_id}",
        }

    else:
        logger.info(f"Instance {instance_id} has auto-assigned public IP")

        # For auto-assigned public IPs, the most effective approach is to:
        # 1. Stop the instance (if it's running)
        # 2. Start it again (it will get a new private IP only if subnet doesn't auto-assign)

        subnet_id = instance.get("SubnetId")

        logger.info(f"Disabling auto-assign public IP on subnet {subnet_id}")
        ec2.modify_subnet_attribute(
            SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": False}
        )
        logger.info(
            f"Successfully disabled auto-assign public IP on subnet {subnet_id}"
        )

        if instance_state == "running":
            logger.info(
                f"Stopping instance {instance_id} to remove auto-assigned public IP"
            )
            ec2.stop_instances(InstanceIds=[instance_id])

            logger.info(f"Starting instance {instance_id}")
            ec2.start_instances(InstanceIds=[instance_id])

            logger.info(f"Successfully restarted instance {instance_id}")
            return {
                "status": "SUCCESS",
                "message": f"Successfully restarted instance {instance_id} to remove public IP",
            }

    return {"Status": "SUCCESS", "Message": "Remediation Completed Successfully"}
