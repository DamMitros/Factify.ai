from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from bson import ObjectId
from datetime import datetime
from keycloak_client import require_auth
from common.python import db

social_bp = Blueprint("social", __name__)

def serialize_doc(doc):
  doc["_id"] = str(doc["_id"])
  return doc

@social_bp.route("/my-analyses", methods=["GET"])
@require_auth
def get_my_analyses():
  user_id = g.user.get("sub")  
  db_instance = db.get_database("factify")
  results = list(db_instance["analysis"].find({"user_id": user_id}).sort("created_at", -1).limit(20))

  analyses = []
  for doc in results:
    overall = doc.get("overall", {})
    label = overall.get("label") or doc.get("label") or doc.get("prediction") or "Unknown"
    score = overall.get("confidence") or overall.get("score") or doc.get("score") or doc.get("confidence") or 0
    text = doc.get("text") or doc.get("content") or ""

    try:
      score = float(score)
    except (ValueError, TypeError):
      score = 0.0

    analyses.append({
      "id": str(doc["_id"]),
      "text_preview": text[:80] + "..." if text else "No text content",
      "label": label,
      "score": score,
      "created_at": doc.get("timestamp") or doc.get("created_at")
    })
  return jsonify(analyses)


@social_bp.route("/feed", methods=["POST"])
@require_auth
def share_prediction():
  data = request.get_json()
  content = data.get("content")
  analysis_id = data.get("analysis_id")

  if not content and not analysis_id:
    raise BadRequest("Post must contain content or analysis reference.")

  post = {
    "user_id": g.user.get("sub"),
    "username": g.user.get("preferred_username", "Unknown"),
    "content": content,
    "analysis_id": analysis_id,
    "likes": [],
    "comments_count": 0,
    "created_at": datetime.utcnow()
  }

  result = db.get_database("factify")["posts"].insert_one(post)
  
  return jsonify({
    "success": True,
    "postId": str(result.inserted_id)
  })

@social_bp.route("/feed", methods=["GET"])
def get_feed():
  posts_cursor = db.get_database("factify")["posts"].find().sort("created_at", -1).limit(50)
  posts = []
  
  db_instance = db.get_database("factify")
  
  for doc in posts_cursor:
    post = serialize_doc(doc)
    
    if post.get("analysis_id"):
      try:
        analysis = db_instance["analysis"].find_one({"_id": ObjectId(post["analysis_id"])})

        if analysis:
          overall = analysis.get("overall", {})
          
          label = overall.get("label") or analysis.get("label") or analysis.get("prediction") or "Unknown"
          score = overall.get("confidence") or overall.get("score") or analysis.get("score") or analysis.get("confidence") or 0
          text = analysis.get("text") or analysis.get("content") or ""
          
          try:
            score = float(score)
          except (ValueError, TypeError):
            score = 0.0
          
          post["analysis_data"] = {
            "label": label,
            "score": score,
            "text_preview": text[:150] + "..." if text else "",
            "full_text": text
          }
      except Exception as e:
        print(f"Error enriching post {post['_id']}: {e}")
        pass
        
    posts.append(post)
    
  return jsonify(posts)

@social_bp.route("/feed/<post_id>", methods=["DELETE"])
@require_auth
def delete_post(post_id):
  posts_col = db.get_database("factify")["posts"]
  post = posts_col.find_one({"_id": ObjectId(post_id)})
  
  if not post:
    raise NotFound("Post not found.")
  
  if post["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only delete your own posts.")

  posts_col.delete_one({"_id": ObjectId(post_id)})
  db.get_database("factify")["comments"].delete_many({"post_id": post_id})
  
  return jsonify({"success": True})

@social_bp.route("/feed/<post_id>", methods=["PUT"])
@require_auth
def update_post(post_id):
  data = request.get_json()
  new_content = data.get("content")
  
  if not new_content:
    raise BadRequest("Content cannot be empty.")
    
  posts_col = db.get_database("factify")["posts"]
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
  posts_col = db.get_database("factify")["posts"]
  
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

  db.get_database("factify")["comments"].insert_one(comment)
  
  db.get_database("factify")["posts"].update_one(
    {"_id": ObjectId(post_id)},
    {"$inc": {"comments_count": 1}}
  )

  return jsonify({"success": True})

@social_bp.route("/feed/<post_id>/comments", methods=["GET"])
def get_comments(post_id):
  comments_cursor = db.get_database("factify")["comments"].find({"post_id": post_id}).sort("created_at", 1)
  comments = [serialize_doc(doc) for doc in comments_cursor]
  return jsonify(comments)

@social_bp.route("/feed/comments/<comment_id>", methods=["DELETE"])
@require_auth
def delete_comment(comment_id):
  comments_col = db.get_database("factify")["comments"]
  comment = comments_col.find_one({"_id": ObjectId(comment_id)})
  
  if not comment:
    raise NotFound("Comment not found.")
  
  if comment["user_id"] != g.user.get("sub"):
    raise Forbidden("You can only delete your own comments.")

  comments_col.delete_one({"_id": ObjectId(comment_id)})
  
  db.get_database("factify")["posts"].update_one(
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
    
  comments_col = db.get_database("factify")["comments"]
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
