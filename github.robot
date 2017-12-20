*** Settings ***
Library  Collections
Library  RequestsLibrary

*** Variables ***
${url}   http://localhost:5000
${filename}   test.txt

*** Test Cases ***
listFile
    Create Session   getlist   ${url}
    ${result} =  Get Request  getlist   /files
    Should Be Equal  ${result.status_code}  ${200}
    Log   ${result.json()}

contentFile
    Create Session   getcontent   ${url}
    ${result} =  Get Request  getcontent   /files/${filename}
    Should Be Equal  ${result.status_code}  ${200}
    Log  ${result.json()}

deleteFile
    Create Session   filedelete   ${url}
    ${result} =  Delete Request  filedelete   /files/${filename} 
    Should Be Equal  ${result.status_code}  ${200}

createFile
    Create Session   filecreate   ${url}
    &{headers}=  Create Dictionary  Content-Type=application/json
    &{params}=  Create Dictionary   content=data   content1=data1

    ${result} =  Post Request  filecreate   /files/${filename}    headers=${headers}    data=${params}
    Should Be Equal  ${result.status_code}  ${201}
    Log  ${result.json()}

updateFile
    Create Session   fileupdate   ${url}
    &{headers}=  Create Dictionary  Content-Type=application/json
    &{params}=  Create Dictionary   content=data

    ${result} =  Put Request  fileupdate   /files/${filename}    headers=${headers}    data=${params}
    Should Be Equal  ${result.status_code}  ${200}
    Log  ${result.json()}
