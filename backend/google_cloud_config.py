"""
Google Cloud Configuration and Setup
"""
import os
import logging
from typing import Optional, Dict, Any
from google.cloud import aiplatform, storage, bigquery, pubsub_v1, logging as cloud_logging
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

class GoogleCloudConfig:
    """Configuration class for Google Cloud services."""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.region = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
        self.credentials = None
        self.initialized = False
        
        # Service clients
        self.ai_platform_client = None
        self.storage_client = None
        self.bigquery_client = None
        self.pubsub_client = None
        self.logging_client = None
        
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize Google Cloud credentials."""
        try:
            # Try to get default credentials
            self.credentials, self.project_id = default()
            
            if not self.project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT_ID environment variable is required")
            
            logger.info(f"Google Cloud credentials initialized for project: {self.project_id}")
            self.initialized = True
            
        except DefaultCredentialsError:
            logger.error("Google Cloud credentials not found. Please set up authentication.")
            logger.info("To set up authentication, run: gcloud auth application-default login")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Google Cloud credentials: {e}")
            self.initialized = False
    
    def initialize_ai_platform(self):
        """Initialize Vertex AI platform."""
        if not self.initialized:
            logger.error("Google Cloud not initialized. Cannot initialize AI Platform.")
            return False
        
        try:
            aiplatform.init(
                project=self.project_id,
                location=self.region,
                credentials=self.credentials
            )
            self.ai_platform_client = aiplatform
            logger.info("Vertex AI platform initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {e}")
            return False
    
    def initialize_storage(self):
        """Initialize Cloud Storage client."""
        if not self.initialized:
            logger.error("Google Cloud not initialized. Cannot initialize Storage.")
            return False
        
        try:
            self.storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            logger.info("Cloud Storage client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Cloud Storage: {e}")
            return False
    
    def initialize_bigquery(self):
        """Initialize BigQuery client."""
        if not self.initialized:
            logger.error("Google Cloud not initialized. Cannot initialize BigQuery.")
            return False
        
        try:
            self.bigquery_client = bigquery.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            logger.info("BigQuery client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing BigQuery: {e}")
            return False
    
    def initialize_pubsub(self):
        """Initialize Pub/Sub client."""
        if not self.initialized:
            logger.error("Google Cloud not initialized. Cannot initialize Pub/Sub.")
            return False
        
        try:
            self.pubsub_client = pubsub_v1.PublisherClient()
            logger.info("Pub/Sub client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Pub/Sub: {e}")
            return False
    
    def initialize_logging(self):
        """Initialize Cloud Logging client."""
        if not self.initialized:
            logger.error("Google Cloud not initialized. Cannot initialize Logging.")
            return False
        
        try:
            self.logging_client = cloud_logging.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            logger.info("Cloud Logging client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Cloud Logging: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information."""
        return {
            'project_id': self.project_id,
            'region': self.region,
            'initialized': self.initialized,
            'services': {
                'ai_platform': self.ai_platform_client is not None,
                'storage': self.storage_client is not None,
                'bigquery': self.bigquery_client is not None,
                'pubsub': self.pubsub_client is not None,
                'logging': self.logging_client is not None
            }
        }

# Global instance
google_cloud_config = GoogleCloudConfig() 