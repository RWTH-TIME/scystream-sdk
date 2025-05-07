Release Notes
===========================================

scystream-sdk 1.0.0 - Release Notes
-----------------------------------

The first version of the scystream sdk.

Providing basic functionalities:

1. Defining entrypoints.

2. Introducing the cbc.yaml.

3. Defining settings for entrypoints, parsing ENV-Variables.

4. Parsing & cross validation of cbc.yaml with actual code definition.

5. Reading & writing to a postgres database, integrating Apache Spark.

6. Reading & writing from/to a S3 bucket, currently not using Apache Spark.

scystream-sdk 1.1.0 - Release Notes
-----------------------------------

1. Updated ENV settings.

   We have added two predefined classes for postgres and file in- and outputs.
   
   These contain default ENV-Keys such as the PG_HOST for defining the host of a postgres
   in-/ouput or S3_ACCESS_KEY for defining the access key of an S3 Bucket.

   These settings can ultimatively be used to configure the corresponding connections.

scystream-sdk 1.2.0 - Release Notes
-----------------------------------

1. Removed adjustable config path from SDKConfig

   The configuration option `config_path` was removed. Every compute block repository must now
   contain the `cbc.yaml` within it's root directory and with the file-name: `cbc.yaml`
    
