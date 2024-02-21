import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_clean_room_cdk.aws_clean_room_cdk_stack import AwsCleanRoomCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_clean_room_cdk/aws_clean_room_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCleanRoomCdkStack(app, "aws-clean-room-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
