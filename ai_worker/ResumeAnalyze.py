# connects to rabbitmq and consumes from queue: resume_analysis
from pathlib import Path
import json
import logging
import os
import pika
from pypdf import PdfReader
import time
import uuid

STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "/app/uploads")).resolve()
logging.basicConfig(level=logging.INFO)

def get_job_files(job_id):
    job_id = str(uuid.UUID(job_id))
    job_dir = (STORAGE_ROOT / job_id).resolve()
    job_dir.relative_to(STORAGE_ROOT)

    if not job_dir.is_dir():
        raise FileNotFoundError(f"Job directory {job_dir} does not exist.")

    resume_path = job_dir / "resume.pdf"
    job_description_path = job_dir / "job_description.txt"

    resume_path = resume_path.resolve()
    job_description_path = job_description_path.resolve()
    resume_path.relative_to(STORAGE_ROOT)
    job_description_path.relative_to(STORAGE_ROOT)

    if not resume_path.is_file() or not job_description_path.is_file():
        raise FileNotFoundError(f"Required files not found in {job_dir}.")

    metadata_path = job_dir / "job.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Job metadata not found in {job_dir}.")

    return job_id, job_dir, resume_path, job_description_path, metadata_path

def update_job_status(metadata_path, status):
    with metadata_path.open(encoding="utf-8") as file:
        metadata = json.load(file)

    metadata["Status"] = status
    temporary_path = metadata_path.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    temporary_path.replace(metadata_path)

def extract_resume_as_text(job_id, job_dir, resume_path, description_path, metadata_path):
    job_description = description_path.read_text(encoding="utf-8")
    if not job_description.strip():
        raise ValueError("The job description is empty.")

    reader = PdfReader(str(resume_path))
    resume_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not resume_text:
        raise ValueError("No extractable text found in the resume PDF.")

    extracted_text_path = job_dir / "resume_text.txt"
    temporary_text_path = job_dir / "resume_text.txt.tmp"
    temporary_text_path.write_text(resume_text, encoding="utf-8")
    temporary_text_path.replace(extracted_text_path)

    logging.info(
        "Extracted %d resume characters and read %d job-description characters for job %s",
        len(resume_text),
        len(job_description),
        job_id,
    )
    update_job_status(metadata_path, "TextExtracted")

def process_job(job_id):
    metadata_path = None
    try:
        job_id, job_dir, resume_path, description_path, metadata_path = get_job_files(job_id)
        update_job_status(metadata_path, "Processing")
        
        extract_resume_as_text(job_id, job_dir, resume_path, description_path, metadata_path)
    except Exception:
        logging.exception("Failed to process job %s", job_id)
        if metadata_path is not None:
            update_job_status(metadata_path, "Failed")
        raise

def consume_resume_job():

    # sets connection parameters
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USERNAME", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    queue_name = os.getenv("RABBITMQ_QUEUE", "resume_analysis")

    # connects to rabbitmq
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)

    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # declares the queue just in case
            channel.queue_declare(queue=queue_name, durable=True)

            def callback(ch, method, properties, body):
                try:
                    job_id = body.decode("utf-8").strip()
                    process_job(job_id)
                except Exception:
                    logging.exception("Rejecting failed resume job")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return

                logging.info("Finished processing job %s", job_id)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=callback)

            logging.info("Waiting for messages on queue %s", queue_name)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logging.exception("RabbitMQ consumer failed: %s", e)
            time.sleep(5)
        finally:
            if "connection" in locals() and connection.is_open:
                connection.close()

if __name__ == "__main__":
    consume_resume_job()