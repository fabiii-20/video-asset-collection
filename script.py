import os
import requests

def download_file(url, folder, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(os.path.join(folder, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

def process_link(link):
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {link}. Status code: {response.status_code}")
        return

    data = response.json()

    _id = data.get("_id")
    if not _id:
        print("No ID found in the response.")
        return

    folder_name = _id
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Thumbnail Image
    thumbnail_href = data.get("thumbnail", {}).get("href")
    if thumbnail_href:
        thumbnail_url = f"http://img-prod-cms-rt-microsoft-com.akamaized.net/{thumbnail_href}"
        download_file(thumbnail_url, folder_name, f"{_id}_tbmnl.jpg")

    # Process binary references
    binary_references = data.get("_links", {}).get("binaryReferences", [])
    if not binary_references:
        print(f"No binaryReferences found for {_id}")
        return

    for item in binary_references:
        item_type = item.get("$type")
        source_href = item.get("sourceHref")
        alias = item.get("alias")
        locale = item.get("locale", "default")  # Fallback to "default" if locale is missing

        if item_type == "videoClosedCaptionBinaryReference":
            if item.get("extension") == "ttml":
                file_name = f"{_id}_cc_{locale}.ttml"
                download_file(source_href, folder_name, file_name)
            elif item.get("extension") == "vtt":
                file_name = f"{_id}_cc_{locale}.vtt"
                download_file(source_href, folder_name, file_name)
        
        elif item_type == "audioBinaryReference":
            file_name = f"{_id}_audio_{locale}.mp3"
            download_file(source_href, folder_name, file_name)
        
        elif item_type == "videoTranscriptBinaryReference":
            file_name = f"{_id}_transcript_{locale}.txt"
            download_file(source_href, folder_name, file_name)

        elif item_type == "videoBinaryReference" and alias == "1001":
            file_name = f"{folder_name}_video_en-us.mp4"
            download_file(source_href, folder_name, file_name)

def main():
    links = [
        "https://query.prod.cms.rt.microsoft.com/cms/api/am/videoFileData/RE3rrFX",
        # Add more links as needed
    ]
    
    for link in links:
        process_link(link)

if __name__ == "__main__":
    main()
