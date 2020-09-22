from google.cloud import storage
from pathlib import Path
import pandas as pd

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )



base_path = Path(__file__).parent/"csv_files"
def decapitate_proteins():
    # open file
    folder_path = base_path /"proteins"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)

    file_path = folder_path/'proteins_no_header_uploaded.csv'
    data_df.to_csv(file_path, header=False, index=False)

    upload_blob("genome-browser-bucket", file_path, "protein_upload_test.csv")


decapitate_proteins()

