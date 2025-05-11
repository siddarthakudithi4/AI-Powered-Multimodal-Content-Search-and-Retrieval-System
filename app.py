# # from dotenv import load_dotenv
# # import os
# # import urllib.parse
# # from pymongo import MongoClient
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # from datetime import datetime
# # import uuid
# # import shutil

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]

# # # --- Image storage setup ---
# # IMAGE_STORAGE = "stored_images"
# # os.makedirs(IMAGE_STORAGE, exist_ok=True)

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}"
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     image_id = str(uuid.uuid4())
# #     filename = f"{image_id}.jpg"
# #     filepath = os.path.join(IMAGE_STORAGE, filename)
# #     try:
# #         img.save(filepath, "JPEG")
# #         collection.insert_one({
# #             "_id": image_id,
# #             "description": description,
# #             "image_path": filepath,
# #             "created_at": datetime.now()
# #         })
# #         return image_id
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         return list(results)
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         collection.delete_many({})
# #         shutil.rmtree(IMAGE_STORAGE)
# #         os.makedirs(IMAGE_STORAGE, exist_ok=True)
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     st.image(Image.open(doc["image_path"]), caption=f"ID: {doc['_id']}", width=150)
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()



# # from dotenv import load_dotenv
# # import os
# # import urllib.parse
# # from pymongo import MongoClient
# # import gridfs
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # from datetime import datetime
# # import uuid
# # import io

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY or not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ Missing environment variables.")
# #     st.stop()

# # # --- MongoDB connection ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]
# # fs = gridfs.GridFS(db)

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Helpers ---
# # def clean_text(text):
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people, place, activity = "NONE", "unknown location", "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people": people = val
# #                 elif key == "place": place = val
# #                 elif key == "activity": activity = val
# #         summary = f"{'No people' if people.lower() == 'none' else people} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}"
# #         return summary
# #     except Exception as e:
# #         st.error(f"❌ Error parsing model response: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     try:
# #         buffer = io.BytesIO()
# #         img.save(buffer, format="JPEG")
# #         buffer.seek(0)
# #         image_id = fs.put(buffer.getvalue(), filename=f"{uuid.uuid4()}.jpg")
# #         collection.insert_one({
# #             "gridfs_id": image_id,
# #             "description": description,
# #             "created_at": datetime.utcnow()
# #         })
# #         return str(image_id)
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         return list(collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1))
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     return collection.count_documents({})

# # def clear_database():
# #     try:
# #         for doc in collection.find():
# #             fs.delete(doc["gridfs_id"])
# #         collection.delete_many({})
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - Image AI via MongoDB + Gemini")
# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #                     st.info(f"📝 Description: {summary}")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter description:", placeholder="e.g., a man in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} result(s)")
# #             for doc in results:
# #                 image_bytes = fs.get(doc["gridfs_id"]).read()
# #                 img = Image.open(io.BytesIO(image_bytes))
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No images found. Try different keywords.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()

# # from dotenv import load_dotenv
# # import os
# # import urllib.parse
# # from pymongo import MongoClient
# # import gridfs
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # from datetime import datetime
# # import uuid
# # import io

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection and GridFS setup ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]
# # fs = gridfs.GridFS(db)  # Initialize GridFS for storing large files (like images)

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}"
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     image_id = str(uuid.uuid4())  # Generate unique ID for the image
# #     try:
# #         # Convert the image to binary and store it in GridFS
# #         img_binary = img.tobytes()
# #         file_id = fs.put(img_binary, filename=f"{image_id}.jpg")  # Store image in GridFS
        
# #         # Insert metadata into the 'images' collection
# #         collection.insert_one({
# #             "_id": image_id,
# #             "description": description,
# #             "image_id": file_id,  # Store the GridFS file ID
# #             "created_at": datetime.now()
# #         })
# #         return image_id
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         images = []
# #         for doc in results:
# #             img_data = fs.get(doc['image_id']).read()  # Get the image from GridFS
# #             images.append({
# #                 "image_data": img_data,
# #                 "description": doc['description'],
# #                 "created_at": doc['created_at'],
# #                 "_id": doc['_id']
# #             })
# #         return images
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         collection.delete_many({})
# #         fs.delete_many({})  # Delete all images from GridFS
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     img = Image.open(io.BytesIO(doc["image_data"]))  # Read image from binary data
# #                     st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()









# # import os
# # import uuid
# # import io
# # import shutil
# # from datetime import datetime
# # from dotenv import load_dotenv
# # import urllib.parse
# # from pymongo import MongoClient
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # import gridfs

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]

# # # --- GridFS setup ---
# # fs = gridfs.GridFS(db)

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # # --- Image storage setup ---
# # IMAGE_STORAGE = "stored_images"
# # os.makedirs(IMAGE_STORAGE, exist_ok=True)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}."
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     image_id = str(uuid.uuid4())
# #     try:
# #         # Save the image to GridFS as binary data
# #         with io.BytesIO() as img_io:
# #             img.save(img_io, format='JPEG')
# #             img_io.seek(0)
# #             file_id = fs.put(img_io, filename=f"{image_id}.jpg", content_type="image/jpeg")

# #         # Store metadata in MongoDB
# #         collection.insert_one({
# #             "_id": image_id,
# #             "description": description,
# #             "image_id": file_id,
# #             "created_at": datetime.now()
# #         })
# #         return image_id
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         images = []
# #         for doc in results:
# #             img_data = fs.get(doc['image_id']).read()  # Get the image from GridFS
# #             try:
# #                 img = Image.open(io.BytesIO(img_data))  # Read image from binary data
# #                 img.verify()  # Verify that the image is valid
# #                 images.append({
# #                     "image_data": img_data,
# #                     "description": doc['description'],
# #                     "created_at": doc['created_at'],
# #                     "_id": doc['_id']
# #                 })
# #             except PIL.UnidentifiedImageError as e:
# #                 st.error(f"❌ Invalid image data for image ID: {doc['_id']}. Error: {str(e)}")
# #             except Exception as e:
# #                 st.error(f"❌ Error processing image with ID: {doc['_id']}. Error: {str(e)}")
# #         return images
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         collection.delete_many({})
# #         fs.drop()  # Remove all images from GridFS
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     try:
# #                         img = Image.open(io.BytesIO(doc["image_data"]))  # Read image from binary data
# #                         st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                     except PIL.UnidentifiedImageError as e:
# #                         st.error(f"❌ Error loading image ID: {doc['_id']}. Invalid image data.")
# #                     except Exception as e:
# #                         st.error(f"❌ Error processing image ID: {doc['_id']}. {str(e)}")
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()


# # import os
# # import uuid
# # import io
# # import shutil
# # from datetime import datetime
# # from dotenv import load_dotenv
# # import urllib.parse
# # from pymongo import MongoClient
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # import gridfs

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]

# # # --- GridFS setup ---
# # fs = gridfs.GridFS(db)

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # # --- Image storage setup ---
# # IMAGE_STORAGE = "stored_images"
# # os.makedirs(IMAGE_STORAGE, exist_ok=True)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}."
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     image_id = str(uuid.uuid4())
# #     try:
# #         # Save the image to GridFS as binary data
# #         with io.BytesIO() as img_io:
# #             img.save(img_io, format='JPEG')
# #             img_io.seek(0)
# #             file_id = fs.put(img_io, filename=f"{image_id}.jpg", content_type="image/jpeg")

# #         # Store metadata in MongoDB
# #         collection.insert_one({
# #             "_id": image_id,
# #             "description": description,
# #             "image_id": file_id,
# #             "created_at": datetime.now()
# #         })
# #         return image_id
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         images = []
# #         for doc in results:
# #             img_data = fs.get(doc['image_id']).read()  # Get the image from GridFS
# #             try:
# #                 img = Image.open(io.BytesIO(img_data))  # Read image from binary data
# #                 img.verify()  # Verify that the image is valid
# #                 images.append({
# #                     "image_data": img_data,
# #                     "description": doc['description'],
# #                     "created_at": doc['created_at'],
# #                     "_id": doc['_id']
# #                 })
# #             except PIL.UnidentifiedImageError as e:
# #                 st.error(f"❌ Invalid image data for image ID: {doc['_id']}. Error: {str(e)}")
# #             except Exception as e:
# #                 st.error(f"❌ Error processing image with ID: {doc['_id']}. Error: {str(e)}")
# #         return images
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         collection.delete_many({})
# #         fs.drop()  # Remove all images from GridFS
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     try:
# #                         img = Image.open(io.BytesIO(doc["image_data"]))  # Read image from binary data
# #                         st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                     except PIL.UnidentifiedImageError as e:
# #                         st.error(f"❌ Error loading image ID: {doc['_id']}. Invalid image data.")
# #                     except Exception as e:
# #                         st.error(f"❌ Error processing image ID: {doc['_id']}. {str(e)}")
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()


# # from dotenv import load_dotenv
# # import os
# # import urllib.parse
# # from pymongo import MongoClient
# # import gridfs  # Added for GridFS
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # from datetime import datetime
# # import uuid
# # import io  # Added for byte stream handling

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # collection = db["images"]
# # fs = gridfs.GridFS(db)  # Initialize GridFS

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}"
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     try:
# #         # Convert image to bytes
# #         img_byte_arr = io.BytesIO()
# #         img.save(img_byte_arr, format='JPEG')
# #         img_byte_arr.seek(0)
        
# #         # Store in GridFS
# #         file_id = fs.put(img_byte_arr.getvalue(), filename=f"{uuid.uuid4()}.jpg")
        
# #         # Store metadata in collection
# #         collection.insert_one({
# #             "_id": str(file_id),
# #             "description": description,
# #             "created_at": datetime.now()
# #         })
# #         return str(file_id)
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         return list(results)
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         # Delete all files from GridFS
# #         for doc in collection.find():
# #             fs.delete(doc["_id"])
# #         # Clear metadata collection
# #         collection.delete_many({})
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     try:
# #                         # Retrieve image from GridFS
# #                         grid_out = fs.get(doc["_id"])
# #                         img = Image.open(io.BytesIO(grid_out.read()))
# #                         st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                     except Exception as e:
# #                         st.error(f"Error loading image: {str(e)}")
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()


# # from dotenv import load_dotenv
# # import os
# # import urllib.parse
# # from pymongo import MongoClient
# # import gridfs
# # from bson.objectid import ObjectId
# # from PIL import Image
# # import streamlit as st
# # import google.generativeai as genai
# # from datetime import datetime
# # import uuid
# # import io

# # # --- Load environment variables ---
# # load_dotenv()
# # GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# # MONGO_USER = os.getenv("MONGO_USER")
# # MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # # --- Validate keys ---
# # if not GOOGLE_API_KEY:
# #     st.error("❌ Google API key not found.")
# #     st.stop()

# # if not MONGO_USER or not MONGO_PASSWORD:
# #     st.error("❌ MongoDB credentials not found.")
# #     st.stop()

# # # --- Escape username and password ---
# # escaped_user = urllib.parse.quote_plus(MONGO_USER)
# # escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# # mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # client = MongoClient(mongo_uri)
# # db = client["visionflow"]
# # fs = gridfs.GridFS(db)
# # collection = db["images"]

# # # --- Gemini setup ---
# # genai.configure(api_key=GOOGLE_API_KEY)

# # @st.cache_resource
# # def load_model():
# #     return genai.GenerativeModel("gemini-1.5-flash")

# # # --- Constants ---
# # PROMPT = """Analyze the image and respond STRICTLY in this format:
# # People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# # - Use natural language without brackets
# # - Keep responses brief but descriptive
# # - Include articles (a/an) for locations"""

# # # --- Utils ---
# # def clean_text(text: str) -> str:
# #     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# # def process_response(response: str) -> str:
# #     try:
# #         people = "NONE"
# #         place = "unknown location"
# #         activity = "NONE"
# #         parts = [p.strip() for p in response.split("|")]
# #         for part in parts:
# #             if ":" in part:
# #                 key, val = part.split(":", 1)
# #                 key = key.strip().lower()
# #                 val = clean_text(val.strip())
# #                 if key == "people":
# #                     people = val
# #                 elif key == "place":
# #                     place = val
# #                 elif key == "activity":
# #                     activity = val

# #         people_text = "No people" if people.lower() == "none" else people
# #         summary = f"{people_text} in {place}"
# #         if activity.lower() != "none":
# #             summary += f" {activity.rstrip('.')}"
# #         return summary
# #     except Exception as e:
# #         st.error(f"Response processing error: {str(e)}")
# #         return response

# # def store_image(img: Image.Image, description: str) -> str:
# #     try:
# #         img_byte_arr = io.BytesIO()
# #         img.save(img_byte_arr, format='JPEG')
# #         img_byte_arr.seek(0)
        
# #         # Store in GridFS and get ObjectId
# #         file_id = fs.put(img_byte_arr.getvalue(), filename=f"{uuid.uuid4()}.jpg")
        
# #         # Store metadata with native ObjectId
# #         collection.insert_one({
# #             "_id": file_id,
# #             "description": description,
# #             "created_at": datetime.now()
# #         })
# #         return str(file_id)
# #     except Exception as e:
# #         st.error(f"❌ Storage error: {str(e)}")
# #         return ""

# # def search_images(query: str):
# #     try:
# #         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
# #         return list(results)
# #     except Exception as e:
# #         st.error(f"❌ Search error: {str(e)}")
# #         return []

# # def get_image_count() -> int:
# #     try:
# #         return collection.count_documents({})
# #     except Exception as e:
# #         st.error(f"❌ Count error: {str(e)}")
# #         return 0

# # def clear_database():
# #     try:
# #         # Delete all GridFS files first
# #         for doc in collection.find():
# #             try:
# #                 fs.delete(doc["_id"])
# #             except Exception as e:
# #                 st.error(f"Error deleting file {doc['_id']}: {str(e)}")
        
# #         # Clear metadata collection
# #         collection.delete_many({})
# #         st.success("✅ All images and metadata cleared.")
# #     except Exception as e:
# #         st.error(f"❌ Clear error: {str(e)}")

# # # --- Streamlit UI ---
# # st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# # st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# # st.markdown(f"### Total images stored: **{get_image_count()}**")

# # def image_capture_section():
# #     st.header("📸 Capture & Store Images")
# #     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
# #     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

# #     if img_file:
# #         try:
# #             img = Image.open(img_file).convert("RGB")
# #             st.image(img, caption="Captured Image", use_column_width=True)
# #             with st.spinner("🔍 Analyzing image..."):
# #                 model = load_model()
# #                 response = model.generate_content([PROMPT, img])
# #                 summary = process_response(response.text)
# #                 image_id = store_image(img, summary)
# #                 if image_id:
# #                     st.success(f"✅ Image stored with ID: `{image_id}`")
# #         except Exception as e:
# #             st.error(f"❌ Processing error: {str(e)}")

# # def image_search_section():
# #     st.header("🔍 Search Images")
# #     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
# #     if query:
# #         results = search_images(query)
# #         if results:
# #             st.subheader(f"🖼️ Found {len(results)} results")
# #             for doc in results:
# #                 col1, col2 = st.columns([1, 2])
# #                 with col1:
# #                     try:
# #                         # Retrieve image from GridFS using ObjectId
# #                         grid_out = fs.get(doc["_id"])
# #                         img = Image.open(io.BytesIO(grid_out.read()))
# #                         st.image(img, caption=f"ID: {doc['_id']}", width=150)
# #                     except Exception as e:
# #                         st.error(f"Error loading image: {str(e)}")
# #                 with col2:
# #                     st.markdown(f"**Description:** {doc['description']}")
# #                     st.markdown(f"**Uploaded on:** {doc['created_at']}")
# #                 st.markdown("---")
# #         else:
# #             st.info("No results. Try a different query.")

# # def database_management_section():
# #     st.header("🗃️ Manage Database")
# #     if st.button("🚨 Clear All Images"):
# #         clear_database()

# # # --- Run ---
# # image_capture_section()
# # image_search_section()
# # database_management_section()








# from dotenv import load_dotenv
# import os
# import urllib.parse
# from pymongo import MongoClient
# import gridfs
# from bson.objectid import ObjectId
# from PIL import Image
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import io

# # --- Load environment variables ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # --- Validate keys ---
# if not GOOGLE_API_KEY:
#     st.error("❌ Google API key not found.")
#     st.stop()

# if not MONGO_USER or not MONGO_PASSWORD:
#     st.error("❌ MongoDB credentials not found.")
#     st.stop()

# # --- Escape username and password ---
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # --- MongoDB Connection ---
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# fs = gridfs.GridFS(db)
# collection = db["images"]

# # --- Gemini setup ---
# genai.configure(api_key=GOOGLE_API_KEY)

# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel("gemini-1.5-flash")

# # --- Constants ---
# PROMPT = """Analyze the image and respond STRICTLY in this format:
# People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# - Use natural language without brackets
# - Keep responses brief but descriptive
# - Include articles (a/an) for locations"""

# # --- Utils ---
# def clean_text(text: str) -> str:
#     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# def process_response(response: str) -> str:
#     try:
#         people = "NONE"
#         place = "unknown location"
#         activity = "NONE"
#         parts = [p.strip() for p in response.split("|")]
#         for part in parts:
#             if ":" in part:
#                 key, val = part.split(":", 1)
#                 key = key.strip().lower()
#                 val = clean_text(val.strip())
#                 if key == "people":
#                     people = val
#                 elif key == "place":
#                     place = val
#                 elif key == "activity":
#                     activity = val

#         people_text = "No people" if people.lower() == "none" else people
#         summary = f"{people_text} in {place}"
#         if activity.lower() != "none":
#             summary += f" {activity.rstrip('.')}"
#         return summary
#     except Exception as e:
#         st.error(f"Response processing error: {str(e)}")
#         return response

# def store_image(img: Image.Image, description: str) -> str:
#     try:
#         img_byte_arr = io.BytesIO()
#         img.save(img_byte_arr, format='JPEG')
#         img_byte_arr.seek(0)
        
#         # Store in GridFS and get ObjectId
#         file_id = fs.put(img_byte_arr.getvalue(), filename=f"image_{datetime.now().timestamp()}.jpg")
        
#         # Store metadata with native ObjectId
#         collection.insert_one({
#             "_id": file_id,  # Store as ObjectId
#             "description": description,
#             "created_at": datetime.now()
#         })
#         return str(file_id)
#     except Exception as e:
#         st.error(f"❌ Storage error: {str(e)}")
#         return ""

# def search_images(query: str):
#     try:
#         results = collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1)
#         return list(results)
#     except Exception as e:
#         st.error(f"❌ Search error: {str(e)}")
#         return []

# def get_image_count() -> int:
#     try:
#         return collection.count_documents({})
#     except Exception as e:
#         st.error(f"❌ Count error: {str(e)}")
#         return 0

# def clear_database():
#     try:
#         # Delete all GridFS files
#         for file in fs.find():
#             try:
#                 fs.delete(file._id)
#             except Exception as e:
#                 st.error(f"Error deleting {file._id}: {str(e)}")
        
#         # Clear metadata collection
#         collection.delete_many({})
#         st.success("✅ All images and metadata cleared.")
#     except Exception as e:
#         st.error(f"❌ Clear error: {str(e)}")

# # --- Streamlit UI ---
# st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# st.title("👁️ VisionFlow - MongoDB Powered Image AI")

# st.markdown(f"### Total images stored: **{get_image_count()}**")

# def image_capture_section():
#     st.header("📸 Capture & Store Images")
#     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
#     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

#     if img_file:
#         try:
#             img = Image.open(img_file).convert("RGB")
#             st.image(img, caption="Captured Image", use_column_width=True)
#             with st.spinner("🔍 Analyzing image..."):
#                 model = load_model()
#                 response = model.generate_content([PROMPT, img])
#                 summary = process_response(response.text)
#                 image_id = store_image(img, summary)
#                 if image_id:
#                     st.success(f"✅ Image stored with ID: `{image_id}`")
#                     st.experimental_rerun()
#         except Exception as e:
#             st.error(f"❌ Processing error: {str(e)}")

# def image_search_section():
#     st.header("🔍 Search Images")
#     query = st.text_input("Enter a description:", placeholder="e.g., a cat in the park")
#     if query:
#         results = search_images(query)
#         if results:
#             st.subheader(f"🖼️ Found {len(results)} results")
#             for doc in results:
#                 col1, col2 = st.columns([1, 2])
#                 with col1:
#                     try:
#                         # Handle ID conversion
#                         file_id = doc["_id"]
#                         if isinstance(file_id, str):
#                             try:
#                                 file_id = ObjectId(file_id)
#                             except:
#                                 st.error("Invalid ID format")
#                                 continue
                        
#                         grid_out = fs.get(file_id)
#                         img = Image.open(io.BytesIO(grid_out.read()))
#                         st.image(img, caption=f"ID: {file_id}", width=150)
#                     except gridfs.NoFile:
#                         st.error("⚠️ Image file missing in database")
#                     except Exception as e:
#                         st.error(f"Error loading image: {str(e)}")
#                 with col2:
#                     st.markdown(f"**Description:** {doc['description']}")
#                     st.markdown(f"**Uploaded on:** {doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
#                 st.markdown("---")
#         else:
#             st.info("No results. Try a different query.")

# def database_management_section():
#     st.header("🗃️ Manage Database")
#     if st.button("🚨 Clear All Images"):
#         clear_database()
#         st.experimental_rerun()

# # --- Run ---
# image_capture_section()
# image_search_section()
# database_management_section()







# from dotenv import load_dotenv
# import os
# import urllib.parse
# from pymongo import MongoClient
# import gridfs
# from bson.objectid import ObjectId
# from PIL import Image
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import io

# # --- Load environment variables ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # --- Validate keys ---
# if not GOOGLE_API_KEY:
#     st.error("❌ Google API key not found.")
#     st.stop()

# if not MONGO_USER or not MONGO_PASSWORD:
#     st.error("❌ MongoDB credentials not found.")
#     st.stop()

# # --- Escape username and password ---
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # --- MongoDB Connection ---
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# fs = gridfs.GridFS(db)
# collection = db["images"]

# # --- Gemini setup ---
# genai.configure(api_key=GOOGLE_API_KEY)

# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel("gemini-1.5-flash")

# # --- Constants ---
# PROMPT = """Analyze the image and respond STRICTLY in this format:
# People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# - Use natural language without brackets
# - Keep responses brief but descriptive
# - Include articles (a/an) for locations"""

# # --- Utils ---
# def clean_text(text: str) -> str:
#     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# def process_response(response: str) -> str:
#     try:
#         people = "NONE"
#         place = "unknown location"
#         activity = "NONE"
#         parts = [p.strip() for p in response.split("|")]
#         for part in parts:
#             if ":" in part:
#                 key, val = part.split(":", 1)
#                 key = key.strip().lower()
#                 val = clean_text(val.strip())
#                 if key == "people":
#                     people = val
#                 elif key == "place":
#                     place = val
#                 elif key == "activity":
#                     activity = val

#         people_text = "No people" if people.lower() == "none" else people
#         summary = f"{people_text} in {place}"
#         if activity.lower() != "none":
#             summary += f" {activity.rstrip('.')}"
#         return summary
#     except Exception as e:
#         st.error(f"Response processing error: {str(e)}")
#         return response

# def store_image(img: Image.Image, description: str) -> str:
#     try:
#         # Convert image to bytes
#         img_byte_arr = io.BytesIO()
#         img.save(img_byte_arr, format='JPEG')
#         img_byte_arr.seek(0)
        
#         # Store in GridFS
#         file_id = fs.put(img_byte_arr.getvalue(), filename=f"img_{datetime.now().timestamp()}.jpg")
        
#         # Store metadata
#         collection.insert_one({
#             "_id": file_id,
#             "description": description,
#             "created_at": datetime.now()
#         })
#         return str(file_id)
#     except Exception as e:
#         st.error(f"❌ Storage error: {str(e)}")
#         return ""

# def search_images(query: str):
#     try:
#         return list(collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1))
#     except Exception as e:
#         st.error(f"❌ Search error: {str(e)}")
#         return []

# def get_image_count() -> int:
#     try:
#         return collection.count_documents({})
#     except Exception as e:
#         st.error(f"❌ Count error: {str(e)}")
#         return 0

# def clear_database():
#     try:
#         # Delete all GridFS files
#         for file in fs.find():
#             fs.delete(file._id)
#         # Clear metadata
#         collection.delete_many({})
#         st.success("✅ All images and metadata cleared.")
#     except Exception as e:
#         st.error(f"❌ Clear error: {str(e)}")

# # --- Streamlit UI ---
# st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# st.title("👁️ VisionFlow - Pure MongoDB Image Storage")

# st.markdown(f"### Total images stored: **{get_image_count()}**")

# def image_capture_section():
#     st.header("📸 Capture & Store Images")
#     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
#     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

#     if img_file:
#         try:
#             img = Image.open(img_file).convert("RGB")
#             st.image(img, caption="Captured Image", use_column_width=True)
#             with st.spinner("🔍 Analyzing image..."):
#                 model = load_model()
#                 response = model.generate_content([PROMPT, img])
#                 summary = process_response(response.text)
#                 image_id = store_image(img, summary)
#                 if image_id:
#                     st.success(f"✅ Image stored with ID: `{image_id}`")
#                     st.rerun()
#         except Exception as e:
#             st.error(f"❌ Processing error: {str(e)}")

# def image_search_section():
#     st.header("🔍 Search Images")
#     query = st.text_input("Search descriptions:", placeholder="e.g., people in a park")
#     if query:
#         results = search_images(query)
#         if results:
#             st.subheader(f"🖼️ Found {len(results)} results")
#             for doc in results:
#                 col1, col2 = st.columns([1, 3])
#                 with col1:
#                     try:
#                         file_id = ObjectId(doc["_id"])
#                         grid_out = fs.get(file_id)
#                         img = Image.open(io.BytesIO(grid_out.read()))
#                         st.image(img, caption=f"ID: {doc['_id']}", width=200)
#                     except Exception as e:
#                         st.error(f"Error loading image: {str(e)}")
#                 with col2:
#                     st.markdown(f"**Description:** {doc['description']}")
#                     st.markdown(f"**Uploaded:** {doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
#                 st.divider()
#         else:
#             st.info("No images found matching your search")

# def database_management_section():
#     st.header("🗄️ Database Management")
#     if st.button("🚨 Clear All Data", type="primary"):
#         clear_database()
#         st.rerun()

# # --- Run Sections ---
# image_capture_section()
# image_search_section()
# database_management_section()











# from dotenv import load_dotenv
# import os
# import urllib.parse
# from pymongo import MongoClient
# import gridfs
# from bson.objectid import ObjectId
# from PIL import Image
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import io

# # --- Load environment variables ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # --- Validate keys ---
# if not GOOGLE_API_KEY:
#     st.error("❌ Google API key not found.")
#     st.stop()

# if not MONGO_USER or not MONGO_PASSWORD:
#     st.error("❌ MongoDB credentials not found.")
#     st.stop()

# # --- Escape username and password ---
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # --- MongoDB Connection ---
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# fs = gridfs.GridFS(db)
# collection = db["images"]

# # --- Gemini setup ---
# genai.configure(api_key=GOOGLE_API_KEY)

# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel("gemini-1.5-flash")

# # --- Constants ---
# PROMPT = """Analyze the image and respond STRICTLY in this format:
# People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# - Use natural language without brackets
# - Keep responses brief but descriptive
# - Include articles (a/an) for locations"""

# # --- Utils ---
# def clean_text(text: str) -> str:
#     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# def process_response(response: str) -> str:
#     try:
#         people = "NONE"
#         place = "unknown location"
#         activity = "NONE"
#         parts = [p.strip() for p in response.split("|")]
#         for part in parts:
#             if ":" in part:
#                 key, val = part.split(":", 1)
#                 key = key.strip().lower()
#                 val = clean_text(val.strip())
#                 if key == "people":
#                     people = val
#                 elif key == "place":
#                     place = val
#                 elif key == "activity":
#                     activity = val

#         people_text = "No people" if people.lower() == "none" else people
#         summary = f"{people_text} in {place}"
#         if activity.lower() != "none":
#             summary += f" {activity.rstrip('.')}"
#         return summary
#     except Exception as e:
#         st.error(f"Response processing error: {str(e)}")
#         return response

# def store_image(img: Image.Image, description: str) -> str:
#     try:
#         # Convert image to bytes
#         img_byte_arr = io.BytesIO()
#         img.save(img_byte_arr, format='JPEG')
#         img_byte_arr.seek(0)

#         # Store in GridFS
#         file_id = fs.put(img_byte_arr.getvalue(), filename=f"img_{datetime.now().timestamp()}.jpg")

#         # Store metadata
#         collection.insert_one({
#             "_id": file_id,
#             "description": description,
#             "created_at": datetime.now()
#         })
#         return str(file_id)
#     except Exception as e:
#         st.error(f"❌ Storage error: {str(e)}")
#         return ""

# def search_images(query: str):
#     try:
#         return list(collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1))
#     except Exception as e:
#         st.error(f"❌ Search error: {str(e)}")
#         return []

# def get_image_count() -> int:
#     try:
#         return collection.count_documents({})
#     except Exception as e:
#         st.error(f"❌ Count error: {str(e)}")
#         return 0

# def clear_database():
#     try:
#         for file in fs.find():
#             fs.delete(file._id)
#         collection.delete_many({})
#         st.success("✅ All images and metadata cleared.")
#     except Exception as e:
#         st.error(f"❌ Clear error: {str(e)}")

# # --- Streamlit UI ---
# st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# st.title("👁️ VisionFlow - Pure MongoDB Image Storage")

# st.markdown(f"### Total images stored: **{get_image_count()}**")

# def image_capture_section():
#     st.header("📸 Capture & Store Images")
#     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
#     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

#     if img_file:
#         try:
#             # Generate a hash key based on file bytes
#             file_key = f"uploaded_{hash(img_file.getvalue())}"
#             if file_key not in st.session_state:
#                 img = Image.open(img_file).convert("RGB")
#                 st.image(img, caption="Captured Image", use_column_width=True)
#                 with st.spinner("🔍 Analyzing image..."):
#                     model = load_model()
#                     response = model.generate_content([PROMPT, img])
#                     summary = process_response(response.text)
#                     image_id = store_image(img, summary)
#                     if image_id:
#                         st.success(f"✅ Image stored with ID: `{image_id}`")
#                         st.session_state[file_key] = True  # Prevent re-upload
#                         st.rerun()
#             else:
#                 st.info("⚠️ This image has already been processed in this session.")
#         except Exception as e:
#             st.error(f"❌ Processing error: {str(e)}")

# def image_search_section():
#     st.header("🔍 Search Images")
#     query = st.text_input("Search descriptions:", placeholder="e.g., people in a park")
#     if query:
#         results = search_images(query)
#         if results:
#             st.subheader(f"🖼️ Found {len(results)} results")
#             for doc in results:
#                 col1, col2 = st.columns([1, 3])
#                 with col1:
#                     try:
#                         file_id = ObjectId(doc["_id"])
#                         grid_out = fs.get(file_id)
#                         img = Image.open(io.BytesIO(grid_out.read()))
#                         st.image(img, caption=f"ID: {doc['_id']}", width=200)
#                     except Exception as e:
#                         st.error(f"Error loading image: {str(e)}")
#                 with col2:
#                     st.markdown(f"**Description:** {doc['description']}")
#                     st.markdown(f"**Uploaded:** {doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
#                 st.divider()
#         else:
#             st.info("No images found matching your search")

# def database_management_section():
#     st.header("🗄️ Database Management")
#     if st.button("🚨 Clear All Data", type="primary"):
#         clear_database()
#         st.rerun()

# # --- Run Sections ---
# image_capture_section()
# image_search_section()
# database_management_section()




# from dotenv import load_dotenv
# import os
# import urllib.parse
# from pymongo import MongoClient
# import gridfs
# from bson.objectid import ObjectId
# from PIL import Image
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import io
# import PyPDF2

# # --- Load environment variables ---
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # --- Validate keys ---
# if not GOOGLE_API_KEY:
#     st.error("❌ Google API key not found.")
#     st.stop()

# if not MONGO_USER or not MONGO_PASSWORD:
#     st.error("❌ MongoDB credentials not found.")
#     st.stop()

# # --- Escape username and password ---
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # --- MongoDB Connection ---
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# fs = gridfs.GridFS(db)
# collection = db["files"]

# # --- Gemini setup ---
# genai.configure(api_key=GOOGLE_API_KEY)

# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel("gemini-1.5-flash")

# # --- Constants ---
# IMAGE_PROMPT = """Analyze the image and respond STRICTLY in this format:
# People:[X person/people/NONE]|Place:[a/an + location description]|Activity:[description/NONE]
# - Use natural language without brackets
# - Keep responses brief but descriptive
# - Include articles (a/an) for locations"""

# DOCUMENT_PROMPT = """Summarize the content of the document below:
# {text}"""

# # --- Utils ---
# def clean_text(text: str) -> str:
#     return text.replace("*", "").replace("[", "").replace("]", "").strip()

# def process_image_response(response: str) -> str:
#     try:
#         people = "NONE"
#         place = "unknown location"
#         activity = "NONE"
#         parts = [p.strip() for p in response.split("|")]
#         for part in parts:
#             if ":" in part:
#                 key, val = part.split(":", 1)
#                 key = key.strip().lower()
#                 val = clean_text(val.strip())
#                 if key == "people":
#                     people = val
#                 elif key == "place":
#                     place = val
#                 elif key == "activity":
#                     activity = val

#         people_text = "No people" if people.lower() == "none" else people
#         summary = f"{people_text} in {place}"
#         if activity.lower() != "none":
#             summary += f" {activity.rstrip('.')}"

#         return summary
#     except Exception as e:
#         st.error(f"Error processing image response: {str(e)}")
#         return response

# def process_document_response(text: str) -> str:
#     try:
#         # Request a very short summary (1-2 lines)
#         prompt = f"Summarize the following document in 1 to 2 lines only:\n{text}"

#         response = genai.generate_content(prompt)
#         return clean_text(response.text)
#     except Exception as e:
#         st.error(f"Error processing document response: {str(e)}")
#         return text


# def store_file(file_data: bytes, file_type: str, description: str) -> str:
#     try:
#         # Store file in GridFS
#         file_id = fs.put(file_data, filename=f"{file_type}_{datetime.now().timestamp()}.pdf" if file_type == "document" else "image.jpg")

#         # Store metadata
#         collection.insert_one({
#             "_id": file_id,
#             "description": description,
#             "file_type": file_type,
#             "created_at": datetime.now()
#         })
#         return str(file_id)
#     except Exception as e:
#         st.error(f"❌ Storage error: {str(e)}")
#         return ""

# def search_files(query: str):
#     try:
#         return list(collection.find({"description": {"$regex": query, "$options": "i"}}).sort("created_at", -1))
#     except Exception as e:
#         st.error(f"❌ Search error: {str(e)}")
#         return []

# def get_file_count() -> int:
#     try:
#         return collection.count_documents({})
#     except Exception as e:
#         st.error(f"❌ Count error: {str(e)}")
#         return 0

# def clear_database():
#     try:
#         for file in fs.find():
#             fs.delete(file._id)
#         collection.delete_many({})
#         st.success("✅ All files and metadata cleared.")
#     except Exception as e:
#         st.error(f"❌ Clear error: {str(e)}")

# # --- Streamlit UI ---
# st.set_page_config(page_title="VisionFlow", page_icon="👁️")
# st.title("👁️ VisionFlow - Pure MongoDB Image & Document Storage")

# st.markdown(f"### Total files stored: **{get_file_count()}**")

# def image_capture_section():
#     st.header("📸 Capture & Store Images")
#     img_source = st.radio("Choose input:", ("📤 Upload", "📷 Camera"), horizontal=True)
#     img_file = st.file_uploader("Upload image") if img_source == "📤 Upload" else st.camera_input("Take a photo")

#     if img_file:
#         try:
#             # Generate a hash key based on file bytes
#             file_key = f"uploaded_{hash(img_file.getvalue())}"
#             if file_key not in st.session_state:
#                 img = Image.open(img_file).convert("RGB")
#                 st.image(img, caption="Captured Image", use_column_width=True)
#                 with st.spinner("🔍 Analyzing image..."):
#                     model = load_model()
#                     response = model.generate_content([IMAGE_PROMPT, img])
#                     summary = process_image_response(response.text)
#                     file_id = store_file(img_file.getvalue(), "image", summary)
#                     if file_id:
#                         st.success(f"✅ Image stored with ID: `{file_id}`")
#                         st.session_state[file_key] = True  # Prevent re-upload
#                         st.rerun()
#             else:
#                 st.info("⚠️ This image has already been processed in this session.")
#         except Exception as e:
#             st.error(f"❌ Processing error: {str(e)}")

# def document_upload_section():
#     st.header("📄 Upload & Analyze Documents")
#     doc_file = st.file_uploader("Upload a document", type=["pdf"])

#     if doc_file:
#         try:
#             # Read the PDF content
#             with io.BytesIO(doc_file.read()) as pdf_file:
#                 pdf_reader = PyPDF2.PdfReader(pdf_file)
#                 text = ""
#                 for page in pdf_reader.pages:
#                     text += page.extract_text()

#             # Summarize the document
#             with st.spinner("🔍 Analyzing document..."):
#                 summary = process_document_response(text)
#                 file_id = store_file(doc_file.getvalue(), "document", summary)
#                 if file_id:
#                     st.success(f"✅ Document stored with ID: `{file_id}`")
#                     st.markdown(f"**Summary:** {summary}")
#         except Exception as e:
#             st.error(f"❌ Document processing error: {str(e)}")

# def file_search_section():
#     st.header("🔍 Search Files")
#     query = st.text_input("Search descriptions:", placeholder="e.g., image of people or PDF about AI")
#     if query:
#         results = search_files(query)
#         if results:
#             st.subheader(f"🖼️ Found {len(results)} results")
#             for doc in results:
#                 col1, col2 = st.columns([1, 3])
#                 with col1:
#                     try:
#                         file_id = ObjectId(doc["_id"])
#                         grid_out = fs.get(file_id)
#                         file_data = grid_out.read()
#                         if doc["file_type"] == "image":
#                             img = Image.open(io.BytesIO(file_data))
#                             st.image(img, caption=f"ID: {doc['_id']}", width=200)
#                         elif doc["file_type"] == "document":
#                             st.download_button("Download Document", file_data, file_name=f"{doc['_id']}.pdf")
#                     except Exception as e:
#                         st.error(f"Error loading file: {str(e)}")
#                 with col2:
#                     st.markdown(f"**Description:** {doc['description']}")
#                     st.markdown(f"**Uploaded:** {doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
#                 st.divider()
#         else:
#             st.info("No files found matching your search")

# def database_management_section():
#     st.header("🗄️ Database Management")
#     if st.button("🚨 Clear All Data", type="primary"):
#         clear_database()
#         st.rerun()

# # --- Run Sections ---
# image_capture_section()
# document_upload_section()
# file_search_section()
# database_management_section()



















# import streamlit as st
# import tempfile
# import whisper
# import io
# from pymongo import MongoClient
# from bson.binary import Binary
# import google.generativeai as genai
# import os

# # ---------------------- CONFIGURATION ----------------------
# # MongoDB setup
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")


# # # --- Escape username and password ---
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # # --- MongoDB Connection ---
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)



# db = client["visionflow"]
# audio_collection = db["audio_files"]

# # Whisper model
# whisper_model = whisper.load_model("base")          

# # Gemini setup
# genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your Gemini API key
# gemini_model = genai.GenerativeModel("gemini-1.5-pro")  # Or any valid Gemini model
# # -----------------------------------------------------------

# # ---------------------- STREAMLIT UI -----------------------
# st.set_page_config(page_title="Voice Description - VisionFlow", page_icon="🎧")
# st.title("🎧 VisionFlow - Voice Description")

# st.markdown("Upload an `.mp3` file to generate a summary description and store it with the file in MongoDB.")

# # Upload audio file
# audio_file = st.file_uploader("📤 Upload Audio (.mp3)", type=["mp3"])

# if audio_file:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         tmp.write(audio_file.read())
#         tmp_path = tmp.name

#     st.audio(audio_file, format="audio/mp3")
#     st.info("🔁 Transcribing with Whisper...")

#     # Whisper transcription
#     try:
#         result = whisper_model.transcribe(tmp_path)
#         transcript = result["text"]
#         st.success("✅ Transcription complete")
#         st.subheader("📝 Transcription")
#         st.write(transcript)
#     except Exception as e:
#         st.error(f"Whisper transcription failed: {e}")
#         transcript = ""

#     # Gemini summarization
#     st.info("🧠 Summarizing with Gemini...")
#     try:
#         summary_response = gemini_model.generate_content(f"Summarize this transcription:\n\n{transcript}")
#         description = summary_response.text.strip()
#         st.success("✅ Summary generated")
#         st.subheader("📄 Description")
#         st.write(description)
#     except Exception as e:
#         st.error(f"Gemini summarization failed: {e}")
#         description = ""

#     # Save to MongoDB
#     audio_binary = Binary(open(tmp_path, "rb").read())
#     audio_doc = {
#         "filename": audio_file.name,
#         "file": audio_binary,
#         "description": description,
#         "transcript": transcript
#     }
#     audio_collection.insert_one(audio_doc)
#     st.success("📦 Audio and metadata saved to MongoDB!")

# # Search and retrieve audio
# st.header("🔍 Search Audio by Description")
# search_query = st.text_input("Enter part of the description to search:")

# if search_query:
#     result = audio_collection.find_one({
#         "description": {"$regex": search_query, "$options": "i"}
#     })

#     if result:
#         st.success("✅ Match found!")
#         st.markdown(f"**📝 Description:** {result['description']}")
#         st.markdown(f"**🗣️ Transcript:** {result['transcript']}")
#         st.audio(io.BytesIO(result["file"]), format="audio/mp3")

#         st.download_button(
#             label="⬇️ Download Audio",
#             data=io.BytesIO(result["file"]),
#             file_name=result["filename"],
#             mime="audio/mpeg"
#         )
#     else:
#         st.warning("No matching description found.")






# import streamlit as st
# import tempfile
# import whisper
# import io
# import os
# import urllib.parse
# from pymongo import MongoClient
# from bson.binary import Binary
# from groq import Groq
# from dotenv import load_dotenv

# # ---------------------- CONFIG ----------------------
# load_dotenv()

# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# audio_collection = db["audio_files"]

# # Whisper model
# whisper_model = whisper.load_model("base")

# # Groq client
# groq_client = Groq(api_key=GROQ_API_KEY)

# # ---------------------- UI ----------------------
# st.set_page_config(page_title="Voice Description - VisionFlow", page_icon="🎧")
# st.title("🎧 VisionFlow - Voice Description")

# st.markdown("Upload an `.mp3` file to generate a **summary description** and store it with the file in **MongoDB**.")

# # Upload audio
# audio_file = st.file_uploader("📤 Upload Audio (.mp3)", type=["mp3"])

# if audio_file:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         tmp.write(audio_file.read())
#         tmp_path = tmp.name

#     st.audio(audio_file, format="audio/mp3")
#     st.info("🔁 Transcribing with Whisper...")

#     # Whisper transcription
#     try:
#         result = whisper_model.transcribe(tmp_path)
#         transcript = result["text"]
#         st.success("✅ Transcription complete")
#         st.subheader("📝 Transcription")
#         st.write(transcript)
#     except Exception as e:
#         st.error(f"Whisper transcription failed: {e}")
#         transcript = ""

#     # Groq summarization
#     st.info("🧠 Summarizing with Groq...")
#     try:
#         completion = groq_client.chat.completions.create(
#             model="mixtral-8x7b-32768",  # You can use llama3-8b-8192 or gemma-7b-it
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that summarizes voice transcripts."},
#                 {"role": "user", "content": f"Summarize the following audio transcript:\n\n{transcript}"}
#             ]
#         )
#         description = completion.choices[0].message.content.strip()
#         st.success("✅ Summary generated")
#         st.subheader("📄 Description")
#         st.write(description)
#     except Exception as e:
#         st.error(f"Groq summarization failed: {e}")
#         description = ""

#     # Save to MongoDB
#     audio_binary = Binary(open(tmp_path, "rb").read())
#     audio_doc = {
#         "filename": audio_file.name,
#         "file": audio_binary,
#         "description": description,
#         "transcript": transcript
#     }
#     audio_collection.insert_one(audio_doc)
#     st.success("📦 Audio and metadata saved to MongoDB!")

# # Search audio
# st.header("🔍 Search Audio by Description")
# search_query = st.text_input("Enter part of the description to search:")

# if search_query:
#     result = audio_collection.find_one({
#         "description": {"$regex": search_query, "$options": "i"}
#     })

#     if result:
#         st.success("✅ Match found!")
#         st.markdown(f"**📝 Description:** {result['description']}")
#         st.markdown(f"**🗣️ Transcript:** {result['transcript']}")
#         st.audio(io.BytesIO(result["file"]), format="audio/mp3")

#         st.download_button(
#             label="⬇️ Download Audio",
#             data=io.BytesIO(result["file"]),
#             file_name=result["filename"],
#             mime="audio/mpeg"
#         )
#     else:
#         st.warning("No matching description found.")












# import streamlit as st
# import tempfile
# import whisper
# import io
# import os
# import urllib.parse
# from pymongo import MongoClient
# from bson.binary import Binary
# from groq import Groq
# from dotenv import load_dotenv

# # ---------------------- CONFIG ----------------------
# load_dotenv()

# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# audio_collection = db["audio_files"]

# # Whisper model
# whisper_model = whisper.load_model("base")

# # Groq client
# groq_client = Groq(api_key=GROQ_API_KEY)

# # ---------------------- UI ----------------------
# st.set_page_config(page_title="Voice Description - VisionFlow", page_icon="🎧")
# st.title("🎧 VisionFlow - Voice Description")

# st.markdown("Upload an `.mp3` file to generate a **summary description** and store it with the file in **MongoDB**.")

# # Upload audio
# audio_file = st.file_uploader("📤 Upload Audio (.mp3)", type=["mp3"])

# if audio_file:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         tmp.write(audio_file.read())
#         tmp_path = tmp.name

#     st.audio(audio_file, format="audio/mp3")
#     st.info("🔁 Transcribing with Whisper...")

#     # Whisper transcription
#     try:
#         result = whisper_model.transcribe(tmp_path)
#         transcript = result["text"]
#         st.success("✅ Transcription complete")
#         st.subheader("📝 Transcription")
#         st.write(transcript)
#     except Exception as e:
#         st.error(f"Whisper transcription failed: {e}")
#         transcript = ""

#     # Groq summarization
#     st.info("🧠 Summarizing with Groq...")
#     try:
#         completion = groq_client.chat.completions.create(
#             model="mixtral-8x7b-32768",  # You can use llama3-8b-8192 or gemma-7b-it
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that summarizes voice transcripts."},
#                 {"role": "user", "content": f"Summarize the following audio transcript:\n\n{transcript}"}
#             ]
#         )
#         description = completion.choices[0].message.content.strip()
#         st.success("✅ Summary generated")
#         st.subheader("📄 Description")
#         st.write(description)
#     except Exception as e:
#         st.error(f"Groq summarization failed: {e}")
#         description = ""

#     # Save to MongoDB
#     audio_binary = Binary(open(tmp_path, "rb").read())
#     audio_doc = {
#         "filename": audio_file.name,
#         "file": audio_binary,
#         "description": description,
#         "transcript": transcript
#     }
#     audio_collection.insert_one(audio_doc)
#     st.success("📦 Audio and metadata saved to MongoDB!")

# # Search audio
# st.header("🔍 Search Audio by Description")
# search_query = st.text_input("Enter part of the description to search:")

# if search_query:
#     result = audio_collection.find_one({
#         "description": {"$regex": search_query, "$options": "i"}
#     })

#     if result:
#         st.success("✅ Match found!")
#         st.markdown(f"**📝 Description:** {result['description']}")
#         st.markdown(f"**🗣️ Transcript:** {result['transcript']}")
#         st.audio(io.BytesIO(result["file"]), format="audio/mp3")

#         st.download_button(
#             label="⬇️ Download Audio",
#             data=io.BytesIO(result["file"]),
#             file_name=result["filename"],
#             mime="audio/mpeg"
#         )
#     else:
#         st.warning("No matching description found.")






# import streamlit as st
# import tempfile
# import whisper
# import io
# import os
# import urllib.parse
# from pymongo import MongoClient
# from bson.binary import Binary
# from groq import Groq
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # ---------------------- CONFIGURATION ----------------------
# # MongoDB credentials
# MONGO_USER = os.getenv("MONGO_USER")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# # Escape special characters
# escaped_user = urllib.parse.quote_plus(MONGO_USER)
# escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# # MongoDB Connection
# mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(mongo_uri)
# db = client["visionflow"]
# audio_collection = db["audio_files"]

# # Whisper model (loads once)
# whisper_model = whisper.load_model("base")

# # Groq setup
# groq_api_key = os.getenv("GROQ_API_KEY")
# groq_client = Groq(api_key=groq_api_key)

# # ---------------------- STREAMLIT UI -----------------------
# st.set_page_config(page_title="Voice Description - VisionFlow", page_icon="🎧")
# st.title("🎧 VisionFlow - Voice Description")

# st.markdown("Upload an `.mp3` file to generate a summary description and store it with the file in MongoDB.")

# # Upload audio file
# audio_file = st.file_uploader("📤 Upload Audio (.mp3)", type=["mp3"])

# if audio_file:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         tmp.write(audio_file.read())
#         tmp_path = tmp.name

#     try:
#         st.audio(audio_file, format="audio/mp3")
#         st.info("🔁 Transcribing with Whisper...")

#         # Whisper Transcription
#         try:
#             result = whisper_model.transcribe(tmp_path)
#             transcript = result["text"]
#             st.success("✅ Transcription complete")
#             st.subheader("📝 Transcription")
#             st.write(transcript)
#         except Exception as e:
#             st.error(f"Whisper transcription failed: {e}")
#             transcript = ""

#         # Groq Summarization
#         if transcript:
#             st.info("🧠 Summarizing with Groq (LLaMA 3)...")
#             try:
#                 completion = groq_client.chat.completions.create(
#                     model="llama3-70b-8192",
#                     messages=[
#                         {"role": "system", "content": "You are a helpful assistant that summarizes voice transcripts."},
#                         {"role": "user", "content": f"Summarize the following audio transcript:\n\n{transcript}"}
#                     ]
#                 )
#                 description = completion.choices[0].message.content.strip()
#                 st.success("✅ Summary generated")
#                 st.subheader("📄 Description")
#                 st.write(description)
#             except Exception as e:
#                 st.error(f"Groq summarization failed: {e}")
#                 description = ""
#         else:
#             description = ""

#         # Save to MongoDB
#         try:
#             audio_binary = Binary(open(tmp_path, "rb").read())
#             audio_doc = {
#                 "filename": audio_file.name,
#                 "file": audio_binary,
#                 "description": description,
#                 "transcript": transcript
#             }
#             audio_collection.insert_one(audio_doc)
#             st.success("📦 Audio and metadata saved to MongoDB!")
#         except Exception as e:
#             st.error(f"MongoDB save failed: {e}")

#     finally:
#         # Clean up the temporary file
#         os.remove(tmp_path)

# # Search and retrieve audio
# st.header("🔍 Search Audio by Description")
# search_query = st.text_input("Enter part of the description to search:")

# if search_query:
#     result = audio_collection.find_one({
#         "description": {"$regex": search_query, "$options": "i"}
#     })

#     if result:
#         st.success("✅ Match found!")
#         st.markdown(f"**📝 Description:** {result['description']}")
#         st.markdown(f"**🗣️ Transcript:** {result['transcript']}")
#         st.audio(io.BytesIO(result["file"]), format="audio/mp3")

#         st.download_button(
#             label="⬇️ Download Audio",
#             data=io.BytesIO(result["file"]),
#             file_name=result["filename"],
#             mime="audio/mpeg"
#         )
#     else:
#         st.warning("No matching description found.")





# import os
# import streamlit as st
# from pymongo import MongoClient
# import gridfs
# from datetime import datetime
# from PIL import Image
# import fitz  # PyMuPDF
# import docx2txt
# from google.cloud import speech
# from agno.agent import Agent
# from agno.models.groq import Groq

# # 🌐 Set environment variables
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Speech_To_Text.json"
# os.environ["GROQ_API_KEY"] = "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"  # Replace with actual key

# # 💬 Groq LLM
# llm_agent = Agent(model=Groq(id="gemma2-9b-it"), markdown=False)

# # 🔊 Google Speech Client
# speech_client = speech.SpeechClient()

# # 🗃️ MongoDB Setup
# MONGO_URI = "mongodb://localhost:27017"
# mongo_client = MongoClient(MONGO_URI)
# db = mongo_client["visionflow"]
# fs = gridfs.GridFS(db)

# collections = {
#     "image": db["images"],
#     "document": db["documents"],
#     "audio": db["audios"]
# }

# # 💡 Helpers
# def summarize_text(text, task="Summarize"):
#     try:
#         prompt = f"{task} this content in a single line:\n\n{text}"
#         response = llm_agent.run(prompt)
#         return response.content.strip()
#     except Exception as e:
#         return f"❌ LLM error: {str(e)}"

# def transcribe_audio(file_data, file_name):
#     audio_content = file_data.read()
#     encoding_map = {
#         ".mp3": speech.RecognitionConfig.AudioEncoding.MP3,
#         ".flac": speech.RecognitionConfig.AudioEncoding.FLAC,
#         ".wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
#     }
#     extension = os.path.splitext(file_name)[1].lower()
#     encoding = encoding_map.get(extension)
#     if not encoding:
#         return "❌ Unsupported audio format."

#     audio = speech.RecognitionAudio(content=audio_content)
#     config = speech.RecognitionConfig(
#         encoding=encoding,
#         sample_rate_hertz=24000,
#         language_code="en-US"
#     )

#     try:
#         response = speech_client.recognize(config=config, audio=audio)
#         transcript = " ".join([r.alternatives[0].transcript for r in response.results])
#         return transcript or "⚠️ No speech detected."
#     except Exception as e:
#         return f"❌ Transcription error: {str(e)}"

# def save_to_mongodb(category, file, description):
#     file_id = fs.put(file.read(), filename=file.name, content_type=file.type)
#     metadata = {
#         "description": description,
#         "filename": file.name,
#         "filetype": file.type,
#         "upload_time": datetime.now(),
#         "file_id": file_id
#     }
#     collections[category].insert_one(metadata)

# def search_file_by_description(category, query):
#     result = collections[category].find_one({"description": {"$regex": query, "$options": "i"}})
#     if result:
#         file_data = fs.get(result["file_id"]).read()
#         return result["filename"], file_data, result["filetype"]
#     return None, None, None

# # 🌐 UI
# st.set_page_config(page_title="🧠 VisionFlow", layout="centered")
# st.title("🧠 VisionFlow: Smart File Description & Search")

# tabs = st.tabs(["📸 Images", "📄 Documents", "🎧 Audio"])

# # ------------------ IMAGES ------------------
# with tabs[0]:
#     st.subheader("📸 Upload Image")
#     img_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
#     if img_file and st.button("📝 Describe Image"):
#         img = Image.open(img_file)
#         st.image(img, caption=img_file.name, use_column_width=True)
#         description = summarize_text("Describe this image briefly.")
#         img_file.seek(0)
#         save_to_mongodb("image", img_file, description)
#         st.success("✅ Description saved to MongoDB!")
#         st.write(f"📌 Description: {description}")

#     st.divider()
#     st.subheader("🔍 Search Images")
#     query = st.text_input("Enter image description")
#     if st.button("🔎 Search Image"):
#         name, data, _ = search_file_by_description("image", query)
#         if name:
#             st.image(data, caption=name)
#         else:
#             st.error("No matching image found.")

# # ------------------ DOCUMENTS ------------------
# with tabs[1]:
#     st.subheader("📄 Upload Document")
#     doc_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
#     if doc_file and st.button("🧠 Summarize Document"):
#         text = ""
#         ext = os.path.splitext(doc_file.name)[1].lower()
#         if ext == ".pdf":
#             with fitz.open(stream=doc_file.read(), filetype="pdf") as doc:
#                 text = "".join([page.get_text() for page in doc])
#         elif ext == ".docx":
#             text = docx2txt.process(doc_file)
#         elif ext == ".txt":
#             text = doc_file.read().decode("utf-8")

#         if not text.strip():
#             st.warning("No content found in document.")
#         else:
#             summary = summarize_text(text)
#             doc_file.seek(0)
#             save_to_mongodb("document", doc_file, summary)
#             st.success("✅ Document saved with summary!")
#             st.write(f"📌 Summary: {summary}")

#     st.divider()
#     st.subheader("🔍 Search Documents")
#     query = st.text_input("Enter document description")
#     if st.button("🔎 Search Document"):
#         name, data, ftype = search_file_by_description("document", query)
#         if name:
#             st.download_button("📄 Download Document", data, file_name=name, mime=ftype)
#         else:
#             st.error("No matching document found.")

# # ------------------ AUDIO ------------------
# with tabs[2]:
#     st.subheader("🎧 Upload Audio")
#     audio_file = st.file_uploader("Upload audio", type=["mp3", "wav", "flac"])
#     if audio_file and st.button("🔊 Transcribe & Summarize"):
#         transcript = transcribe_audio(audio_file, audio_file.name)
#         if transcript.startswith("❌"):
#             st.error(transcript)
#         else:
#             st.success("✅ Transcription done!")
#             st.write(transcript)
#             with st.spinner("🧠 Summarizing..."):
#                 summary = summarize_text(transcript)
#             st.write(f"📌 Summary: {summary}")
#             audio_file.seek(0)
#             save_to_mongodb("audio", audio_file, summary)
#             st.success("🎧 Audio file saved!")

#     st.divider()
#     st.subheader("🔍 Search Audio")
#     query = st.text_input("Enter audio description")
#     if st.button("🔎 Search Audio"):
#         name, data, ftype = search_file_by_description("audio", query)
#         if name:
#             st.audio(data, format="audio/mp3" if name.endswith(".mp3") else "audio/wav")
#         else:
#             st.error("No audio found.")





import os
import urllib.parse
import streamlit as st
from google.cloud import speech
from agno.agent import Agent
from agno.models.groq import Groq
from pymongo import MongoClient
import gridfs
from datetime import datetime

# 🔐 Google & Groq credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Speech_To_Text.json"
os.environ["GROQ_API_KEY"] = "your_groq_api_key"  # Replace with your real key

# ✅ Load and escape MongoDB credentials
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

escaped_user = urllib.parse.quote_plus(MONGO_USER)
escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# 📦 MongoDB Atlas connection
mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["visionflow"]
fs = gridfs.GridFS(db)
audio_collection = db["audio_files"]

# 🎙️ Google Speech Client & LLM
speech_client = speech.SpeechClient()
llm_agent = Agent(model=Groq(id="gemma2-9b-it"), markdown=False)

# 🎧 Transcription
def transcribe_audio(file_data, file_name):
    audio_content = file_data.read()

    if file_name.endswith(".mp3"):
        encoding = speech.RecognitionConfig.AudioEncoding.MP3
    elif file_name.endswith(".flac"):
        encoding = speech.RecognitionConfig.AudioEncoding.FLAC
    elif file_name.endswith(".wav"):
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
    else:
        return "❌ Unsupported file format."

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=24000,
        language_code="en-US"
    )

    try:
        response = speech_client.recognize(config=config, audio=audio)
        results = response.results
        if not results:
            return "⚠️ No speech detected."
        transcript = " ".join([r.alternatives[0].transcript for r in results])
        return transcript
    except Exception as e:
        return f"❌ Transcription error: {str(e)}"

# 🧠 Summarize transcript
def summarize_transcript(text):
    try:
        prompt = f"Summarize this audio transcript in a single line:\n\n{text}"
        response = llm_agent.run(prompt)
        return response.content.strip()
    except Exception as e:
        return f"❌ LLM error: {str(e)}"

# 💾 Save audio to MongoDB
def save_audio_to_mongodb(file, summary):
    file_id = fs.put(file.read(), filename=file.name, content_type=file.type)
    metadata = {
        "description": summary,
        "filename": file.name,
        "filetype": file.type,
        "upload_time": datetime.now(),
        "file_id": file_id
    }
    audio_collection.insert_one(metadata)

# 🔍 Search MongoDB by description
def search_audio_by_description(query):
    result = audio_collection.find_one({"description": {"$regex": query, "$options": "i"}})
    if result:
        file_data = fs.get(result["file_id"]).read()
        return result["filename"], file_data
    return None, None

# 🌐 Streamlit App UI
st.set_page_config(page_title="🎧 Voice Description", layout="centered")
st.title("🎤 Upload Audio → Get Summary → Store & Search")

# 🎵 Upload section
audio_file = st.file_uploader("Upload audio (.mp3, .wav, .flac)", type=["mp3", "wav", "flac"])

if audio_file and st.button("📝 Transcribe & Summarize & Save"):
    st.info(f"File: {audio_file.name} | Type: {audio_file.type}")
    with st.spinner("🔊 Transcribing..."):
        transcript = transcribe_audio(audio_file, audio_file.name)
    if transcript.startswith("❌") or transcript.startswith("⚠️"):
        st.error(transcript)
    else:
        st.success("✅ Transcription complete!")
        st.write(transcript)

        with st.spinner("🧠 Summarizing..."):
            summary = summarize_transcript(transcript)
        st.subheader("📌 Summary")
        st.write(summary)

        audio_file.seek(0)  # reset pointer
        save_audio_to_mongodb(audio_file, summary)
        st.success("✅ Saved to MongoDB!")

# 🔍 Search by description
st.divider()
st.subheader("🔍 Search Audio by Description")
search_query = st.text_input("Enter description keywords:")

if st.button("🔎 Search"):
    if not search_query.strip():
        st.warning("Please enter a search term.")
    else:
        with st.spinner("Searching MongoDB..."):
            filename, file_data = search_audio_by_description(search_query)
            if filename:
                st.success(f"🎧 Found file: {filename}")
                st.audio(file_data, format="audio/mp3" if filename.endswith(".mp3") else "audio/wav")
            else:
                st.error("❌ No matching audio found.")
