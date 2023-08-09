from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm

class SqlServerExampleStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC and an EC2 instance
        vpc = ec2.Vpc(self, "MyVPC", max_azs=2)
        instance = ec2.Instance(self, "MyInstance",
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE2,
                instance_size=ec2.InstanceSize.MICRO,
            ),
            machine_image=ec2.MachineImage.latest_windows(version=ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE),
            vpc=vpc,
        )

        # Install SQL Server using user data script
        instance.user_data.add_commands(
            "powershell.exe Install-WindowsFeature -Name SQL-Server-2019",
            # Add more setup commands here
        )

        # Create an SSM parameter for the database connection string
        ssm.StringParameter(self, "DatabaseConnectionString",
            parameter_name="/myapp/db-connection-string",
            string_value=f"Server=localhost;Database=ExampleDB;User Id=your-username;Password=your-password;",
        )

        # Create tables and insert data
        instance.user_data.add_commands(
            "powershell.exe Invoke-SqlCmd -Query \"USE ExampleDB; CREATE TABLE Customers (CustomerID INT PRIMARY KEY, FirstName NVARCHAR(50), LastName NVARCHAR(50), Email NVARCHAR(100));\"",
            "powershell.exe Invoke-SqlCmd -Query \"USE ExampleDB; INSERT INTO Customers (CustomerID, FirstName, LastName, Email) VALUES (1, 'John', 'Doe', 'john@example.com');\"",
            # Add more table creation and data insertion commands here
        )

app = core.App()
SqlServerExampleStack(app, "SqlServerExampleStack")
app.synth()
