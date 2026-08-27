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
                self.portfolio_col = self.db.portfolio
                self.users_col = self.db.users
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
        self.portfolio_projects = []
        self.portfolio_current_id = 0
        self.users = []
        print("Using in-memory storage")

    # ---- Users ----

    def get_all_users(self):
        """Retrieve all users, shaped for streamlit-authenticator's credentials dict"""
        if self.use_mongodb:
            docs = list(self.users_col.find())
        else:
            docs = self.users

        usernames = {}
        for d in docs:
            usernames[d['username']] = {
                k: v for k, v in d.items()
                if k not in ('username', '_id', 'created_at')
            }
        return usernames

    def create_user(self, username, user_data):
        """Persist a newly registered user (password must already be hashed)"""
        doc = {'username': username, 'created_at': datetime.now().isoformat()}
        doc.update(user_data)

        if self.use_mongodb:
            self.users_col.insert_one(doc)
        else:
            self.users.append(doc)
        return doc

    # ---- Applications ----

    def add_application(self, user_id, data):
        """Add a new job application for a user"""
        data['user_id'] = user_id
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

    def get_all_applications(self, user_id):
        """Retrieve all job applications for a user, sorted by date"""
        if self.use_mongodb:
            apps = list(self.applications_col.find({"user_id": user_id}).sort("created_at", -1))
            for app in apps:
                app['id'] = str(app['_id'])
            return apps
        else:
            return sorted(
                [a for a in self.applications if a.get('user_id') == user_id],
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )

    def get_application(self, user_id, app_id):
        """Get a specific application by ID, scoped to its owner"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                app = self.applications_col.find_one({"_id": ObjectId(app_id), "user_id": user_id})
                if app:
                    app['id'] = str(app['_id'])
                return app
            except Exception:
                return None
        else:
            for app in self.applications:
                if app['id'] == app_id and app.get('user_id') == user_id:
                    return app
            return None

    def update_application(self, user_id, app_id, data):
        """Update an existing application, scoped to its owner"""
        data['updated_at'] = datetime.now().isoformat()

        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.applications_col.update_one(
                    {"_id": ObjectId(app_id), "user_id": user_id},
                    {"$set": data}
                )
                return self.get_application(user_id, app_id)
            except Exception:
                return None
        else:
            for i, app in enumerate(self.applications):
                if app['id'] == app_id and app.get('user_id') == user_id:
                    self.applications[i].update(data)
                    return self.applications[i]
            return None

    def delete_application(self, user_id, app_id):
        """Delete an application by ID, scoped to its owner"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.applications_col.delete_one({"_id": ObjectId(app_id), "user_id": user_id})
                return True
            except Exception:
                return False
        else:
            self.applications = [
                app for app in self.applications
                if not (app['id'] == app_id and app.get('user_id') == user_id)
            ]
            return True

    def get_statistics(self, user_id):
        """Calculate application statistics for a user"""
        apps = self.get_all_applications(user_id)
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

    # ---- Profile ----

    def get_profile(self, user_id):
        """Get a user's profile"""
        if self.use_mongodb:
            return self.profile_col.find_one({"user_id": user_id})
        else:
            if not hasattr(self, 'profiles'):
                self.profiles = {}
            return self.profiles.get(user_id)

    def save_profile(self, user_id, profile_data):
        """Save a user's profile"""
        profile_data['user_id'] = user_id

        if self.use_mongodb:
            # Delete old profile and insert new one
            self.profile_col.delete_many({"user_id": user_id})
            self.profile_col.insert_one(profile_data)
            return profile_data
        else:
            if not hasattr(self, 'profiles'):
                self.profiles = {}
            self.profiles[user_id] = profile_data
            return profile_data

    def update_profile(self, user_id, updates):
        """Update a user's profile"""
        if self.use_mongodb:
            self.profile_col.update_one({"user_id": user_id}, {"$set": updates}, upsert=True)
            return self.get_profile(user_id)
        else:
            if not hasattr(self, 'profiles'):
                self.profiles = {}
            profile = self.profiles.setdefault(user_id, {'user_id': user_id})
            profile.update(updates)
            return profile

    # ---- Portfolio ----

    def get_portfolio_projects(self, user_id):
        """Retrieve all portfolio projects for a user"""
        if self.use_mongodb:
            projects = list(self.portfolio_col.find({"user_id": user_id}).sort("created_at", 1))
            for p in projects:
                p['id'] = str(p['_id'])
            return projects
        else:
            return [p for p in self.portfolio_projects if p.get('user_id') == user_id]

    def add_portfolio_project(self, user_id, data):
        """Add a new portfolio project for a user"""
        data['user_id'] = user_id
        data['created_at'] = datetime.now().isoformat()

        if self.use_mongodb:
            result = self.portfolio_col.insert_one(data)
            data['_id'] = str(result.inserted_id)
            data['id'] = data['_id']
            return data
        else:
            data['id'] = self.portfolio_current_id
            self.portfolio_projects.append(data)
            self.portfolio_current_id += 1
            return data

    def update_portfolio_project(self, user_id, project_id, data):
        """Update a portfolio project (e.g. store generated write-up), scoped to its owner"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.portfolio_col.update_one(
                    {"_id": ObjectId(project_id), "user_id": user_id},
                    {"$set": data}
                )
                return True
            except Exception:
                return False
        else:
            for p in self.portfolio_projects:
                if p['id'] == project_id and p.get('user_id') == user_id:
                    p.update(data)
                    return True
            return False

    def delete_portfolio_project(self, user_id, project_id):
        """Delete a portfolio project by ID, scoped to its owner"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            try:
                self.portfolio_col.delete_one({"_id": ObjectId(project_id), "user_id": user_id})
                return True
            except Exception:
                return False
        else:
            self.portfolio_projects = [
                p for p in self.portfolio_projects
                if not (p['id'] == project_id and p.get('user_id') == user_id)
            ]
            return True
