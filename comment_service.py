from concurrent.futures import thread
import threading
import time
import copy

class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class CommentService:
    def __init__(self, post_store):
        self.post_store = post_store
        # TODO: Initialize your data structures and concurrency controls here.

        #structure of comments is something like { postId : [comments] }
        #for each comment there is replies : {} where you store all the replies
        self.comments = {}
        self.next_comment_id = 1
        self.next_reply_id = 1
        self.lock = threading.Lock()


    def _validate_input(self , user_id , content):

        #user id should be of type string and should not be empty after removing whitespaces
        if not isinstance(user_id , str) or not user_id.strip():
            raise ValidationError("user_id is not valid")

        if not isinstance(content , str) or not content.strip():
            raise ValidationError("content is not valid")

    
    def add_comment(self, post_id: int, user_id: str, content: str) -> dict:
        """
        Create a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "user_id": str,
            "content": str,
            "created_at": float,
            "replies": []
        }

        Raises NotFoundError if post_id does not exist.
        Raises ValidationError if user_id or content is empty.
        """
        self._validate_input(user_id , content)

        with self.lock:

            if not self.post_store.exists(post_id):
                raise NotFoundError("Post not found")

            comment = {
                "id": self.next_comment_id,
                "post_id": post_id,
                "user_id": user_id,
                "content": content,
                "created_at": time.time(),
                "replies": []
            }

            self.next_comment_id += 1

            if post_id not in self.comments:
                self.comments[post_id] = []

            self.comments[post_id].append(comment)

            #returning a deep copy so that changes in the copy dont reflect in original data
            return copy.deepcopy(comment)

            

    def add_reply(self, post_id: int, comment_id: int, user_id: str, content: str) -> dict:
        """
        Create a reply to a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "comment_id": int,
            "user_id": str,
            "content": str,
            "created_at": float
        }

        Raises NotFoundError if post_id does not exist.
        Raises NotFoundError if comment_id does not exist for the given post.
        Raises ValidationError if user_id or content is empty.
        """
        self._validate_input(user_id, content)

        with self.lock:
            if not self.post_store.exists(post_id):
                raise NotFoundError("Post not found")

            comments = self.comments.get(post_id , [])

            target_comment = None

            for comment in comments:
                if comment["id"] == comment_id:
                    target_comment = comment
                    break

            if target_comment is None:
                raise NotFoundError("Comment not found")

            reply = {
                "id": self.next_reply_id,
                "post_id": post_id,
                "comment_id": comment_id,
                "user_id": user_id,
                "content": content,
                "created_at": time.time()
            }

            self.next_reply_id += 1

            target_comment["replies"].append(reply)

            return copy.deepcopy(reply)

            

    def get_comments(self, post_id: int) -> list:
        """
        Return all comments for the given post.

        Each comment must include its "replies" list.
        Comments and replies must be returned in creation order.

        Raises NotFoundError if post_id does not exist.
        """
        
        with self.lock:

            if not self.post_store.exists(post_id):
                raise NotFoundError("Post not found")

            comments = self.comments.get(post_id , [])

            return copy.deepcopy(comments)
