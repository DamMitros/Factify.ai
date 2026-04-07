from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from bson import ObjectId
from datetime import datetime
from keycloak_client import require_auth, role_required
from common.python import db
from config import DB_NAME, COL_ANALYSIS_AI_TEXT, COL_ANALYSIS_AI_IMAGE, COL_POSTS,COL_COMMENTS

social_bp = Blueprint("social", __name__)

def serialize_doc(doc):
  doc["_id"] = str(doc["_id"])
  return doc

@social_bp.route("/feed", methods=["POST"])
@require_auth
def share_prediction():
  data = request.get_json()
  content = data.get("content")
  analysis_id = data.get("analysis_id")
  analysis_type = data.get("analysis_type", "text")

  if not content and not analysis_id:
    raise BadRequest("Post must contain content or analysis reference.")

  post = {
    "user_id": g.user.get("sub"),
    "username": g.user.get("preferred_username", "Unknown"),
    "content": content,
    "analysis_id": analysis_id,
    "analysis_type": analysis_type,
    "likes": [],
    "comments_count": 0,
    "created_at": datetime.utcnow()
  }

  result = db.get_database(DB_NAME)[COL_POSTS].insert_one(post)
  
  return jsonify({
    "success": True,
    "postId": str(result.inserted_id)
  })

@social_bp.route("/feed", methods=["GET"])
def get_feed():
  posts_cursor = db.get_database(DB_NAME)[COL_POSTS].find().sort("created_at", -1).limit(50)
  posts = []
  
  db_instance = db.get_database(DB_NAME)
  
  for doc in posts_cursor:
    post = serialize_doc(doc)
    
    if post.get("analysis_id"):
      try:
        a_type = post.get("analysis_type", "text")
        collection = COL_ANALYSIS_AI_IMAGE if a_type == "image" else COL_ANALYSIS_AI_TEXT
        analysis = db_instance[collection].find_one({"_id": ObjectId(post["analysis_id"])})

        if not analysis:
            alt_collection = COL_ANALYSIS_AI_TEXT if a_type == "image" else COL_ANALYSIS_AI_IMAGE
            analysis = db_instance[alt_collection].find_one({"_id": ObjectId(post["analysis_id"])})
            if analysis:
                a_type = "text" if alt_collection == COL_ANALYSIS_AI_TEXT else "image"

        if analysis:
          overall = analysis.get("overall", {})
          
          label = overall.get("label") or analysis.get("label") or analysis.get("prediction") or "Unknown"
          score = overall.get("confidence") or overall.get("score") or analysis.get("score") or analysis.get("confidence") or 0
          
          if a_type == "image":
              text = f"Image: {analysis.get('filename', 'unnamed')}"
              image_preview = analysis.get("image_preview")
          else:
              text = analysis.get("text") or analysis.get("content") or ""
              image_preview = None
          
          try:
            score = float(score)
          except (ValueError, TypeError):
            score = 0.0
          
          post["analysis_data"] = {
            "label": label,
            "score": score,
            "text_preview": text[:150] + "..." if text and len(text) > 150 else text,
            "full_text": text,
            "type": a_type,
            "image_preview": image_preview
          }
      except Exception as e:
        print(f"Error enriching post {post['_id']}: {e}")
        pass
        
    posts.append(post)
    
  return jsonify(posts)

@social_bp.route("/feed/<post_id>", methods=["DELETE"])
@require_auth
def delete_post(post_id):
  posts_col = db.get_database(DB_NAME)[COL_POSTS]
  post = posts_col.find_one({"_id": ObjectId(post_id)})
  
  if not post:
    raise NotFound("Post not found.")
  
  if post["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only delete your own posts.")

  posts_col.delete_one({"_id": ObjectId(post_id)})
  db.get_database(DB_NAME)[COL_COMMENTS].delete_many({"post_id": post_id})
  
  return jsonify({"success": True})

@social_bp.route("/feed/<post_id>", methods=["PUT"])
@require_auth
def update_post(post_id):
  data = request.get_json()
  new_content = data.get("content")
  
  if not new_content:
    raise BadRequest("Content cannot be empty.")
    
  posts_col = db.get_database(DB_NAME)[COL_POSTS]
  post = posts_col.find_one({"_id": ObjectId(post_id)})
  
  if not post:
    raise NotFound("Post not found.")
    
  if post["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only edit your own posts.")

  posts_col.update_one(
    {"_id": ObjectId(post_id)},
    {"$set": {"content": new_content, "updated_at": datetime.utcnow()}}
  )
  
  return jsonify({"success": True})

@social_bp.route("/feed/<post_id>/like", methods=["POST"])
@require_auth
def toggle_like(post_id):
  user_id = g.user.get("sub")
  posts_col = db.get_database(DB_NAME)[COL_POSTS]
  
  post = posts_col.find_one({"_id": ObjectId(post_id)})
  if not post:
    raise NotFound("Post not found.")

  if user_id in post.get("likes", []):
    posts_col.update_one(
      {"_id": ObjectId(post_id)},
      {"$pull": {"likes": user_id}}
    )
    liked = False
  else:
    posts_col.update_one(
      {"_id": ObjectId(post_id)},
      {"$addToSet": {"likes": user_id}}
    )
    liked = True

  return jsonify({"success": True, "liked": liked})

@social_bp.route("/feed/<post_id>/comment", methods=["POST"])
@require_auth
def add_comment(post_id):
  data = request.get_json()
  text = data.get("text")
  
  if not text:
    raise BadRequest("Comment cannot be empty.")

  comment = {
    "post_id": post_id,
    "user_id": g.user.get("sub"),
    "username": g.user.get("preferred_username", "Unknown"),
    "text": text,
    "created_at": datetime.utcnow()
  }

  db.get_database(DB_NAME)[COL_COMMENTS].insert_one(comment)
  
  db.get_database(DB_NAME)[COL_POSTS].update_one(
    {"_id": ObjectId(post_id)},
    {"$inc": {"comments_count": 1}}
  )

  return jsonify({"success": True})

@social_bp.route("/feed/<post_id>/comments", methods=["GET"])
def get_comments(post_id):
  comments_cursor = db.get_database(DB_NAME)[COL_COMMENTS].find({"post_id": post_id}).sort("created_at", 1)
  comments = [serialize_doc(doc) for doc in comments_cursor]
  return jsonify(comments)

@social_bp.route("/feed/comments/<comment_id>", methods=["DELETE"])
@require_auth
def delete_comment(comment_id):
  comments_col = db.get_database(DB_NAME)[COL_COMMENTS]
  comment = comments_col.find_one({"_id": ObjectId(comment_id)})
  
  if not comment:
    raise NotFound("Comment not found.")
  
  if comment["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only delete your own comments.")

  comments_col.delete_one({"_id": ObjectId(comment_id)})
  
  db.get_database(DB_NAME)[COL_POSTS].update_one(
    {"_id": ObjectId(comment["post_id"])},
    {"$inc": {"comments_count": -1}}
  )
  
  return jsonify({"success": True})

@social_bp.route("/feed/comments/<comment_id>", methods=["PUT"])
@require_auth
def update_comment(comment_id):
  data = request.get_json()
  new_text = data.get("text")
  
  if not new_text:
    raise BadRequest("Comment text cannot be empty.")
    
  comments_col = db.get_database(DB_NAME)[COL_COMMENTS]
  comment = comments_col.find_one({"_id": ObjectId(comment_id)})
  
  if not comment:
    raise NotFound("Comment not found.")
    
  if comment["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only edit your own comments.")

  comments_col.update_one(
    {"_id": ObjectId(comment_id)},
    {"$set": {"text": new_text, "updated_at": datetime.utcnow()}}
  )
  
  return jsonify({"success": True})

@social_bp.route("/feed/<user_id>/posts", methods=["GET"])
@role_required("admin")
def get_user_posts(user_id):
  posts_cursor = db.get_database(DB_NAME)[COL_POSTS].find({"user_id": user_id}).sort("created_at", -1)
  posts = [serialize_doc(doc) for doc in posts_cursor]
  return jsonify(posts)

@social_bp.route("/feed/<user_id>/comments", methods=["GET"])
@role_required("admin")
def get_user_comments(user_id):
  comments_cursor = db.get_database(DB_NAME)[COL_COMMENTS].find({"user_id": user_id}).sort("created_at", -1)
  comments = [serialize_doc(doc) for doc in comments_cursor]
  return jsonify(comments)
