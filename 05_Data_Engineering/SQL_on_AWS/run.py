import  boto3, \
        configparser, \
        json, \
        progressbar, \
        psycopg2, \
        sys, \
        time
#import boto3 as bt, \
        # configparser, \
        # create_tables, \
        # etl, \
        # json, \
        # pandas as pd, \
        # psycopg2

def read_cfg_file(file_name):
    global config
    config = configparser.ConfigParser()
    config.read_file(open(file_name))

def connect_to_cluster():
    try:
        conn = psycopg2.connect(
                        """
                        host={} \
                        dbname={} \
                        user={} \
                        password={} \
                        port={}
                        """.format(*config['DWH_CONN'].values()))
        return conn
    except Exception as e:
        print(e)

def create_clients():

    REGION = config['AWS']['REGION']
    KEY = config['AWS']['KEY']
    SECRET = config['AWS']['SECRET']

    clients={}

    clients['s3'] = boto3.resource('s3',
                        region_name=REGION,
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                        )

    clients['ec2'] = boto3.resource('ec2',
                       region_name=REGION,
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                       )

    clients['iam'] = boto3.client('iam',
                        region_name=REGION,
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                        )

    clients['redshift'] = boto3.client('redshift',
                        region_name=REGION,
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                        )
    return clients

# def get_bucket_data(s3):#, bucket):
#     for bucket in s3.buckets.all():
#         print('Bucket Name: ', bucket.name)
#         for obj in bucket.objects.all():
#             print(obj)
#         #s3.Bucket("udacity-labs")

def check_iam_role(iam):
    ROLE = config['IAM_ROLE']['NAME']
    try:
        roleArn = iam.get_role(RoleName=ROLE)['Role']['Arn']
        print('Found role {}.'.format(ROLE))
    except:
        POLICY_ARN = config['IAM_ROLE']['POLICY_ARN']
        iam.create_role(
                Path='/',
                RoleName=ROLE,
                Description = "Read access to S3 for Redshift cluster.",
                AssumeRolePolicyDocument=json.dumps(
                    {
                        'Statement': [
                            {
                                'Action': 'sts:AssumeRole',
                                'Effect': 'Allow',
                                'Principal': {
                                    'Service': 'redshift.amazonaws.com'
                                    }
                                }
                            ],
                        'Version': '2012-10-17'
                        }
                     )
                )
        iam.attach_role_policy(
                RoleName=ROLE,
                PolicyArn=POLICY_ARN
                )['ResponseMetadata']['HTTPStatusCode']
        roleArn = iam.get_role(RoleName=ROLE)['Role']['Arn']
        print('Created role {} with policy: \n{}'.format(ROLE, POLICY_ARN))
    config['IAM_ROLE']['ROLE_ARN'] = roleArn

def get_clusters(redshift, verbose=False):
    response = redshift.describe_clusters()
    clusters = response['Clusters']
    if len(clusters) != 0:
        my_cluster = config['DWH_SPECS']['CLUSTER_IDENTIFIER'].lower()
        for cluster in clusters:
            if cluster['ClusterIdentifier'] == my_cluster:
                if verbose:
                    print('Found cluster ', my_cluster)
                return True
        return False
    else:
        return False

def create_cluster(redshift):
    redshift.create_cluster(
        #SPECS
        ClusterType=config['DWH_SPECS']['CLUSTER_TYPE'],
        NodeType=config['DWH_SPECS']['NODE_TYPE'],
        NumberOfNodes=int(config['DWH_SPECS']['NUM_NODES']),

        #CONN
        DBName=config['DWH_CONN']['NAME'],
        ClusterIdentifier=config['DWH_SPECS']['CLUSTER_IDENTIFIER'],
        MasterUsername=config['DWH_CONN']['USER'],
        MasterUserPassword=config['DWH_CONN']['PASSWORD'],

        #Role for s3 access
        IamRoles=[config['IAM_ROLE']['ROLE_ARN']]
        )

def check_cluster_availability(
        redshift,
        target_status,
        wait_seconds=10,
        timeout_seconds=600):
    message = {
        'available':'Creating cluster...: ',
        'deleted':'Deleting cluster...: '
        }
    widget = ['{}'.format(message[target_status]), progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(
        widgets=widget,
        max_value=timeout_seconds
        ).start()
    cluster_id = config['DWH_SPECS']['CLUSTER_IDENTIFIER']
    if target_status == 'available':
        for i in range(int(timeout_seconds/wait_seconds)):
            status = redshift.describe_clusters(
                ClusterIdentifier=cluster_id
                )['Clusters'][0]['ClusterStatus']
            elapsed = i*wait_seconds
            if status != target_status:
                for j in range(wait_seconds):
                    time.sleep(1)
                    bar.update(elapsed+j)
            else:
                # print confirmation
                print('Cluster {} {}}.'.format(cluster_id, target_status))
                print('Duration: ', elapsed, ' sec.')
                return
    elif target_status == 'deleted':
        for i in range(timeout_seconds):
            if get_clusters(redshift):
                time.sleep(1)
                bar.update(i)
            else:
                # print confirmation
                print('Cluster {} {}}.'.format(cluster_id, target_status))
                print('Duration: ', i, ' sec.')
                return
    sys.exit('Timeout.')

def get_endpoint(redshift):
    cluster_id=config['DWH_SPECS']['CLUSTER_IDENTIFIER']
    config['DWH_CONN']['HOST'] = redshift.describe_clusters(
        ClusterIdentifier=cluster_id
        )['Clusters'][0]['Endpoint']['Address']
    print('Host: ', config['DWH_CONN']['HOST'] )

def delete_role(iam):
    role = config['IAM_ROLE']['NAME']
    try:
        iam.detach_role_policy(
            RoleName=role,
            PolicyArn=config['IAM_ROLE']['POLICY_ARN']
            )
        iam.delete_role(RoleName=role)
        print('Deleted role {}.'.format(role))
    except:
        print('Error while deleting role {}'.format(role))

def open_tcp_port(
        ec2,
        port,
        cidr_ip='0.0.0.0/0',
        ip_protocol='TCP'):
    vpc = ec2.Vpc(id=config['DWH_SPECS']['VPC_ID'])
    sg = vpc.security_groups.all()
    print('SG: ', list(sg))
    defaultSg = list(vpc.security_groups.all())[0]
    #print(defaultSg)
    try:
        defaultSg.authorize_ingress(
            GroupName=defaultSg.group_name,
            CidrIp=cidr_ip,
            IpProtocol=ip_protocol,
            FromPort=int(port),
            ToPort=int(port)
            )
    except Exception as e:
        if 'already exists' not in str(e):
            print(e)
            raise e
        else:
            pass

def check_role_arn(redshift):
    # get properties
    properties = redshift.describe_clusters(
        ClusterIdentifier=config['DWH_SPECS']['CLUSTER_IDENTIFIER']
        )['Clusters'][0]
    # check roleArn
    roleArn_clr = properties['IamRoles'][0]['IamRoleArn']
    roleArn_iam = config['IAM_ROLE']['ROLE_ARN']
    if roleArn_clr != roleArn_iam:
        raise Exception('RoleArn does not match.\
                        \nroleArn (iam): {},\
                        \nroleArn (cluster): {}'.format(
                            roleArn_iam,
                            roleArn_clr)
                        )
    # save VpcId
    config['DWH_SPECS']['VPC_ID'] = properties['VpcId']

def setup_cluster(clients):
    create_cluster(clients['redshift'])
    check_cluster_availability(clients['redshift'], 'available')
    check_role_arn(clients['redshift'])
    open_tcp_port(clients['ec2'], port=config['DWH_CONN']['PORT'])

def delete_cluster(redshift):
    redshift.delete_cluster(
        ClusterIdentifier=config['DWH_SPECS']['CLUSTER_IDENTIFIER'],
        SkipFinalClusterSnapshot=True
        )
    check_cluster_availability(redshift, 'deleted')

def main():
    read_cfg_file('dwh.cfg')
    clients = create_clients()
    check_iam_role(clients['iam'])
    if not get_clusters(clients['redshift'], verbose=True):
         setup_cluster(clients)
    get_endpoint(clients['redshift'])
    conn = connect_to_cluster()
    cur = conn.cursor()
    print('Conn: ', conn)
    delete_cluster(clients['redshift'])
    delete_role(clients['iam'])
    sys.exit('End.')

# def testProgressBar(
#         wait_seconds=10,
#         timeout_seconds=60):
#     widget = ['Creating cluster...: ', progressbar.AnimatedMarker()]
#     maxvalue = timeout_seconds
#     bar = progressbar.ProgressBar(
#         widgets=widget,
#         max_value=maxvalue
#         ).start()
#     for i in range(int(timeout_seconds/wait_seconds)):
#         status = 'something'
#         elapsed = i*wait_seconds
#         if status != 'available':
#             for j in range(wait_seconds):
#                 time.sleep(1)
#                 bar.update(elapsed+j)
#         else:
#             print('hi')

if __name__ == "__main__":
    main()
