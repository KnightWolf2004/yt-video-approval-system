import os
import sys
import json
import time
import random
import argparse
import httplib2

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser


# Constants for YouTube Data API
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "../../client_secrets.json"))
CONFIG_FILE = os.path.abspath(os.path.join(SCRIPT_DIR, "upload_config.json"))
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Retry Configuration
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Privacy options allowed
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def load_video_config(config_path=CONFIG_FILE):
    if not os.path.exists(config_path):
        sys.exit(f"Config file '{config_path}' not found.")
    with open(config_path, "r") as f:
        config = json.load(f)
    # Validate minimum required fields
    if not os.path.exists(config.get("file", "")):
        sys.exit(f"Video file '{config.get('file')}' not found.")
    if config.get("privacyStatus", "private") not in VALID_PRIVACY_STATUSES:
        sys.exit(f"Invalid privacyStatus value: {config.get('privacyStatus')}. Must be one of {VALID_PRIVACY_STATUSES}")
    return config

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                  scope=YOUTUBE_UPLOAD_SCOPE,
                                  message=f"Missing {CLIENT_SECRETS_FILE}")
    storage = Storage(f"{sys.argv[0]}-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
    tags = options.get("keywords")
    if tags:
        tags = tags.split(",")
    else:
        tags = None

    body = dict(
        snippet=dict(
            title=options.get("title"),
            description=options.get("description"),
            tags=tags,
            categoryId=options.get("category")
        ),
        status=dict(
            privacyStatus=options.get("privacyStatus")
        )
    )

    media = MediaFileUpload(options.get("file"), chunksize=-1, resumable=True)

    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    resumable_upload(insert_request)

def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(f"Video id '{response['id']}' was successfully uploaded.")
                else:
                    sys.exit(f"The upload failed with an unexpected response: {response}")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                sys.exit("No longer attempting to retry.")
            sleep_seconds = random.uniform(0, 2 ** retry)
            print(f"Sleeping {sleep_seconds} seconds and then retrying...")
            time.sleep(sleep_seconds)
            error = None

def main():
    config = load_video_config()

    # Build argparse args compatible with oauth2client tools
    if argparser is None:
        parser = argparse.ArgumentParser(add_help=False)
    else:
        parser = argparse.ArgumentParser(parents=[argparser], add_help=False)

    args, unknown = parser.parse_known_args()

    youtube = get_authenticated_service(args)

    try:
        initialize_upload(youtube, config)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")

if __name__ == "__main__":
    main()
