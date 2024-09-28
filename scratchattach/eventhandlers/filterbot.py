"""v2 ready: FilterBot class"""

from .message_events import MessageEvents
import time

class HardFilter:

    def __init__(self, *, equals=None, contains=None, author_name=None, project_id=None, profile=None, case_sensitive=False):
        self.equals=equals
        self.contains=contains
        self.author_name=author_name
        self.project_id=project_id
        self.profile=profile
        self.case_sensitive=case_sensitive
    
    def apply(self, content, author_name, source_id):
        if not self.case_sensitive:
            content = content.lower()
        if self.case_sensitive:
            if self.equals == content:
                return True
        else:
            if self.equals.lower() == content:
                return True
        if self.case_sensitive:
            if self.contains.lower() in content:
                return True
        else:
            if self.contains in content:
                return True
        if self.author_name == author_name:
            return True
        if self.project_id == source_id or self.profile == source_id:
            return True
        return False

class SoftFilter(HardFilter):
    def __init__(self, score:float, *, equals=None, contains=None, author_name=None, project_id=None, profile=None, case_sensitive=False):
        self.score = score
        super().__init__(equals=equals, contains=contains, author_name=author_name, project_id=project_id, profile=profile, case_sensitive=case_sensitive)

class SpamFilter(HardFilter):
    def __init__(self, *, equals=None, contains=None, author_name=None, project_id=None, profile=None, case_sensitive=False):
        self.memory = []
        super().__init__(equals=equals, contains=contains, author_name=author_name, project_id=project_id, profile=profile, case_sensitive=case_sensitive)

    def apply(self, content, author_name, source_id):
        applies = super().apply(content, author_name, source_id)
        if not applies:
            return False
        self.memory.insert(0, {"content":content, "time":time.time()})
        for comment in list(self.memory)[1:]:
            if comment["time"] < time.time() -300:
                self.memory.remove(comment)
            if comment["content"].lower() == content.lower():
                return True

class Filterbot(MessageEvents):

    def __init__(self, user, *, log_deletions=True):
        super().__init__(user)
        self.hard_filters = []
        self.soft_filters = []
        self.spam_filters = []
        self.log_deletions = log_deletions
        self.event(self.on_message)
        self.update_interval = 2

    def add_filter(self, filter_obj):
        if isinstance(filter_obj, HardFilter):
            self.hard_filters.append(filter_obj)
        if isinstance(filter_obj, SoftFilter):
            self.soft_filters.append(filter_obj)
        if isinstance(filter_obj, SpamFilter):
            self.spam_filters.append(filter_obj)
    
    def add_f4f_filter(self):
        self.add_filter(HardFilter(contains="f4f"))
        self.add_filter(HardFilter(contains="follow me"))
        self.add_filter(HardFilter(contains="please follow"))
        self.add_filter(HardFilter(contains="f 4 f"))
        self.add_filter(HardFilter(contains="follow for follow"))

    def add_ads_filter(self):
        self.add_filter(SoftFilter(1, contains="scratch.mit.edu/projects/"))
        self.add_filter(SoftFilter(-1, contains="feedback"))
        self.add_filter(HardFilter(contains="check out my"))
        self.add_filter(HardFilter(contains="play my"))

    def add_spam_filter(self):
        self.add_filter(SpamFilter(contains=""))


    def on_message(self, message):
        if message.type == "addcomment":
            delete = False
            content = message.comment_fragment

            if message.comment_type == 0: # project comment
                source_id = self.comment_obj_id
                if self.user._session.connect_project(self.comment_obj_id).author_name != self.user.username:
                    return # no permission to delete
            if message.comment_type == 1: # profile comment
                source_id = self.comment_obj_title
                if self.comment_obj_title != self.user.username:
                    return # no permission to delete
            if message.comment_type == 2: # studio comment
                return # studio comments aren't handled

            # Apply hard filters
            for hard_filter in self.hard_filters:
                if hard_filter.apply(content, message.actor_username, source_id):
                    delete=True
                    if self.log_deletions:
                        print(f"Comment #{content.comment_id} violates hard filter: {hard_filter}")
                    break

            # Apply spam filters
            if delete is False:
                for spam_filter in self.spam_filters:
                    if spam_filter.apply(content, message.actor_username, source_id):
                        delete=True
                        if self.log_deletions:
                            print(f"Comment #{content.comment_id} violates hard filter: {spam_filter}")
                        break

            # Apply soft filters
            if delete is False:
                score = 0
                for soft_filter in self.soft_filters:
                    if soft_filter.apply(content, message.actor_username, source_id):
                        score += soft_filter.score
                if score > 1:
                    print(f"Comment #{content.comment_id} violates too many soft filters")
                    delete = True
            
            if delete is True:
                try:
                    message.target().delete()
                    if self.log_deletions:
                        print(f"Deleted comment #{content.comment_id} by f{message.actor_username}: '{content}'")
                except Exception:
                    if self.log_deletions:
                        print(f"Failed to: Delete comment #{content.comment_id} by f{message.actor_username}: '{content}'")

        