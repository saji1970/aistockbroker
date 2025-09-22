"""
Cloud Storage Service for Data Management
"""
import logging
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from google.cloud import storage
from google_cloud_config import google_cloud_config

logger = logging.getLogger(__name__)

class CloudStorageService:
    """Service for managing data in Google Cloud Storage."""
    
    def __init__(self, bucket_name: str = None):
        """Initialize Cloud Storage service."""
        self.bucket_name = bucket_name or f"{google_cloud_config.project_id}-stock-data"
        self.client = None
        self.bucket = None
        
        if google_cloud_config.initialized:
            self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Cloud Storage client."""
        try:
            if google_cloud_config.initialize_storage():
                self.client = google_cloud_config.storage_client
                self._ensure_bucket_exists()
                logger.info(f"Cloud Storage initialized with bucket: {self.bucket_name}")
            else:
                logger.error("Failed to initialize Cloud Storage")
        except Exception as e:
            logger.error(f"Error initializing Cloud Storage: {e}")
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if it doesn't."""
        try:
            self.bucket = self.client.bucket(self.bucket_name)
            
            if not self.bucket.exists():
                self.bucket.create()
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Using existing bucket: {self.bucket_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
    
    def save_stock_data(self, symbol: str, data: pd.DataFrame, period: str = "1y") -> bool:
        """Save stock data to Cloud Storage."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return False
            
            # Convert DataFrame to JSON
            data_json = data.to_json(orient='records', date_format='iso')
            
            # Create blob name
            timestamp = datetime.now().strftime("%Y%m%d")
            blob_name = f"stock_data/{symbol}/{period}/{timestamp}.json"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(data_json, content_type='application/json')
            
            logger.info(f"Saved stock data for {symbol} to {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving stock data for {symbol}: {e}")
            return False
    
    def load_stock_data(self, symbol: str, period: str = "1y", date: str = None) -> Optional[pd.DataFrame]:
        """Load stock data from Cloud Storage."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return None
            
            # Determine blob name
            if date:
                blob_name = f"stock_data/{symbol}/{period}/{date}.json"
            else:
                # Get the most recent file
                blobs = list(self.client.list_blobs(
                    self.bucket_name, 
                    prefix=f"stock_data/{symbol}/{period}/"
                ))
                
                if not blobs:
                    logger.warning(f"No data found for {symbol}")
                    return None
                
                # Get the most recent blob
                latest_blob = max(blobs, key=lambda b: b.name)
                blob_name = latest_blob.name
            
            # Download from Cloud Storage
            blob = self.bucket.blob(blob_name)
            data_json = blob.download_as_text()
            
            # Convert JSON to DataFrame
            data = pd.read_json(data_json, orient='records')
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
            
            logger.info(f"Loaded stock data for {symbol} from {blob_name}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading stock data for {symbol}: {e}")
            return None
    
    def save_portfolio_state(self, portfolio_id: str, portfolio_data: Dict) -> bool:
        """Save portfolio state to Cloud Storage."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return False
            
            # Convert to JSON
            data_json = json.dumps(portfolio_data, default=str)
            
            # Create blob name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"portfolios/{portfolio_id}/state_{timestamp}.json"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(data_json, content_type='application/json')
            
            logger.info(f"Saved portfolio state for {portfolio_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving portfolio state: {e}")
            return False
    
    def load_portfolio_state(self, portfolio_id: str) -> Optional[Dict]:
        """Load the latest portfolio state from Cloud Storage."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return None
            
            # Get the most recent portfolio state
            blobs = list(self.client.list_blobs(
                self.bucket_name, 
                prefix=f"portfolios/{portfolio_id}/"
            ))
            
            if not blobs:
                logger.warning(f"No portfolio state found for {portfolio_id}")
                return None
            
            # Get the most recent blob
            latest_blob = max(blobs, key=lambda b: b.name)
            
            # Download from Cloud Storage
            data_json = latest_blob.download_as_text()
            portfolio_data = json.loads(data_json)
            
            logger.info(f"Loaded portfolio state for {portfolio_id}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error loading portfolio state: {e}")
            return None
    
    def save_backtest_results(self, backtest_id: str, results: Dict) -> bool:
        """Save backtest results to Cloud Storage."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return False
            
            # Convert to JSON
            data_json = json.dumps(results, default=str)
            
            # Create blob name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"backtests/{backtest_id}/results_{timestamp}.json"
            
            # Upload to Cloud Storage
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(data_json, content_type='application/json')
            
            logger.info(f"Saved backtest results for {backtest_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving backtest results: {e}")
            return False
    
    def list_stored_symbols(self) -> List[str]:
        """List all symbols with stored data."""
        try:
            if not self.bucket:
                logger.error("Cloud Storage not initialized")
                return []
            
            blobs = list(self.client.list_blobs(
                self.bucket_name, 
                prefix="stock_data/"
            ))
            
            symbols = set()
            for blob in blobs:
                # Extract symbol from blob name: stock_data/SYMBOL/period/date.json
                parts = blob.name.split('/')
                if len(parts) >= 2:
                    symbols.add(parts[1])
            
            return list(symbols)
            
        except Exception as e:
            logger.error(f"Error listing stored symbols: {e}")
            return []
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information and statistics."""
        try:
            if not self.bucket:
                return {'error': 'Cloud Storage not initialized'}
            
            # Get bucket statistics
            blobs = list(self.client.list_blobs(self.bucket_name))
            
            total_size = sum(blob.size for blob in blobs)
            total_files = len(blobs)
            
            # Count by type
            stock_data_files = len([b for b in blobs if b.name.startswith('stock_data/')])
            portfolio_files = len([b for b in blobs if b.name.startswith('portfolios/')])
            backtest_files = len([b for b in blobs if b.name.startswith('backtests/')])
            
            return {
                'bucket_name': self.bucket_name,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'file_types': {
                    'stock_data': stock_data_files,
                    'portfolios': portfolio_files,
                    'backtests': backtest_files
                },
                'symbols': self.list_stored_symbols()
            }
            
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {'error': str(e)}

# Global instance
cloud_storage_service = CloudStorageService() 