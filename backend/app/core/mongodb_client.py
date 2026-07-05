"""
MongoDB client configuration and CSV fallback utilities for sensor data storage
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.core.csv_storage import CSVStorage


class MongoDBService:
    """Service for interacting with MongoDB (with CSV fallback)."""
    
    def __init__(self):
        self.csv_storage = CSVStorage()
        self.available = False
        try:
            self.client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=2000
            )
            # Trigger connection
            self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DATABASE]
            self.collection = self.db.sensor_readings
            self.collection.create_index([("measurement", 1), ("timestamp", -1)])
            self.collection.create_index([("device_id", 1), ("timestamp", -1)])
            self.collection.create_index([("sensor_id", 1), ("timestamp", -1)])
            self.collection.create_index("timestamp")
            self.db.actuator_states.create_index([("actuator_id", 1), ("timestamp", -1)])
            self.db.actuator_states.create_index("timestamp")
            self.available = True
        except PyMongoError:
            self.client = None
            self.db = None
            self.collection = None
    
    def write_sensor_data(
        self,
        measurement: str,
        device_id: str,
        sensor_id: str,
        value: float,
        timestamp: int = None,
        tags: dict = None
    ):
        """
        Write sensor data to MongoDB
        
        Args:
            measurement: Measurement name (e.g., 'temperature', 'humidity')
            device_id: Device identifier
            sensor_id: Sensor identifier
            value: Sensor reading value
            timestamp: Unix timestamp (optional, defaults to now)
            tags: Additional tags (optional)
        """
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp())
        
        if not self.available:
            self.csv_storage.write_sensor_data(
                measurement=measurement,
                device_id=device_id,
                sensor_id=sensor_id,
                value=value,
                timestamp=timestamp,
                tags=tags
            )
            return
        
        document = {
            "measurement": measurement,
            "device_id": device_id,
            "sensor_id": sensor_id,
            "value": value,
            "timestamp": timestamp,
            "created_at": datetime.utcnow()
        }
        
        if tags:
            document.update({f"tag_{k}": v for k, v in tags.items()})
        
        self.collection.insert_one(document)
    
    def query_sensor_data(
        self,
        measurement: str,
        device_id: str = None,
        sensor_id: str = None,
        start_time: str = None,
        stop_time: str = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Query sensor data from MongoDB
        
        Args:
            measurement: Measurement name
            device_id: Filter by device_id (optional)
            sensor_id: Filter by sensor_id (optional)
            start_time: Start time (ISO format or Unix timestamp, optional)
            stop_time: Stop time (ISO format or Unix timestamp, optional)
            limit: Maximum number of records to return
        """
        if start_time:
            start_dt = self._parse_datetime(start_time)
            start_ts = int(start_dt.timestamp())
        else:
            start_ts = int((datetime.utcnow() - timedelta(hours=1)).timestamp())
        stop_ts = int(self._parse_datetime(stop_time).timestamp()) if stop_time else None
        
        if not self.available:
            return self.csv_storage.query_sensor_data(
                measurement=measurement,
                device_id=device_id,
                sensor_id=sensor_id,
                start_time=start_ts,
                stop_time=stop_ts,
                limit=limit
            )
        
        query = {
            "measurement": measurement,
            "timestamp": {"$gte": start_ts}
        }
        if stop_ts:
            query["timestamp"]["$lte"] = stop_ts
        if device_id:
            query["device_id"] = device_id
        if sensor_id:
            query["sensor_id"] = sensor_id
        
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        
        data = []
        for doc in cursor:
            data.append({
                "time": datetime.fromtimestamp(doc["timestamp"]).isoformat(),
                "measurement": doc["measurement"],
                "device_id": doc["device_id"],
                "sensor_id": doc["sensor_id"],
                "value": doc["value"]
            })
        
        # Reverse to get chronological order
        return list(reversed(data))
    
    def get_aggregated_data(
        self,
        measurement: str,
        device_id: str = None,
        sensor_id: str = None,
        window: str = "1h",
        aggregate: str = "mean"
    ) -> List[Dict]:
        """
        Get aggregated sensor data
        
        Args:
            measurement: Measurement name
            device_id: Filter by device_id (optional)
            sensor_id: Filter by sensor_id (optional)
            window: Time window (e.g., "1h", "5m")
            aggregate: Aggregation function (mean, max, min, sum)
        """
        if not self.available:
            return self.csv_storage.get_aggregated_data(
                measurement=measurement,
                device_id=device_id,
                sensor_id=sensor_id,
                window=window,
                aggregate=aggregate
            )
        
        # Parse window (e.g., "1h" -> 1 hour, "5m" -> 5 minutes)
        window_value = int(window[:-1])
        window_unit = window[-1]
        
        if window_unit == 'h':
            delta = timedelta(hours=window_value)
            bin_size_seconds = window_value * 3600
        elif window_unit == 'm':
            delta = timedelta(minutes=window_value)
            bin_size_seconds = window_value * 60
        elif window_unit == 'd':
            delta = timedelta(days=window_value)
            bin_size_seconds = window_value * 86400
        else:
            delta = timedelta(hours=1)  # default
            bin_size_seconds = 3600
        
        start_time = int((datetime.utcnow() - delta).timestamp())
        
        query = {
            "measurement": measurement,
            "timestamp": {"$gte": start_time}
        }
        
        if device_id:
            query["device_id"] = device_id
        
        if sensor_id:
            query["sensor_id"] = sensor_id
        
        # Determine aggregation operator
        agg_operator = "$avg" if aggregate == "mean" else \
                      "$max" if aggregate == "max" else \
                      "$min" if aggregate == "min" else \
                      "$sum"
        
        # Use MongoDB aggregation pipeline with simpler grouping
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "$subtract": [
                            "$timestamp",
                            {"$mod": ["$timestamp", bin_size_seconds]}
                        ]
                    },
                    "value": {agg_operator: "$value"},
                    "measurement": {"$first": "$measurement"},
                    "device_id": {"$first": "$device_id"},
                    "sensor_id": {"$first": "$sensor_id"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        data = []
        for result in results:
            timestamp_dt = datetime.fromtimestamp(result["_id"])
            data.append({
                "time": timestamp_dt.isoformat(),
                "measurement": result["measurement"],
                "device_id": result["device_id"],
                "sensor_id": result["sensor_id"],
                "value": round(result["value"], 2)
            })
        
        return data
    
    def get_distinct_measurements(self) -> List[str]:
        """Get list of distinct measurement types"""
        if not self.available:
            return self.csv_storage.get_distinct_measurements()
        return self.collection.distinct("measurement")
    
    def get_distinct_devices(self) -> List[str]:
        """Get list of distinct device IDs"""
        if not self.available:
            return self.csv_storage.get_distinct_devices()
        return self.collection.distinct("device_id")
    
    def write_actuator_state(self, actuator_state):
        """
        Write actuator state to MongoDB
        
        Args:
            actuator_state: ActuatorState object
        """
        timestamp = actuator_state.timestamp or int(datetime.utcnow().timestamp())
        if not self.available:
            self.csv_storage.write_actuator_state(
                actuator_id=actuator_state.actuator_id,
                device_id=actuator_state.device_id,
                actuator_type=actuator_state.actuator_type,
                state=actuator_state.state,
                value=actuator_state.value,
                timestamp=timestamp,
                tags=actuator_state.tags
            )
            return
        
        collection = self.db.actuator_states

        document = {
            "actuator_id": actuator_state.actuator_id,
            "device_id": actuator_state.device_id,
            "actuator_type": actuator_state.actuator_type,
            "state": actuator_state.state,
            "value": actuator_state.value,
            "timestamp": timestamp,
            "created_at": datetime.utcnow()
        }
        
        if actuator_state.tags:
            document.update({f"tag_{k}": v for k, v in actuator_state.tags.items()})
        
        collection.insert_one(document)
    
    def get_actuator_states(
        self,
        actuator_id: str = None,
        device_id: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get actuator states from MongoDB
        
        Args:
            actuator_id: Filter by actuator_id (optional)
            device_id: Filter by device_id (optional)
            limit: Maximum number of records to return
        """
        if not self.available:
            return self.csv_storage.get_actuator_states(
                actuator_id=actuator_id,
                device_id=device_id,
                limit=limit
            )
        
        collection = self.db.actuator_states
        
        query = {}
        if actuator_id:
            query["actuator_id"] = actuator_id
        if device_id:
            query["device_id"] = device_id
        
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        
        data = []
        for doc in cursor:
            data.append({
                "time": datetime.fromtimestamp(doc["timestamp"]).isoformat(),
                "actuator_id": doc["actuator_id"],
                "device_id": doc["device_id"],
                "actuator_type": doc["actuator_type"],
                "state": doc["state"],
                "value": doc.get("value")
            })
        
        return list(reversed(data))
    
    def get_current_actuator_states(self) -> List[Dict]:
        """Get the most recent state of each actuator"""
        if not self.available:
            return self.csv_storage.get_current_actuator_states()
        
        collection = self.db.actuator_states
        
        # Get distinct actuator IDs
        actuator_ids = collection.distinct("actuator_id")
        
        current_states = []
        for actuator_id in actuator_ids:
            latest = collection.find({"actuator_id": actuator_id}).sort("timestamp", -1).limit(1)
            for doc in latest:
                current_states.append({
                    "actuator_id": doc["actuator_id"],
                    "device_id": doc["device_id"],
                    "actuator_type": doc["actuator_type"],
                    "state": doc["state"],
                    "value": doc.get("value"),
                    "time": datetime.fromtimestamp(doc["timestamp"]).isoformat()
                })
        
        return current_states
    
    def close(self):
        """Close MongoDB client connections"""
        if self.client:
            self.client.close()

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        if not value:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            return datetime.fromtimestamp(int(value))


# Global instance
mongodb_service = MongoDBService()

