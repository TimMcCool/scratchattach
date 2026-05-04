"""FilterBot class"""

from __future__ import annotations

import requests as _requests

from .message_events import MessageEvents
import time
from collections import deque
from scratchattach.site import activity


class HardFilter:
    def __init__(
        self,
        filter_name="UntitledFilter",
        *,
        equals=None,
        contains=None,
        author_name=None,
        project_id=None,
        profile=None,
        case_sensitive=False,
    ):
        self.equals = equals
        self.contains = contains
        self.author_name = author_name
        self.project_id = project_id
        self.profile = profile
        self.case_sensitive = case_sensitive
        self.filter_name = filter_name

    def apply(self, content, author_name, source_id):
        text_to_check = content if self.case_sensitive else content.lower()
        if self.equals is not None:
            comparison_equals = self.equals if self.case_sensitive else self.equals.lower()
            if text_to_check == comparison_equals:
                return True
        if self.contains is not None:
            comparison_contains = self.contains if self.case_sensitive else self.contains.lower()
            if comparison_contains in text_to_check:
                return True
        if self.author_name is not None and self.author_name == author_name:
            return True
        if (self.project_id is not None and self.project_id == source_id) or (
            self.profile is not None and self.profile == source_id
        ):
            return True
        return False


class SoftFilter(HardFilter):
    def __init__(
        self,
        score: float,
        filter_name="UntitledFilter",
        *,
        equals=None,
        contains=None,
        author_name=None,
        project_id=None,
        profile=None,
        case_sensitive=False,
    ):
        self.score = score
        super().__init__(
            filter_name,
            equals=equals,
            contains=contains,
            author_name=author_name,
            project_id=project_id,
            profile=profile,
            case_sensitive=case_sensitive,
        )


class SpamFilter(HardFilter):
    def __init__(
        self,
        filter_name="UntitledFilter",
        *,
        equals=None,
        contains=None,
        author_name=None,
        project_id=None,
        profile=None,
        case_sensitive=False,
    ):
        super().__init__(
            filter_name,
            equals=equals,
            contains=contains,
            author_name=author_name,
            project_id=project_id,
            profile=profile,
            case_sensitive=case_sensitive,
        )
        self.memory = deque()
        self.retention_period = 300

    def apply(self, content, author_name, source_id):
        if not super().apply(content, author_name, source_id):
            return False
        current_time = time.time()

        # Prune old entries from memory
        while self.memory and self.memory[-1]["time"] < current_time - self.retention_period:
            self.memory.pop()

        content_lower = content.lower()
        # Check for duplicates
        for comment in self.memory:
            if comment["content"].lower() == content_lower:
                return True

        # Add new comment to memory
        self.memory.appendleft({"content": content, "time": current_time})
        return False


class Filterbot(MessageEvents):
    # The Filterbot class is built upon MessageEvents, similar to how CloudEvents is built upon CloudEvents

    def __init__(self, user, *, log_deletions=True):
        super().__init__(user)
        self.hard_filters = []
        self.soft_filters = []
        self.spam_filters = []
        self.log_deletions = log_deletions
        self.event(self.on_message, thread=False)
        self.update_interval = 2

    def add_filter(self, filter_obj):
        if isinstance(filter_obj, SpamFilter):
            self.spam_filters.append(filter_obj)
        elif isinstance(filter_obj, SoftFilter):
            self.soft_filters.append(filter_obj)
        elif isinstance(filter_obj, HardFilter):
            self.hard_filters.append(filter_obj)

    def add_f4f_filter(self):
        self.add_filter(HardFilter("(f4f_filter) 'f4f'", contains="f4f"))
        self.add_filter(HardFilter("(f4f_filter) 'follow me'", contains="follow me"))
        self.add_filter(HardFilter("(f4f_filter) 'follow @'", contains="follow @"))
        self.add_filter(HardFilter("(f4f_filter) f 4 f'", contains="f 4 f"))
        self.add_filter(HardFilter("(f4f_filter) 'follow for'", contains="follow for"))

    def add_ads_filter(self):
        self.add_filter(SoftFilter(1, "(ads_filter) links", contains="scratch.mit.edu/projects/"))
        self.add_filter(SoftFilter(-1, "(ads_filter) feedback", contains="feedback"))
        self.add_filter(HardFilter("(ads_filter) 'check out my'", contains="check out my"))
        self.add_filter(HardFilter("(ads_filter) 'play my'", contains="play my"))
        self.add_filter(SoftFilter(1, "(ads_filter) 'advertis'", contains="advertis"))

    def add_spam_filter(self):
        self.add_filter(SpamFilter("(spam_filter)", contains=""))

    def add_genalpha_nonsense_filter(self):
        self.add_filter(HardFilter("(genalpha_nonsene_filter) 'skibidi'", contains="skibidi"))
        self.add_filter(HardFilter("[genalpha_nonsene_filter) 'rizzler'", contains="rizzler"))
        self.add_filter(HardFilter("(genalpha_nonsene_filter) 'fanum tax'", contains="fanum tax"))

    def _apply_filters(self, message: activity.Activity, source_id: int | str | None) -> tuple[bool, str]:
        """
        Applies the filterbot filters and returns whether the message violates the filters, and why
        returns tuple of whether to delete, and the reason
        """
        assert message.type == activity.ActivityTypes.addcomment

        content = message.comment_fragment

        # Apply hard filters
        for hard_filter in self.hard_filters:
            if hard_filter.apply(content, message.actor_username, source_id):
                return True, f"hard filter: {hard_filter.filter_name}"

        # Apply spam filters
        for spam_filter in self.spam_filters:
            if spam_filter.apply(content, message.actor_username, source_id):
                return True, f"spam filter: {spam_filter.filter_name}"

        # Apply soft filters
        score = 0
        violated_filters = []
        for soft_filter in self.soft_filters:
            if soft_filter.apply(content, message.actor_username, source_id):
                score += soft_filter.score
                violated_filters.append(soft_filter.filter_name)

        if score >= 1:
            return True, f"too many soft filters: {violated_filters}"

        return False, ""

    def _determine_source_and_deletable(self, message: activity.Activity) -> tuple[int | str | None, bool]:
        if message.comment_type == 0:  # project comment
            project_id = message.comment_obj_id
            if self.user._session.connect_project(message.comment_obj_id).author_name == self.user.username:
                return project_id, True  # only permission to delete comments that are on our own project

        elif message.comment_type == 1:  # profile comment
            if message.comment_obj_title == self.user.username:
                return message.comment_obj_title, True  # no permission to delete messages that are not on our profile
        # elif message.comment_type == 2:  # studio comment
        # studio comments aren't handled
        return None, False

    def _print_if_logging(self, *args, **kwargs):
        if self.log_deletions:
            print(*args, **kwargs)

    def on_message(self, message: activity.Activity):
        if message.type != activity.ActivityTypes.addcomment:
            return

        source_id, deletable = self._determine_source_and_deletable(message)
        if not deletable:
            return

        content = message.comment_fragment
        delete, reason = self._apply_filters(message, source_id)

        if delete:
            self._print_if_logging(f"DETECTED: #{message.comment_id} violates {reason}")
            try:
                if target := message.target_comment():
                    resp = target.delete()
                    assert isinstance(resp, _requests.Response)
                    self._print_if_logging(
                        f"DELETED: #{message.comment_id} by {message.actor_username!r}: '{content}' with message {resp.content!r} & headers {resp.headers!r}"
                    )
            except Exception as e:
                if self.log_deletions:
                    print(f"DELETION FAILED: #{message.comment_id} by {message.actor_username!r}: '{content}'; exception: {e}")
