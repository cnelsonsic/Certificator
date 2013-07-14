Certificator
============

[![Build Status](https://travis-ci.org/cnelsonsic/certificator.png?branch=master)](https://travis-ci.org/cnelsonsic/certificator)

Certificates that a person has the skills to pay the bills.

# Running
```bash
$ virtualenv .env
$ source .env/bin/activate
(.env) $ ./setup.py develop
(.env) $ certificator-server &
(.env) $ open http://127.0.0.1:5000
```

# Testing
```bash
(.env) $ ./setup.py nosetests
```
