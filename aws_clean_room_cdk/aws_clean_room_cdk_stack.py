from aws_cdk import (
    # Duration,
    CfnOutput,
    CfnTag,
    Stack,
    aws_glue as glue,
    # aws_sqs as sqs,
    aws_cleanrooms as cleanrooms,
    RemovalPolicy,
    aws_iam as iam,
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
        # table_name = "delphinodelphit"
        glue_database_name = "microetldb"
        glue_table_name = "output_parquet_files"
        collaboration_identifier = "collaboration-uuid"
         # Create IAM Role for the service to assume
        configured_table_role = iam.Role(
            self,
            "ServiceRole",
            assumed_by=iam.ServicePrincipal("cleanrooms.amazonaws.com"),
            description="IAM role for the service to access catalog metadata and query the table",
        )
        configured_table_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "glue:GetDatabase",           
                    "glue:GetDatabases",         
                    "glue:GetTable",           
                    "glue:GetTables",         
                    "glue:GetPartition",           
                    "glue:GetPartitions",         
                    "glue:GetSchema",           
                    "glue:GetSchemaVersion",            
                    "glue:BatchGetPartition"            
                    ],
                resources=["*"]
            )
        )
        # Create an S3 bucket for query results
        query_results_bucket =  Bucket(self, "ProcessedDataS3bucket", 
                                  bucket_name="delphitcleanroomqueryresults", 
                                  versioned=False,
                                  removal_policy=RemovalPolicy.DESTROY,
                                  auto_delete_objects=True, block_public_access=BlockPublicAccess.BLOCK_ALL
                                  )
        #collaboration
        collaboration = cleanrooms.CfnCollaboration(
            self,
            "DelphitCollaboration",
            name="AWS clean room project",
            description="never trust",
            creator_display_name="delphit-datas",
            creator_member_abilities=["CAN_QUERY"],
            members=[
                {
                    "accountId": "AccountID",  
                    "displayName": "Delphino",
                    "memberAbilities": [ "CAN_RECEIVE_RESULTS"]
                }
            ],
            query_log_status="ENABLED"
           
        )

        collaboration.set_query_compute_cost_payer = "AccountID"
        
        cfn_membership = cleanrooms.CfnMembership(self, "CfnMembership",
            collaboration_identifier=collaboration_identifier,
            query_log_status="ENABLED",
            tags=[CfnTag(
                key="delphit-datas",
                value="owner"
            )]
        )
       



        # Create the configured table
        configured_table = cleanrooms.CfnConfiguredTable(
            self,
            "ConfiguredTable",
            name=glue_table_name,
            analysis_method="DIRECT_QUERY",
            allowed_columns=[
                "departure_date",
                "departure_datetime_utc",
                "departure_airport_name",
                "departure_city",
                "departure_country",
                "arrival_datetime_utc",
                "arrival_airport_name"
            ],
            table_reference=cleanrooms.CfnConfiguredTable.TableReferenceProperty(
                glue=cleanrooms.CfnConfiguredTable.GlueTableReferenceProperty(
                    database_name=glue_database_name,
                    table_name=glue_table_name
                )
            ),
            analysis_rules=[
                cleanrooms.CfnConfiguredTable.AnalysisRuleProperty(
                    policy=cleanrooms.CfnConfiguredTable.ConfiguredTableAnalysisRulePolicyProperty(
                        v1=cleanrooms.CfnConfiguredTable.ConfiguredTableAnalysisRulePolicyV1Property(
                            aggregation=cleanrooms.CfnConfiguredTable.AnalysisRuleAggregationProperty(
                                aggregate_columns=[
                                    cleanrooms.CfnConfiguredTable.AggregateColumnProperty(
                                        column_names=["departure_date"],
                                        function="SUM"
                                    ),
                                    cleanrooms.CfnConfiguredTable.AggregateColumnProperty(
                                        column_names=["departure_datetime_utc"],
                                        function="AVG"
                                    )
                                    # Add more aggregate columns as needed
                                ],
                                dimension_columns=[
                                    "departure_airport_name",
                                    "departure_city",
                                    "departure_country"
                                ],
                                join_columns=["arrival_airport_name"],
                                output_constraints=[
                                    cleanrooms.CfnConfiguredTable.AggregationConstraintProperty(
                                        column_name="departure_date",
                                        minimum=123,
                                        type="COUNT_DISTINCT"
                                    )
                                    # Add more output constraints as needed
                                ],
                                scalar_functions=["CAST"],
                                allowed_join_operators=["AND", "OR"],
                                join_required="QUERY_RUNNER"
                            )
                        )
                    ),
                    type="AGGREGATION"
                )
            ]
        )

        cfn_configured_table_association = cleanrooms.CfnConfiguredTableAssociation(self, "DelphitdelphinoTableAssociation",
            configured_table_identifier="collaboration-uuid",
            membership_identifier="membership-uuid",
            name=glue_table_name,
            role_arn=configured_table_role.role_arn,
          
            description="description",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
                # Output the configured table ID
        CfnOutput(
            self,
            "ConfiguredTableId",
            value=configured_table.attr_configured_table_identifier,
        )