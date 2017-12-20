from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response

import requests
import logging
import base64
import json

app = Flask(__name__)

headers = {"PRIVATE-TOKEN": "CorJy2g_kpvaRt4G-SkY"}
id = '4161484'
branch = 'master'

#To list files
def _listFiles():

    url = "https://gitlab.com/api/v4/projects/"+id+"/repository/tree?"

    req = requests.get(url, headers=headers)

    if req.status_code != 200:
       logging.warning("status: " + str(req.status_code))
       logging.warning("error msg: " + req.text)
       response = jsonify ( {'status': req.status_code, 'error': req.text} )
       response.status_code = req.status_code
       return response

    data=req.json()
    print (data)
    logging.warning(json.dumps(data, indent=2))
    filearr=[]
    for index in range(len(data)):
 
      if data[index]['type'] != "file":
         continue
      
      fileName = data[index]['name']
      data = filearr.append ({"name" : fileName, "type" : "file"})
    return jsonify(data)

@app.route('/files', methods=['GET'])
def listFiles():
  return _listFiles()

#To view filecontent
def _fileContent(filename):

   url = "https://gitlab.com/api/v4/projects/"+id+"/repository/files/"+filename+"?ref="+branch

   req = requests.get(url, headers=headers)
   
   if req.status_code != 200:
      logging.warning("status : " + str(req.status_code))
      logging.warning(json.dumps(req.text, indent=2))
      response = jsonify ( {'status': req.status_code, 'error': "could not retrieve sha"} )
      response.status_code = req.status_code
      return response
   
   response = req.json()
   print (response)
   data = base64.b64decode(response['content']).decode('utf-8')
   response = jsonify ( { 'content': data } )
                  
   print (data)    
   response.status_code = req.status_code
   print(response)
   return (response)


@app.route('/files/<filename>', methods=['GET'])
def fileContent(filename):
  return _fileContent(filename)

#To delete file
def _deleteFile(filename):

   payload={"commit_message" : "file_deleted"}
   url = "https://gitlab.com/api/v4/projects/"+id+"/repository/files/"+filename+"?branch="+branch+"&"
 
   req = requests.delete( url, headers=headers, json=payload)
   if req.status_code == 204:
      response = jsonify ( {'status': req.status_code, 'msg': "file is successfully deleted"} )
      return response

   logging.warning("status: " + str(req.status_code))
   logging.warning(json.dumps(req.text, indent=2))
   response = jsonify ( {'status': req.status_code, 'error': "could not delete file"} )
   response.status_code = req.status_code
   response = req.json()
   return jsonify(response) 

@app.route('/files/<filename>', methods=['DELETE'])
def deleteFile(filename):
  return _deleteFile(filename)
  

#To create file
def _createFile(filename, content):
   
   payload={"branch":branch,"content":content,"commit_message" : "file_created"}
   logging.warning(json.dumps(payload, indent=2))

   url = "https://gitlab.com/api/v4/projects/"+id+"/repository/files/"+filename+"?"

   req = requests.post(url, headers=headers, json=payload)
   
   logging.warning("status: " + str(req.status_code))
   logging.warning(json.dumps(req.text, indent=2))

   if req.status_code == 201:
      response = jsonify ( {
                  'status': req.status_code, 
                  'msg': "file " + filename + " created",
                  } )
      response.status_code = req.status_code
      return response

   if req.status_code == 422:
      response = jsonify ( {'status': req.status_code, 'error': "file " + filename + " already exists"} )
      response.status_code = req.status_code
      return response

   response = req.status_code
   return "successfully created"

@app.route('/files/<filename>', methods=['POST'])
def createFile(filename):

  if request.data:
    # request has data but not json, so it must be file upload
    res = request.data
    data = json.loads(res.decode('utf-8'))
    print (data)
    content = json.dumps(data)
    return _createFile(filename, content)

  if 'file' in request.files:
    fileData = request.files['file'].read()
    content = base64.b64encode( fileData )
    return _createFile(filename, content)

  logging.error('file data missing')
  response = jsonify ( {'error': 'file data missing'} )
  response.status_code = 400
  return response



#To update file
def _updateFile(filename, content):

   payload={"branch":branch,"content":content,"commit_message" : "file_updated"}
   logging.warning(json.dumps(payload, indent=2))

   url = "https://gitlab.com/api/v4/projects/"+id+"/repository/files/"+filename+"?"

   req = requests.put(url, headers=headers, json=payload)

   logging.warning("url: " + url)
   logging.warning("status: " + str(req.status_code))
   logging.warning(json.dumps(req.text, indent=2))
  
   if req.status_code == 200:
      response = jsonify ( {
                  'status': req.status_code,
                  'msg': "file " + filename + " updated",
                  } )
                  
      response.status_code = req.status_code
      return response

   response = jsonify ({'status': req.status_code, 'error': req.text})
   
   response = req.status_code
   return "successfully updated"

@app.route('/files/<filename>', methods=['PUT'])
def updateFile(filename):

  if request.data:
    # request has data but not json, so it must be file upload
    res = request.data
    data = json.loads(res.decode('utf-8'))
    print (data)
    content = json.dumps(data)
    return _updateFile(filename, content)

  if 'file' in request.files:
    fileData = request.files['file'].read()
    content = base64.b64encode( fileData )
    return _updateFile(filename, content)

  logging.error('file data missing')
  response = jsonify ( {'error': 'file data missing'} )
  response.status_code = 400
  return response



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
   app.run(debug = True, host = 'localhost')

