\
\
\
\
\
\
\
\
\
\
\
\

import os
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_client() -> MongoClient:
\
\
\
\
\
\
\
\
\
\
\
\

    uri = os.environ.get("MONGODB_URI", "").strip()

    if not uri:
        st.error(
            "❌ **MONGODB_URI is not set.**\n\n"
            "- **Local:** Add `MONGODB_URI=...` to your `.env` file\n"
            "- **Streamlit Cloud:** Add it under App Settings → Secrets"
        )
        st.stop()

    try:
        client = MongoClient(
            uri,

            serverSelectionTimeoutMS=5000,

            maxPoolSize=10,
        )

        client.admin.command("ping")
        return client

    except ConfigurationError as e:

        st.error(
            f"❌ **MongoDB URI is malformed.**\n\n"
            f"Expected format: `mongodb+srv://user:password@cluster.mongodb.net/skillmap`\n\n"
            f"Error: `{e}`"
        )
        st.stop()

    except ServerSelectionTimeoutError:

        st.error(
            "❌ **Cannot connect to MongoDB Atlas.**\n\n"
            "Possible causes:\n"
            "- Your Atlas cluster is paused (free clusters pause after 60 days idle)\n"
            "- Your current IP address is not in the Atlas Network Access allowlist\n"
            "- Wrong username or password in the connection string\n\n"
            "Fix: Go to [MongoDB Atlas](https://cloud.mongodb.com) → "
            "Network Access → Add IP Address → Allow from anywhere (0.0.0.0/0)"
        )
        st.stop()

def get_db():
\
\
\
\
\
\
\
\
\
\
\
\
\
\

    return get_client()["skillmap"]

def ensure_indexes():
\
\
\
\
\
\
\
\
\
\

    db = get_db()

    db.users.create_index("email", unique=True)

    db.roadmaps.create_index("user_id")

    db.progress.create_index([("user_id", 1), ("roadmap_id", 1)])

    db.quizzes.create_index(
        [("roadmap_id", 1), ("subtopic_id", 1)],
        unique=True,
    )
