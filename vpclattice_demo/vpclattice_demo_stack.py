from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    # aws_sqs as sqs,
)
from constructs import Construct

class VpclatticeDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Declare VPCA.
        myVpcA = ec2.Vpc(self, "TheVPCA",
            ip_addresses=ec2.IpAddresses.cidr("10.1.0.0/16")
        )

        # Declare VPCB.
        myVpcB = ec2.Vpc(self, "TheVPCB",
            ip_addresses=ec2.IpAddresses.cidr("10.2.0.0/16")
        )

        #Declare lambda
        myLambdaA = _lambda.Function(self, "Lambda_A",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("vpclattice_demo/lambda_A"),
            handler="lambda_function.lambda_handler"                       
        )

        #add a VPC endpoint for Lambda in VPCA
        myVpcA.add_interface_endpoint("VPC Endpoint",
                                    service=ec2.InterfaceVpcEndpointAwsService.LAMBDA_,                                                                        
                                    private_dns_enabled=True,                                    
                                    open=True,
                                    )
        
        #Create instance with a web server in VPCA
        myInstanceA = ec2.Instance(self, "InstanceA",
            vpc=myVpcA,
            instance_type=ec2.InstanceType("m5.large"),        
            machine_image=ec2.MachineImage.latest_amazon_linux(
               generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            )
        )

        with open("vpclattice_demo/ws.py", "r") as myfile:
            myPythonScript = myfile.read()

        myInstanceA.user_data.add_commands("yum update -y")
        myInstanceA.user_data.add_commands("yum install amazon-linux-extras -y")        
        myInstanceA.user_data.add_commands("amazon-linux-extras install epel -y")
        myInstanceA.user_data.add_commands("yum install figlet -y")
        myInstanceA.user_data.add_commands("echo 'echo Instance A|figlet' >/root/instance.sh")
        myInstanceA.user_data.add_commands("chmod +x /root/instance.sh")
        myInstanceA.user_data.add_commands("echo '{}' > /root/ws.py".format(myPythonScript))
        myInstanceA.user_data.add_commands("python3 /root/ws.py&")
        
        #open the instance security group port 8080 from other machines in VPCA
        myInstanceA.connections.allow_from(ec2.Peer.ipv4(myVpcA.vpc_cidr_block),ec2.Port.tcp(8080), "Allow from machines in the same VPC to port 8080")
        myInstanceA.connections.allow_from(ec2.Peer.ipv4("169.254.0.0/16"),ec2.Port.tcp(8080), "Allow from machines in the same VPC to port 8080")

        #create instance in VPCB to access service declared in VPCLattice
        myInstanceB = ec2.Instance(self, "InstanceB",
            vpc=myVpcB,
            instance_type=ec2.InstanceType("m5.large"),                    
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                )
        )

        myInstanceB.user_data.add_commands("yum update -y")
        myInstanceB.user_data.add_commands("yum install amazon-linux-extras -y")        
        myInstanceB.user_data.add_commands("amazon-linux-extras install epel -y")
        myInstanceB.user_data.add_commands("yum install figlet -y")
        myInstanceB.user_data.add_commands("echo 'echo Instance B|figlet' >/root/instance.sh")
        myInstanceB.user_data.add_commands("chmod +x /root/instance.sh")


        #create security groups in both VPC for vcplattice association
        mySGA = ec2.SecurityGroup(self, "SGA",
                vpc=myVpcA,                                      
                description="SGA for VPCLattice association"
                )
        mySGA.add_ingress_rule(ec2.Peer.ipv4(myVpcA.vpc_cidr_block),ec2.Port.tcp(443),"Allow from machines in the same VPC to port 443")

        mySGB = ec2.SecurityGroup(self, "SGB",
                vpc=myVpcB,                                                                        
                description="SGB for VPCLattice association"
                )
        mySGB.add_ingress_rule(ec2.Peer.ipv4(myVpcB.vpc_cidr_block),ec2.Port.tcp(443),"Allow from machines in the same VPC to port 443")

