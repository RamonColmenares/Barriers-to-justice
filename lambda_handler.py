"""
AWS Lambda handler for the juvenile immigration API
"""
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

# Import your existing Flask app
try:
    from api.index import app
except ImportError:
    # Fallback if running locally
    sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
    from index import app

# AWS Lambda WSGI adapter
try:
    from awsgi import response
except ImportError:
    # If awsgi is not available, we'll handle it differently
    def response(app, event, context):
        # Basic Lambda response format
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'API is running'})
        }

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': ''
            }
        
        # Use awsgi to handle the Flask app
        return response(app, event, context)
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
