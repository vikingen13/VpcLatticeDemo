
# Amazon VPC Lattice demonstration!

This project is a basic infrastructure to be used as a starting point for a VPC Lattice démonstration.

It uses the AWS CDK.

The project deploys the following infrastructure in your AWS account:
![Architecture](https://raw.githubusercontent.com/vikingen13/VpcLatticeDemo/main/archi.png)

The architecture is composed of 2 VPC named VPC A and VPC B. There is absolutely no route between the 2 VPC's.

In each VPC, there is an instance deployed in the private subnet.

VPC A contains an application composed of 2 components:
- Instance A hosts a web server listening on port 8080 and answering "Hello from EC2"
- A Lambda, connected to VPC A through a VPC endpoint answering "Hello from Lambda".

The objective of the demo is to bundle a VPC Lattice service composed of the 2 components and to make it available in VPC A and in VPC B.

## Architecture deployment

The project uses the CDK. It is assumed that Python and CDK are installed on your machine.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now deploy the CloudFormation stack.

```
$ cdk deploy
```

## Check that everything is fine

At this point, the infrastructure is deployed.
To check that everything is correctly deployed, run the following steps:

- Connect to Instance A using session manager in the AWS console

- execute the following command ```curl 127.0.0.1:8080```

- The command should answer "Hello from EC2".

## Create the VPC Lattice service based on the EC2 and Lambda components

### Create the target Groups

In the VPC section of the AWS console, select **VPC Lattice/Target Groups** and create a new target group.

Select **Instances**, name it **instancetg**, select **HTTP** and **8080** as the protocol and port.

For VPC, select **theVPCA**, leave other options as is.

On the second screen, select **InstanceA** and click **Include as pending below** to register the instance and then **create target group**.

Create a second target group named **lambdatg** for the AWS Lambda component. Select **VpcLatticeDemoStack-Lambda** for the target lambda function.

### Create the VPC Lattice service

In the VPC section of the AWS console, select **VPC Lattice/Services** and create a new service.

Name the service **demoservicea**.

Select AWS IAM as auth type and apply the **Allow authenticated and unautheticated access** policy template.

In the routing section, create a listener on HTTPS port 443. Slect the 2 target groups that were precedently created. This will load balance traffic evenly between the EC2 instance and the Lambda by default.

Add two optional rules in the listener:
- In the first rule, select **instancetg** for target group and insert **instance** for the path name.
- In the second rule, select the **lambdatg** for target group and insert **lambda** for the path name.

Skip the network association part.

At this point, we have created a service named "servicea" that can be associated with several service networks. The service is not reachable until it is associated with at least one service network.

## Create a service network, associate it with the servicea and with VPC A

In the VPC section of the AWS console, select **VPC Lattice/Service networks** and create a new service network.

In service associations, Associate the service network with **servicea**.

In VPC associations, add a VPC association and select **theVPCA**. For security group, select the security group containing **SGA**. This security group allows connections on the port 443 from the local network.

## Check that everything is fine

At that point, we have created a service network containing a service. This service network is associated with the VPC A, meaning that instances in VPC A can access the services in the service network.

To verify that:
- In VPC Lattice/service, select **servicea** and copy the domain name of the service
- connect on Instance A
- run the following command: ```curl https://servicea-038d966f319699c66.7d67968.vpc-lattice-svcs.eu-west-1.on.aws```
- You should get a random answer from the lambda or the EC2 (Hello from Lambda or Hello from EC2)
- You can also test the following commands: ```curl https://servicea-038d966f319699c66.7d67968.vpc-lattice-svcs.eu-west-1.on.aws/instance``` and ```curl https://servicea-038d966f319699c66.7d67968.vpc-lattice-svcs.eu-west-1.on.aws/lambda```

If you test the same commands from Instance B, you should not get an answer. This is because VPC B is not associated with the service network.

## Associate the service network with VPC B

In the VPC section of the AWS console, select **VPC Lattice/Service networks**.

Select the service network previously created and create a new VPC association for **theVPCB** with **SGB** as the security group.

Once this association is created, you should be able to access the service from Instance B in VPC B (note that it may take some minutes to become active).