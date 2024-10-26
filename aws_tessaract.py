import boto3


def analyze_id(
    file_path, aws_access_key_id, aws_secret_access_key, region_name="us-east-1"
):
    """Analyzes an ID document from a local file path using Amazon Textract and returns the extracted data as JSON.

    Args:
        file_path (str): The path to the ID document file.
        aws_access_key_id (str): Your AWS access key ID.
        aws_secret_access_key (str): Your AWS secret access key.
        region_name (str): The AWS region where Textract is deployed. Default is 'us-east-1'.

    Returns:
        dict: A dictionary containing the extracted data in a structured format, suitable for JSON serialization.
    """
    # Initialize a boto3 session and Textract client
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    client = session.client("textract")

    # Read the image file
    with open(file_path, "rb") as document:
        image_bytes = document.read()

    # Analyze the ID document
    response = client.analyze_id(DocumentPages=[{"Bytes": image_bytes}])

    # Extract relevant data
    extracted_data = []
    for doc_fields in response["IdentityDocuments"]:
        for id_field in doc_fields["IdentityDocumentFields"]:
            field_data = {}
            for key, val in id_field.items():
                if "Type" in str(key):
                    field_data["Type"] = val["Text"]
                if "ValueDetection" in str(key):
                    field_data["Value"] = val["Text"]
            extracted_data.append(field_data)

    # Return data as a dictionary
    return {i["Type"]: i["Value"] for i in extracted_data}


# Example usage of the function
