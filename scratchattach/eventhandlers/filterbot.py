"""v2 ready: FilterBot class"""

from .message_events import MessageEvents
import time
from abc import ABC

class BaseFilter(ABC):
    
    def __init__(self, filter_name="UntitledFilter"):
        self.filter_name = filter_name
    
    def apply(self, content, author_name, source_id) -> bool:
        return False

    
class ContainsFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, content=None, case_sensitive=False, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.content = content if case_sensitive or content is None else content.lower()
        self.case_sensitive = case_sensitive
        
    def apply(self, content, author_name, source_id) -> bool:
        if not self.case_sensitive:
            content = content.lower()
        return self.content in content
    
class EqualsFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, content=None, case_sensitive=False, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.content = content if case_sensitive or content is None else content.lower()
        self.case_sensitive = case_sensitive
        
    def apply(self, content, author_name, source_id) -> bool:
        if not self.case_sensitive:
            content = content.lower()
        return self.content == content
    
class AuthorFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, content=None, case_sensitive=False, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.content = content if case_sensitive or content is None else content.lower()
        self.case_sensitive = case_sensitive
        
    def apply(self, content, author_name, source_id) -> bool:
        if not self.case_sensitive:
            author_name = author_name.lower()
        return (self.content and self.content == author_name)
    
class OriginIdFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, profile=None, project_id=None, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.profile = profile
        self.project_id = project_id
        
    def apply(self, content, author_name, source_id) -> bool:
        return (self.project_id and self.project_id == source_id) or (self.profile and self.profile == source_id)

    
class ParentFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, subfilters=None, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.subfilters = subfilters or []
        
    def apply(self, content, author_name, source_id):
        return any(__filter.apply(content, author_name, source_id) for __filter in self.subfilters)
    
class MultiFilter(ParentFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, equals=None, contains=None, author_name=None, project_id=None, profile=None, case_sensitive=False, **kwargs):
        subfilters = []
        subfilters.append(ContainsFilter(content=contains, case_sensitive=case_sensitive))
        subfilters.append(EqualsFilter(content=equals, case_sensitive=case_sensitive))
        subfilters.append(AuthorFilter(content=author_name, case_sensitive=case_sensitive))
        subfilters.append(OriginIdFilter(profile=profile, project_id=project_id))
        kwargs.setdefault("subfilters", [])
        kwargs["subfilters"].extend(subfilters)
        super().__init__(filter_name, *args, **kwargs)
        self.equals=equals
        self.contains=contains
        self.author_name=author_name
        self.project_id=project_id
        self.profile=profile
        self.case_sensitive=case_sensitive
        self.filter_name = filter_name

class BaseHardFilter(BaseFilter):
    pass

class HardFilter(BaseHardFilter, MultiFilter):
    pass

class BaseSoftFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", score:float=1, *args, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.score = score

class SoftFilter(BaseSoftFilter, MultiFilter):
    pass

class BaseSpamFilter(BaseFilter):
    
    def __init__(self, filter_name="UntitledFilter", *args, **kwargs):
        super().__init__(filter_name, *args, **kwargs)
        self.memory = []
    
    def apply(self, content, author_name, source_id):
        applies = super().apply(content, author_name, source_id)
        if not applies:
            return False
        self.memory.insert(0, {"content":content, "time":time.time()})
        print(content, self.memory)
        for comment in list(self.memory)[1:]:
            if comment["time"] < time.time() -300:
                self.memory.remove(comment)
            if comment["content"].lower() == content.lower():
                return True
        return False

class SpamFilter(BaseSpamFilter, MultiFilter):
    pass

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
        if isinstance(filter_obj, BaseHardFilter):
            self.hard_filters.append(filter_obj)
        elif isinstance(filter_obj, BaseSoftFilter):
            self.soft_filters.append(filter_obj)
        elif isinstance(filter_obj, BaseSpamFilter):
            self.spam_filters.append(filter_obj)
    
    def add_f4f_filter(self):
        self.add_filter(HardFilter("(f4f_filter) 'f4f'", contains="f4f"))
        self.add_filter(HardFilter("(f4f_filter) 'follow me'", contains="follow me"))
        self.add_filter(HardFilter("(f4f_filter) 'follow @'", contains="follow @"))
        self.add_filter(HardFilter("(f4f_filter) f 4 f'", contains="f 4 f"))
        self.add_filter(HardFilter("(f4f_filter) 'follow for'", contains="follow for"))

    def add_ads_filter(self):
        self.add_filter(SoftFilter("(ads_filter) links", 1, contains="scratch.mit.edu/projects/"))
        self.add_filter(SoftFilter("(ads_filter) feedback", -1, contains="feedback"))
        self.add_filter(HardFilter("(ads_filter) 'check out my'", contains="check out my"))
        self.add_filter(HardFilter("(ads_filter) 'play my'", contains="play my"))
        self.add_filter(SoftFilter("(ads_filter) 'advertis'", 1, contains="advertis"))

    def add_spam_filter(self):
        self.add_filter(SpamFilter("(spam_filter)", contains=""))

    def add_genalpha_nonsense_filter(self):
        self.add_filter(HardFilter("(genalpha_nonsene_filter) 'skibidi'", contains="skibidi"))
        self.add_filter(HardFilter("[genalpha_nonsene_filter) 'rizzler'", contains="rizzler"))
        self.add_filter(HardFilter("(genalpha_nonsene_filter) 'fanum tax'", contains="fanum tax"))

    def on_message(self, message):
        if message.type == "addcomment":
            delete = False
            content = message.comment_fragment

            if message.comment_type == 0: # project comment
                source_id = message.comment_obj_id
                if self.user._session.connect_project(message.comment_obj_id).author_name != self.user.username:
                    return # no permission to delete
            if message.comment_type == 1: # profile comment
                source_id = message.comment_obj_title
                if message.comment_obj_title != self.user.username:
                    return # no permission to delete
            if message.comment_type == 2: # studio comment
                return # studio comments aren't handled

            # Apply hard filters
            for hard_filter in self.hard_filters:
                if hard_filter.apply(content, message.actor_username, source_id):
                    delete=True
                    if self.log_deletions:
                        print(f"DETECTED: #{message.comment_id} violates hard filter: {hard_filter.filter_name}")
                    break

            # Apply spam filters
            if delete is False:
                for spam_filter in self.spam_filters:
                    if spam_filter.apply(content, message.actor_username, source_id):
                        delete=True
                        if self.log_deletions:
                            print(f"DETECTED: #{message.comment_id} violates spam filter: {spam_filter.filter_name}")
                        break

            # Apply soft filters
            if delete is False:
                score = 0
                violated_filers = []
                for soft_filter in self.soft_filters:
                    if soft_filter.apply(content, message.actor_username, source_id):
                        score += soft_filter.score
                        violated_filers.append(soft_filter.name)
                if score >= 1:
                    print(f"DETECTED: #{message.comment_id} violates too many soft filters: {violated_filers}")
                    delete = True
            
            if delete is True:
                try:
                    message.target().delete()
                    if self.log_deletions:
                        print(f"DELETED: #{message.comment_id} by f{message.actor_username}: '{content}'")
                except Exception:
                    if self.log_deletions:
                        print(f"DELETION FAILED: #{message.comment_id} by f{message.actor_username}: '{content}'")

        