import requests
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = self.create_vpc()
        self.create_ec2(vpc)

    def create_vpc(self) -> ec2.Vpc:
        vpc = ec2.Vpc(self, "dev-vpc-01", vpc_name="dev-vpc-01",
                      ip_addresses=ec2.IpAddresses.cidr("10.1.0.0/16"),
                      max_azs=1,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              name="dev-public-subnet-01",
                              subnet_type=ec2.SubnetType.PUBLIC,
                              cidr_mask=24
                          )])

        for s in vpc.public_subnets:
            print(s)

        return vpc

    def create_ec2(self, vpc):
        sg = ec2.SecurityGroup(self, "dev-sg-01",
                               vpc=vpc,
                               description="Allow SSH access from my global IP",
                               allow_all_outbound=True)
        sg.add_ingress_rule(ec2.Peer.ipv4(
            f'{self.get_global_ipv4()}/32'), ec2.Port.tcp(22), "SSH access")

        ec2.Instance(self, "dev-ec2-amazonlinux2023-01", instance_name="dev-ec2-amazonlinux2023-01",
                     instance_type=ec2.InstanceType("t3.micro"),
                     machine_image=ec2.MachineImage.latest_amazon_linux2023(),
                     vpc=vpc,
                     key_name="common-key",
                     vpc_subnets=ec2.SubnetSelection(
                         subnet_type=ec2.SubnetType.PUBLIC),
                     security_group=sg)

    def get_global_ipv4(self) -> str:
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            return response.json()['origin'].split(',')[0].strip()
        else:
            return "0.0.0.0/0"
