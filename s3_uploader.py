import os
import sys
import boto3
import mimetypes
from datetime import datetime

# Configure defaults
DEFAULT_BUCKET = "ueda-qa-watch"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation_results")

def upload_simulation_results(bucket_name=DEFAULT_BUCKET):
    """
    Uploads all files in the simulation_results directory to the specified S3 bucket.
    """
    if not os.path.exists(RESULTS_DIR):
        print(f"Error: Results directory {RESULTS_DIR} does not exist.")
        return False

    s3 = boto3.client("s3")
    
    # Check if bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Error: Bucket '{bucket_name}' is not accessible or does not exist.")
        print(str(e))
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uploaded_files = []

    print(f"Starting upload to S3 bucket '{bucket_name}'...")
    
    for filename in os.listdir(RESULTS_DIR):
        filepath = os.path.join(RESULTS_DIR, filename)
        if os.path.isdir(filepath):
            continue

        # Determine MIME type
        content_type, _ = mimetypes.guess_type(filepath)
        if filename.endswith(".md"):
            content_type = "text/markdown; charset=utf-8"
        elif filename.endswith(".feature"):
            content_type = "text/plain; charset=utf-8"
        elif filename.endswith(".js") or filename.endswith(".spec.js"):
            content_type = "text/javascript; charset=utf-8"
        
        if not content_type:
            content_type = "application/octet-stream"

        # Construct S3 keys (both timestamped and latest)
        s3_key_timestamped = f"simulations/{timestamp}/{filename}"
        s3_key_latest = f"simulations/latest/{filename}"

        extra_args = {
            "ContentType": content_type
        }

        try:
            # Upload timestamped version
            s3.upload_file(filepath, bucket_name, s3_key_timestamped, ExtraArgs=extra_args)
            # Upload latest version
            s3.upload_file(filepath, bucket_name, s3_key_latest, ExtraArgs=extra_args)
            
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key_timestamped}"
            uploaded_files.append({
                "filename": filename,
                "s3_key": s3_key_timestamped,
                "s3_url": s3_url
            })
            print(f"  Uploaded {filename} -> s3://{bucket_name}/{s3_key_timestamped}")
        except Exception as e:
            print(f"  Failed to upload {filename}: {str(e)}")

    print(f"Upload complete. {len(uploaded_files)} files uploaded successfully.")
    return uploaded_files

if __name__ == "__main__":
    bucket = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BUCKET
    results = upload_simulation_results(bucket)
    if results:
        print("\nS3 URLs:")
        for r in results:
            print(f"- {r['filename']}: {r['s3_url']}")
    else:
        sys.exit(1)
