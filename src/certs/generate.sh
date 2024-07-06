openssl genpkey -algorithm RSA -out private.key
openssl req -new -key private.key -out csr.pem -config san.cnf
openssl x509 -req -days 3650 -in csr.pem -signkey private.key -out certificate.crt -extensions v3_req -extfile san.cnf
cat private.key certificate.crt > certificate.pem