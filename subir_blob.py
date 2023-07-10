# =============================================================================
# CERTIFICATES - UPLOAD AND DOWNLOAD
# =============================================================================

# download_blobs.py
# Python program to bulk download blob files from azure storage
# Uses latest python SDK() for Azure blob storage
# Requires python 3.6 or above
import os,uuid
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import ContentSettings, ContainerClient, __version__

class AzureBlob:
    def __init__(self, local_path, conn_str, container_name):
      print("Intializing Azure Blob Storage")
     
      # Initialize the connection to Azure storage account
      self.blob_service_client =  BlobServiceClient.from_connection_string(conn_str) #1
      print("Correct access to Blob Service Client")
      print("----------------------------------------")
      self.my_container = self.blob_service_client.get_container_client(container_name) #1
      print("Correct access to Container")
      print("----------------------------------------")
      self.container_client = ContainerClient.from_connection_string(conn_str, container_name) #2
      print("Correct access to Client and Container")
      print("----------------------------------------")
      
    
    def upload(self, file_name, certificado):
            # GET CLIENT AND UPLOAD
        # FIRST DELETE ANY FILE WITH THAT NAME
        self.delete_blob(file_name)
        try:
            # Try to get a client interact with an especific blob
            blob_client = self.container_client.get_blob_client(file_name)
            print("\nCorrect access to file")
        except:
            print("Could not access file in Container")
            return 0
        print("----------------------------------------")
        print("\nUploading to Azure Storage:\n\t" + file_name)
        print("...")
        try:
            blob_client.upload_blob(certificado)
            print(str(file_name), "Uploaded successfully")
        except:
            print("Error: Could not upload document")
     
    def download(self, file_name):
      my_blobs = self.my_container.list_blobs()
      for blob in my_blobs:
          if blob.name == file_name:
              #print(blob.name)
              bytes = self.my_container.get_blob_client(blob).download_blob().content_as_bytes()
              print("Downloaded successfully - ", str(blob.name))
              return bytes
    
    def delete_blob(self, file_name):
        blobs_list = self.my_container.list_blobs()
        for blob in blobs_list:
            if blob.name == file_name:
                self.my_container.delete_blob(blob.name)
        
    
    

# AB = AzureBlob(local_path, conn_str, container_name)

#AB.download("pruebas.txt")
#AB.delete_blob("pruebas2.txt")

#AB.upload("pruebas.txt")
#AB.download2("pruebas.txt")
#AB.print_file("pruebas.txt")

#read_file("./data/pruebas2.txt")
