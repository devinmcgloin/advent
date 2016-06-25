import http.client

conn = http.client.HTTPConnection("localhost:5000")

payload = "{\n  \"trigger\": \"message:appUser\",\n  \"messages\": [\n    {\n      \"authorId\": \"123jkh12jnsk1j232\",\n      \"received\": 1463970327.568,\n      \"text\": \"Hello! Is this thing on?\",\n      \"role\": \"appUser\",\n      \"_id\": \"j123hkj12bdmnbj23bk\",\n      \"source\": {\n        \"type\": \"messenger\"\n      },\n      \"actions\": []\n    }\n  ],\n  \"appUser\": {\n    \"_id\": \"02cd2a2d59461d69558f41e3\",\n    \"surname\": \"Example\",\n    \"givenName\": \"John\",\n    \"signedUpAt\": \"2016-05-19T18:18:03.736Z\",\n    \"conversationStarted\": true,\n    \"credentialRequired\": false,\n    \"devices\": [\n      {\n        \"lastSeen\": \"2016-05-23T02:25:28.385Z\",\n        \"id\": \"0c3cd52a-721a-4c85-a185-ca59358be92a\",\n        \"platform\": \"messenger\",\n        \"active\": true\n      }\n    ],\n    \"properties\": {}\n  }\n}"

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

while True:
    conn.request("POST", "/general", payload, headers)

    res = conn.getresponse()
    data = res.read()
