# **Genome browser project**

## Setting up
To be able to run the app locally, change the datasets, or deploy a new version of the app, you need to do this setup first

>Prerequisities: Git, pip and python (3.7.3 or newer) installed. GCP privileges for relevant parts of the project.

1. Ensure you have the updated repository version

    - If you don't have the repository locally, clone it from GitHub:

        `git clone https://github.com/ML-Bioinfo-CEITEC/genome_browser.git`
        
    - otherwise, update the repository

        `git pull`

2. Enter the api folder

    `cd api/`

3. install packages

    `pip install -r requirements.txt` 


4. Go to GCP website and download secrets.py file from [genome-browser-secrets-bucket](https://console.cloud.google.com/storage/browser/genome-browser-secrets-bucket;tab=objects?forceOnBucketsSortingFiltering=false&project=spring-ranger-289710&prefix=&forceOnObjectsSortingFiltering=false).
5. Put the `secrets.py` file to the `api/db` folder
6. Run `db/yaml_gen.py` script (for example in console with `python db/yaml_gen.py` command)

7. Whitelist your IP in public IP section of the SQL database (Needed only for local running and new dataset upload)
    - go to [database connections tab](https://console.cloud.google.com/sql/instances/genome-browser-db/connections?project=spring-ranger-289710)
    - click on add network and add your [ipv4 adress](https://whatismyipaddress.com/) to the list

    ![](https://user-images.githubusercontent.com/30112906/94141254-c0099d00-fe6c-11ea-92e4-bcc4dc2b0b8f.PNG)

    - click Save

## Running the app locally
> Prerequisities: you have completed the setting up part
1) go to `db/config.py` and change the `deploy_mode` variable to `False`
2) from the `api` folder, run the command `python main.py`
3) the app is now running on your local URL (printed to console) connected to GCP SQL database
4) [Optional] If you want to change the database connection to a local database, change the POSTGRES dictionary values in secrets.py (`public host` variable would be `localhost`)
5) [Optional] Change the `app.config['DEBUG']` to `True` in `main.py` to see debug messages when developing the app


## Uploading new data
> Prerequisities: you have completed the setting up part

1) Ensure your data is in csv format with columns ordered like this:

- Genes: `id,symbol,biotype,chr,start,end,strand`

- Binding sites: `protein_name,chr,start,end,strand,score,note`

- Proteins: `protein_name,protein_id,uniprot_url`

2) Put the three CSV files into the `api/db/csv_files` directory
3) go to `import_preparation.py` script and put the csv names to relevant variables
4) run the `import_preparation.py` script. The new, preprocessed csv files will be in `api/db/csv_files/prepared` folder. **This step will delete all rows in the database, so the user will see no results until you complete the following steps.**
5) go to [genome-browser-bucket](https://console.cloud.google.com/storage/browser/genome-browser-bucket;tab=objects?forceOnBucketsSortingFiltering=false&project=spring-ranger-289710&prefix=&forceOnObjectsSortingFiltering=false) and upload the prepared files there
6) go to the [database page](https://console.cloud.google.com/sql/instances/genome-browser-db/overview?project=spring-ranger-289710) and click import

![](https://user-images.githubusercontent.com/30112906/94155800-a3c32b80-fe7f-11ea-8f01-bbee539a6c5d.PNG)

- For each separate prepared csv file do the following 
    - select the `genome-browser-bucket` and select the prepared csv file
    - verify the csv format is chosen
    - select the `genome_data_db` database
    - type in the table name (`genes`, `binding_sites` or `proteins`), depending on the chosen file
    - click import
    - wait until the file is transformed into table and click the import button at the top again

7) After all the csv files are put into database, run the `import_finish.py`, creating the final table
8) [Optional] - delete the csv files from `genome-browser-bucket`


## Deploying new version
> Prerequisities: you have completed the setting up part
1) install [google cloud sdk](https://cloud.google.com/sdk/docs/install) if it's not already installed. 
    - Check the run 'gcloud init' checkbox at the end.
    - Select the spring-ranger-289710 project in the console when `gcloud init` is executed.
    - Configure the default Compute Region and Zone to `europe-west3-a` region
2) In the Google cloud sdk shell, ensure you're in the `api` folder of the project
3) Ensure the `deploy_mode` variable in  `db/config.py` is set to `True`
4) run `gcloud app deploy` command (this will upload all local files from the api folder to GCP, including unstaged files)
5) confirm the deployment with `Y` command on prompt
6) [Optional] Delete the old version from the [app engine page](https://console.cloud.google.com/appengine/versions?project=spring-ranger-289710&serviceId=default)


## Changing the app or database configuration
The app engine server's configuration is specified in the `app.yaml` file, generated from the data in `secrets.py`.

If you want to deploy the app with new configuration, change the `app.yaml` file according to the [official docs](https://cloud.google.com/appengine/docs/standard/python3/config/appref).

If you want to change the database connection, change the `POSTGRES` variable in secrets.py

If you want these new configurations to be the new default, upload the new `secrets.py` to the [genome-browser-secrets-bucket](https://console.cloud.google.com/storage/browser/genome-browser-secrets-bucket;tab=objects?forceOnBucketsSortingFiltering=false&project=spring-ranger-289710&prefix=&forceOnObjectsSortingFiltering=false) and notify other team members to update their local `secrets.py` files and then regenerate app.yaml file with `yaml_gen.py` script.

## Codebase 
### main.py
This is the root file of the application, running it will launch a server listening for HTTP requests.

### routes.py
This is the file containing the API logic. Currently, there are two endpoints

'/' endpoint returns the rendered HTML file with the paginated results based on the parameters in the request

'/download' endpoint returns the CSV file with filtered data based on the parameters in the request

### templates folder 
This folder contains all the HTML templates that are rendered, using jinja2 syntax.

### secrets.py 
This file contains all the secrets of the app, **do not share this file in any public way**. If you want to update the secrets.py file, upload the new version to the `genome-browser-secrets-bucket` on GCP.

### requirements.txt 
This file contains all the required packages for the app. If you update the app with new dependencies, update this file and push it to github. Updating the file can be done with the command `pip freeze > requirements.txt` in the `api` folder

### html_content.py
This file contains specific text areas of the website, which can be directly modified.

### Helper scripts
`yaml_gen`, `import_preparation` and `import_finish` are helper scripts used for deployment and database updating. Their use is described in the relevant tutorials.


