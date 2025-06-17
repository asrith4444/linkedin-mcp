import mimetypes
import requests
from config import ACCESS_TOKEN, FOLDER_PATH
import os


class LinkedInClient:
    API_BASE = "https://api.linkedin.com/v2"
    folder_path = os.path.expanduser(FOLDER_PATH)
    # Ensure the folder path exists

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def post_text(self, author_urn, text):
        """Publish a text-only post. Returns the post URN."""
        url = f"{self.API_BASE}/ugcPosts"
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        resp = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json().get("id")

    def _register_upload(self, author_urn):
        """Register an image upload and get upload URL + asset URN."""
        url = f"{self.API_BASE}/assets?action=registerUpload"
        payload = {
            "registerUploadRequest": {
                "owner": author_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [{
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER"
                }],
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
            }
        }
        resp = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json()

    def _upload_image(self, upload_url, file_path):
        """Upload binary image data to the given upload URL."""
        mime_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, "rb") as f:
            data = f.read()
        resp = requests.put(
            upload_url,
            data=data,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": mime_type or "application/octet-stream"
            }
        )
        resp.raise_for_status()

    def post_image(self, author_urn, text, image_paths):
        """Publish a post with one or more images. Returns the post URN."""
        media_entries = []
        # 1) Register & upload each image
        for path in image_paths:
            reg = self._register_upload(author_urn)
            path = os.path.join(self.folder_path, path)
            if not os.path.isfile(path):
                raise ValueError(f"Image file does not exist: {path}")
            upload_url = reg["value"]["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]
            asset_urn = reg["value"]["asset"]
            self._upload_image(upload_url, path)
            media_entries.append({"status": "READY", "media": asset_urn})

        # 2) Create the UGC post with media
        url = f"{self.API_BASE}/ugcPosts"
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": media_entries
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        resp = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json().get("id")
    
    def _register_video_upload(self, author_urn: str):
        """
        Tells LinkedIn you’re about to upload a video
        and returns an upload URL + asset URN.
        """
        url = f"{self.API_BASE}/assets?action=registerUpload"
        payload = {
            "registerUploadRequest": {
                "owner": author_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                "serviceRelationships": [{
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER"
                }],
                # small videos can often use synchronous PUT
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
            }
        }
        resp = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json()["value"]

    def _upload_video(self, upload_url: str, file_path: str):
        """
        Upload the video bytes to the URL LinkedIn gave you.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Video file does not exist: {file_path}")
        # Read the file in binary mode
        with open(file_path, "rb") as f:
            data = f.read()
        resp = requests.put(
            upload_url,
            data=data,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": mime_type or "application/octet-stream"
            }
        )
        resp.raise_for_status()

    def post_video(self,
                   author_urn: str,
                   text: str,
                   video_path: str,
                   title: str = None,
                   description: str = None) -> str:
        """
        Publish a post with a single video.
        Returns the post URN.
        """
        # 1) register & get upload info
        upload_info = self._register_video_upload(author_urn)
        upload_url = upload_info["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = upload_info["asset"]

        video_path = os.path.join(self.folder_path, video_path)

        # 2) upload the bytes
        self._upload_video(upload_url, video_path)

        # 3) build the UGC post
        media_entry = {
            "status": "READY",
            "description": {"text": description} if description else {},
            "media": asset_urn,
            "title": {"text": title} if title else {}
        }

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "VIDEO",
                    "media": [media_entry]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        resp = requests.post(
            f"{self.API_BASE}/ugcPosts",
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json().get("id")
    
