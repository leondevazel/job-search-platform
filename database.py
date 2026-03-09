from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        """Initialize MongoDB connection"""
        mongodb_uri = os.getenv("MONGODB_URI")
        
        if mongodb_uri and "mongodb" in mongodb_uri:
            # Use MongoDB
            try:
                self.client = MongoClient(mongodb_uri)
                self.db = self.client.job_tracker
                self.applications_col = self.db.applications
                self.profile_col = self.db.profile
                self.use_mongodb = True
                print("Connected to MongoDB!")
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                self._init_memory_storage()
        else:
            # Fallback to memory storage
            self._init_memory_storage()
    
    def _init_memory_storage(self):
        """Initialize in-memory storage as fallback"""
        self.use_mongodb = False
        self.applications = []
        self.current_id = 0
        print("Using in-memory storage")
    
    def add_application(self, data):
        """Add a new job application"""
        data['date_applied'] = datetime.now().strftime("%Y-%m-%d")
        data['created_at'] = datetime.now().isoformat()
        
        if self.use_mongodb:
            result = self.applications_col.insert_one(data)
            data['_id'] = str(result.inserted_id)
            return data
        else:
            data['id'] = self.current_id
            self.applications.append(data)
            self.current_id += 1
            return data
    
    def get_all_applications(self):
        """Retrieve all job applications sorted by date"""
        if self.use_mongodb:
            apps = list(self.applications_col.find().sort("created_at", -1))
            for app in apps:
                app['id'] = str(app['_id'])
            return apps
        else:
            return sorted(self.applications, 
                         key=lambda x: x.get('created_at', ''), 
                         reverse=True)
    
    def get_application(self, app_id):
        """Get a specific application by ID"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                app = self.applications_col.find_one({"_id": ObjectId(app_id)})
                if app:
                    app['id'] = str(app['_id'])
                return app
            except:
                return None
        else:
            for app in self.applications:
                if app['id'] == app_id:
                    return app
            return None
    
    def update_application(self, app_id, data):
        """Update an existing application"""
        data['updated_at'] = datetime.now().isoformat()
        
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.applications_col.update_one(
                    {"_id": ObjectId(app_id)},
                    {"$set": data}
                )
                return self.get_application(app_id)
            except:
                return None
        else:
            for i, app in enumerate(self.applications):
                if app['id'] == app_id:
                    self.applications[i].update(data)
                    return self.applications[i]
            return None
    
    def delete_application(self, app_id):
        """Delete an application by ID"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.applications_col.delete_one({"_id": ObjectId(app_id)})
                return True
            except:
                return False
        else:
            self.applications = [app for app in self.applications 
                               if app['id'] != app_id]
            return True
    
    def get_statistics(self):
        """Calculate application statistics"""
        apps = self.get_all_applications()
        total = len(apps)
        
        if total == 0:
            return {
                'total': 0,
                'applied': 0,
                'interview': 0,
                'offer': 0,
                'rejected': 0
            }
        
        stats = {
            'total': total,
            'applied': len([a for a in apps if a.get('status') == 'Applied']),
            'interview': len([a for a in apps if a.get('status') == 'Interview']),
            'offer': len([a for a in apps if a.get('status') == 'Offer']),
            'rejected': len([a for a in apps if a.get('status') == 'Rejected'])
        }
        return stats
    
    def get_profile(self):
        """Get user profile"""
        if self.use_mongodb:
            profile = self.profile_col.find_one()
            return profile
        else:
            if hasattr(self, 'profile'):
                return self.profile
            return None
    
    def save_profile(self, profile_data):
        """Save user profile"""
        if self.use_mongodb:
            # Delete old profile and insert new one
            self.profile_col.delete_many({})
            self.profile_col.insert_one(profile_data)
            return profile_data
        else:
            self.profile = profile_data
            return self.profile
    
    def update_profile(self, updates):
        """Update user profile"""
        if self.use_mongodb:
            self.profile_col.update_one({}, {"$set": updates}, upsert=True)
            return self.get_profile()
        else:
            if not hasattr(self, 'profile'):
                self.profile = {}
            self.profile.update(updates)
            return self.profile