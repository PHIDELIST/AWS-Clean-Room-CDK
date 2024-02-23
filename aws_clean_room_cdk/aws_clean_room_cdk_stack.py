from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
   aws_cleanrooms as cleanrooms,
)
from constructs import Construct
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption

class AwsCleanRoomCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "AwsCleanRoomCdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        
        # Define your collaboration

        collaboration = cleanrooms.CfnCollaboration(
            self,
            "DelphitCollaboration",
            name="AWS clean room project",
            description="never trust",
            creator_display_name="delphit-datas",
            creator_member_abilities=["CAN_QUERY"],
            members=[
                {
                    "accountId": "798552153158",  
                    "displayName": "Account1_Delphino",
                    "memberAbilities": [ "CAN_RECEIVE_RESULTS"]
                }
            ],
            query_log_status="ENABLED",
           
        )

        collaboration.set_query_compute_cost_payer = "576997243977"