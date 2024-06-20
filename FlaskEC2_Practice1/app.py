from flask import Flask, render_template, request, redirect, url_for,jsonify
import boto3
import datetime 

app = Flask(__name__)
ec2 = boto3.resource('ec2')


@app.route('/')
def Index():
    instances = ec2.instances.all()
    instances_list = [] 
    for instance in instances:
        instances_list.append(
            {
                'id': instance.id,
                'state': instance.state['Name'],
                'type': instance.instance_type,
                'public_ip': instance.public_ip_address
            }
        )
    return jsonify(instances_list)    


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)