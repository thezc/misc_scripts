#!/usr/bin/python
import json
import boto3


ec2_region = "us-west-1"
server_type="cluster"
name=""

def grab_instances():
        # connection to aws 
        boto3.setup_default_session(profile_name='company')
        client = boto3.client('ec2')
        print (boto3.session.Session().available_profiles)
        response = client.describe_instances(Filters=[
                                {'Name' : 'instance-state-name','Values' : ['running']},
                                {'Name' : 'tag:server_type','Values' : [server_type]}
                                ]
                        )     
        # create a list of all the instances for this page 
        count=0
        mylist=[]
        for r in response['Reservations']:
                for  i in r['Instances']:
                        vals={}
                        ec2_instance_id=i["InstanceId"]
                        ec2_instance_type=i["InstanceType"]
                        ec2_image_id=i["ImageId"]
                        tag_list= i["Tags"]
                        for t in tag_list:
                                vals[t.get("Key")]=t.get("Value")
                        ec2_name=vals["Name"]
                        moneta_server_type=vals["server_type"]
                        mylist.append({"name": ec2_name, "id": ec2_instance_id, "ami": ec2_image_id, "type": ec2_instance_type})
        return mylist
        

instances = grab_instances()

def gen_memory_metrics(instance_list):
        # build a list of all memory metrics for each instance
        mem_metrics = []
        count=0
        ecount=1
        mcount=1
        for i in instance_list:
                mem_metrics.append([ { "expression": "((m" + str(mcount) + " + m" + str((mcount+1)) + " + m" + str((mcount+2)) + ")/m" + str((mcount+3)) + " * 100)", "label": instances[count]["id"] + " (" + instances[count]["name"] + ")", "id": "e" + str(ecount), "region": ec2_region } ])
                mem_metrics.append([ "CWAgent", "mem_total", "InstanceId", instances[count]["id"], "ImageId", instances[count]["ami"], "InstanceType", instances[count]["type"], { "id": "m" + str((mcount+3)), "visible": False } ])
                mem_metrics.append([ ".", "mem_used", ".", ".", ".", ".", ".", ".", { "id": "m" + str(mcount), "visible": False } ])
                mem_metrics.append([ ".", "mem_buffered", ".", ".", ".", ".", ".", ".", { "id": "m" + str((mcount+1)), "visible": False } ])
                mem_metrics.append([ ".", "mem_cached", ".", ".", ".", ".", ".", ".", { "id": "m" + str((mcount+2)), "visible": False } ])
                count+=1
                ecount+=1
                mcount+=4
        return mem_metrics

def gen_cpu_metrics(instance_list):
        # build a list of all cpu metrics for each instance
        cpu_metrics = []
        count=0
        ecount=1
        mcount=1
        for i in instance_list:
                cpu_metrics.append([ "AWS/EC2", "CPUUtilization", "InstanceId", instances[count]["id"], {"label": instances[count]["id"] + " (" + instances[count]["name"] + ")"} ])
                count+=1
                ecount+=1
                mcount+=4
        return cpu_metrics


def gen_diskio_metrics(instance_list):
        # build a list of all diskio metrics for each instance
        diskio_metrics = []                                                                                                                                                                            
        count=0      
        ecount=1
        mcount=1                                                                                                                                                                                                                                     
        for i in instance_list:
            diskio_metrics.append([ { "expression": "(m" + str(mcount) + " + m" + str((mcount+1)) + ")", "label": instances[count]["id"] + " (" + instances[count]["name"] + ")", "id": "e" + str(ecount), "region": ec2_region } ])                                                                                                                                                                                                       
            diskio_metrics.append([ "CWAgent", "diskio_read_bytes", "InstanceId", instances[count]["id"], { "id": "m" + str(mcount), "visible": False } ])                     
            diskio_metrics.append([ "CWAgent", "diskio_write_bytes", "InstanceId", instances[count]["id"], { "id": "m" + str(mcount+1), "visible": False } ])                                      
            count+=1                                                                                                                                                                                                                                                                   
            ecount+=1 
            mcount+=3
        return diskio_metrics                                                                                                                                                                                                                            

def gen_diskio_read_metrics(instance_list):
    # build a list of all diskio metrics for each instance
    diskio_read_metrics = []                                                                                                                                               
    count=0                                                                                                                                                           
    ecount=1                                                                                                                                                          
    mcount=1
    for i in instance_list:                                                                                                                                           
        diskio_read_metrics.append([ { "expression": "(m" + str(mcount) + ")", "label": instances[count]["id"] + " (" + instances[count]["name"] + ")", "id": "e" + str(ecount), "region": ec2_region } ])
        diskio_read_metrics.append([ "CWAgent", "diskio_read_bytes", "InstanceId", instances[count]["id"], { "id": "m" + str(mcount), "visible": False } ])                
        count+=1                                                                                                                                                      
        ecount+=1                                                                                                                                                     
        mcount+=3
    return diskio_read_metrics                                                                                                                                                                                                                                              

def gen_diskio_write_metrics(instance_list):
    # build a list of all diskio metrics for each instance
    diskio_write_metrics = []                                                                                                                               
    count=0                                                                          
    ecount=1
    mcount=1
    for i in instance_list:                                                                                                                              
        diskio_write_metrics.append([ { "expression": "(m" + str(mcount) + ")", "label": instances[count]["id"] + " (" + instances[count]["name"] + ")", "id": "e" + str(ecount), "region": ec2_region } ])
        diskio_write_metrics.append([ "CWAgent", "diskio_write_bytes", "InstanceId", instances[count]["id"], { "id": "m" + str(mcount), "visible": False } ])
        count+=1                                                                                                                                         
        ecount+=1                                                                                                                                        
        mcount+=3
    return diskio_write_metrics 


data = {}
data['widgets'] = [
        
        # Memory usage
        {
        "type": "metric",
        "x": 11,
        "y": 0,
        "width":  11,
        "height": 7,
            "properties": {
                "metrics": gen_memory_metrics(instances),
                "view": "timeSeries",
                "stacked": False,
                "region": ec2_region,
                "stat": "Average",
                "period": 300,
                "title": "% MEM USED",
                "unit": "Percent"
            }
        },
        
        # CPU Usage
        {
        "height": 7,
        "width": 11,
        "y": 0,
        "x": 0,
        "type": "metric",
            "properties": {
                "metrics": gen_cpu_metrics(instances),
                "view": "timeSeries",
                "stacked": False,
                "region": ec2_region,
                "title": "CPU Utilization"
            }
        },

        # Disk IO Read
        {
        "height": 7,
        "width": 11,
        "y": 8,
        "x": 11,
        "type": "metric",
            "properties": {
                "metrics": gen_diskio_read_metrics(instances),
                "view": "timeSeries",
                "stacked": False,
                "period": 300,
                "stat": "Maximum",
                "region": ec2_region,
                "title": "Disk IO Read",
            }
        },

        # Disk IO Write
        {
        "height": 7,
        "width": 11,
        "y": 8,
        "x": 0,
        "type": "metric",
            "properties": {
                "metrics": gen_diskio_write_metrics(instances),
                "view": "timeSeries",
                "stacked": False,
                "period": 300,
                "stat": "Maximum",
                "region": ec2_region,
                "title": "Disk IO Write",
            }
        },
        
        # Disk IO
        {
        "height": 7,
        "width": 11,
        "y": 16,
        "x": 0,
        "type": "metric",
            "properties": {
                "metrics": gen_diskio_metrics(instances),
                "view": "timeSeries",           
                "stacked": False,               
                "period": 300,
                "stat": "Maximum",
                "region": ec2_region,
                "title": "Disk IO Total",
            }
        }
]

###############################################

# print out the dashboard
json_data = json.dumps(data, indent=4)
print(json_data)

