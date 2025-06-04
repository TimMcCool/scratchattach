"""ForumTopic and ForumPost classes"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag

from . import user
from . import session as module_session
from scratchattach.utils.commons import headers
from scratchattach.utils import exceptions, commons
from ._base import BaseSiteComponent
from scratchattach.utils.requests import requests

@dataclass
class ForumTopic(BaseSiteComponent):
    '''
    Represents a Scratch forum topic.

    Attributes:

    :.id:

    :.title:

    :.category_name:

    :.last_updated:

    Attributes only available if the object was created using scratchattach.get_topic_list or scratchattach.Session.connect_topic_list:

    :.reply_count:

    :.view_count:

    :.update(): Updates the attributes
    '''
    id: int
    title: str
    category_name: str
    last_updated: str
    _session: Optional[module_session.Session] = field(default=None)
    reply_count: Optional[int] = field(default=None)
    view_count: Optional[int] = field(default=None)

    def __post_init__(self):
        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_api = f"https://scratch.mit.edu/discuss/feeds/topic/{self.id}/"

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session.get_headers()
            self._cookies = self._session.get_cookies()

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        # As there is no JSON API for getting forum topics anymore,
        # the data has to be retrieved from the XML feed.
        response = self.update_function(
            self.update_api,
            headers = self._headers,
            cookies = self._cookies, timeout=20 # fetching forums can take very long
        )
        # Check for 429 error:
        if "429" in str(response):
            return "429"
        
        # Parse XML response
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}

                title = root.findtext('atom:title', namespaces=namespace).replace("Latest posts on ","")
                category_name = root.findall('.//atom:entry', namespaces=namespace)[0].findtext('.//atom:title', namespaces=namespace).split(" :: ")[1]
                last_updated = root.findtext('atom:updated', namespaces=namespace)

            except Exception as e:
                raise exceptions.ScrapeError(str(e))
        else:
            raise exceptions.ForumContentNotFound
        self.title = title
        self.category_name = category_name
        self.last_updated = last_updated
        return True
    
    @classmethod
    def from_id(cls, __id: int, session: module_session.Session, update: bool = False):
        new = cls(id=__id, _session=session, title="", last_updated="", category_name="")
        if update:
            new.update()
        return new
    
    def _update_from_dict(self, data: dict[str, Any]):
        self.__dict__.update(data)

    def posts(self, *, page=1, order="oldest") -> list[ForumPost]:
        """
        Args:
            page (int): The page of the forum topic that should be returned. First page is at index 1.

        Returns:
            list<scratchattach.forum.ForumPost>: A list containing the posts from the specified page of the forum topic 
        """
        if order != "oldest":
            print("Warning: All post orders except for 'oldest' are deprecated and no longer work") # For backwards compatibility

        posts = []
        
        try:
            url = f"https://scratch.mit.edu/discuss/topic/{self.id}/?page={page}"
            response = requests.get(url, headers=headers, cookies=self._cookies)
        except Exception as e:
            raise exceptions.FetchError(str(e))
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            soup_elm = soup.find("div", class_="djangobb")
            assert isinstance(soup_elm, Tag)
            try:
                pagination_div = soup_elm.find('div', class_='pagination')
                assert isinstance(pagination_div, Tag)
                num_pages = int(pagination_div.find_all('a', class_='page')[-1].text)
            except Exception:
                num_pages = 1

            try:
                # get topic category:
                topic_category = ""
                breadcrumb_ul = soup_elm.find_all('ul')[1]  # Find the second ul element
                if breadcrumb_ul:
                    assert isinstance(breadcrumb_ul, Tag)
                    link = breadcrumb_ul.find_all('a')[1]  # Get the right anchor tag
                    topic_category = link.text.strip()  # Extract and strip text content
            except Exception as e:
                print(f"Warning: Couldn't scrape topic category for topic {self.id} - {e}")
                topic_category = ""
                
            # get corresponding posts:
            post_htmls = soup.find_all('div', class_='blockpost')
            for raw_post in post_htmls:
                if not isinstance(raw_post, Tag):
                    continue
                post = ForumPost(id=int(str(raw_post['id']).replace("p", "")), topic_id=self.id, _session=self._session, topic_category=topic_category, topic_num_pages=num_pages)
                post.update_from_html(raw_post)

                posts.append(post)
        except Exception as e:
            raise exceptions.ScrapeError() from e

        return posts

    def first_post(self):
        """
        Returns:
            scratchattach.forum.ForumPost: An object representing the first topic post 
        """
        posts = self.posts(page=1)
        if len(posts) > 0:
            return posts[0]

@dataclass
class ForumPost(BaseSiteComponent):
    '''
    Represents a Scratch forum post.

    Attributes:

    :.id:

    :.author_name: The name of the user who created this post

    :.author_avatar_url:

    :.posted: The date the post was made

    :.topic_id: The id of the topic this post is in

    :.topic_name: The name of the topic the post is in

    :.topic_category: The name of the category the post topic is in

    :.topic_num_pages: The number of pages the post topic has

    :.deleted: Whether the post was deleted (always False because deleted posts can't be retrieved anymore)

    :.html_content: Returns the content as HTML

    :.content: Returns the content as text

    :.post_index: The index that the post has in the topic
        
    :.update(): Updates the attributes
    '''
    id: int = field(default=0)
    topic_id: int = field(default=0)
    topic_name: str = field(default="")
    topic_category: str = field(default="")
    topic_num_pages: int = field(default=0)
    author_name: str = field(default="")
    author_avatar_url: str = field(default="")
    posted: str = field(default="")
    deleted: bool = field(default=False)
    html_content: str = field(default="")
    content: str = field(default="")
    post_index: int = field(default=0)
    _session: Optional[module_session.Session] = field(default=None)
    def __post_init__(self):

        # A forum post can't be updated the usual way as there is no API anymore
        self.update_api = ""

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session.get_headers()
            self._cookies = self._session.get_cookies()

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"
    
    def update_function(self, *args, **kwargs):
        raise TypeError("Forum posts cannot be updated like this")

    def update(self):
        """
        Updates the attributes of the ForumPost object.
        As there is no API for retrieving a single post anymore, this requires reloading the forum page.
        """
        page = 1
        posts = ForumTopic.from_id(self.topic_id, session=self._session).posts(page=1)
        while posts != []:
            matching = list(filter(lambda x : int(x.id) == int(self.id), posts))
            if len(matching) > 0:
                this = matching[0]
                break
            page += 1
            posts = ForumTopic.from_id(self.topic_id, session=self._session).posts(page=page)
        else:
            return False
        self._update_from_dict(vars(this))

    def _update_from_dict(self, data: dict[str, Any]):
        self.__dict__.update(data)
        return True
    
    def update_from_html(self, soup_html: Tag):
        return self._update_from_html(soup_html)

    def _update_from_html(self, soup_html: Tag):
        post_index_elm = soup_html.find('span', class_='conr')
        assert isinstance(post_index_elm, Tag)
        id_attr = soup_html['id']
        assert isinstance(id_attr, str)
        posted_elm = soup_html.find('a', href=True)
        assert isinstance(posted_elm, Tag)
        content_elm = soup_html.find('div', class_='post_body_html')
        assert isinstance(content_elm, Tag)
        author_name_elm = soup_html.select_one('dl dt a')
        assert isinstance(author_name_elm, Tag)
        topic_name_elm = soup_html.find('h3')
        assert isinstance(topic_name_elm, Tag)
        
        self.post_index = int(post_index_elm.text.strip('#'))
        self.id = int(id_attr.replace("p", ""))
        self.posted = posted_elm.text.strip()
        self.content = content_elm.text.strip()
        self.html_content = str(soup_html.find('div', class_='post_body_html'))
        self.author_name = author_name_elm.text.strip()
        self.author_avatar_url = str(author_name_elm['href'])
        self.topic_name = topic_name_elm.text.strip()
        return True

    def topic(self):
        """
        Returns:
            scratchattach.forum.ForumTopic: An object representing the forum topic this post is in.
        """
        return self._make_linked_object("id", self.topic_id, ForumTopic, exceptions.ForumContentNotFound)

    def ocular_reactions(self):
        return requests.get(f"https://my-ocular.jeffalo.net/api/reactions/{self.id}", timeout=10).json()

    def author(self):
        """
        Returns:
            scratchattach.user.User: An object representing the user who created this forum post.
        """
        return self._make_linked_object("username", self.author_name, user.User, exceptions.UserNotFound)
    
    def edit(self, new_content: str):
        """
        Changes the content of the forum post.  You can only use this function if this object was created using :meth:`scratchattach.session.Session.connect_post` or through another method that requires authentication. You must own the forum post.
        
        Args:
            new_content (str): The text that the forum post will be set to.
        """
        
        self._assert_auth()

        cookies = dict(self._cookies)
        cookies["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        cookies["Content-Type"] = "application/x-www-form-urlencoded"

        r = requests.post(
            f"https://scratch.mit.edu/discuss/post/{self.id}/edit/",
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "de,en;q=0.9",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "Referer": f"https://scratch.mit.edu/discuss/post/{self.id}/edit/",
                "x-csrftoken": "a"
            },
            cookies = cookies,
            json = f"csrfmiddlewaretoken=a&body={new_content}&",
            timeout = 10,
        )


def get_topic(topic_id) -> ForumTopic:

    """
    Gets a forum topic without logging in. Data received from Scratch's RSS feed XML API.

    Args:
        topic_id (int): ID of the requested forum topic

    Returns:
        scratchattach.forum.ForumTopic: An object representing the requested forum topic

    Warning:
        Scratch's API uses very heavy caching for logged out users, therefore the returned data will not be up to date.

        Any methods that require authentication will not work on the returned object.
        
        If you need up-to-date data or want to use methods that require authentication, create the object with :meth:`scratchattach.session.Session.connect_topic` instead.
    """
    return commons._get_object("id", topic_id, ForumTopic, exceptions.ForumContentNotFound)


def get_topic_list(category_id, *, page=1):

    """
    Gets the topics from a forum category without logging in. Data web-scraped from Scratch's forums UI.

    Args:
        category_id (str): ID of the forum category
    
    Keyword Arguments:
        page (str): Page of the category topics that should be returned

    Returns:
        list<scratchattach.forum.ForumTopic>: A list containing the forum topics from the specified category

    Warning:
        Scratch's API uses very heavy caching for logged out users, therefore the returned data will not be up to date.

        Any methods that require authentication will not work on the returned objects.

        If you need up-to-date data or want to use methods that require authentication, get the forum topics with :meth:`scratchattach.session.Session.connect_topic_list` instead.
    """

    try:
        response = requests.get(f"https://scratch.mit.edu/discuss/{category_id}/?page={page}")
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        raise exceptions.FetchError(str(e))

    try:
        category_name = soup.find('h4').find("span").get_text()
    except Exception as e:
        raise exceptions.BadRequest("Invalid category id")

    try:
        topics = soup.find_all('tr')
        topics.pop(0)
        return_topics = []

        for topic in topics:
            title_link = topic.find('a')
            title = title_link.text.strip()
            topic_id = title_link['href'].split('/')[-2]

            columns = topic.find_all('td')
            columns = [column.text for column in columns]
            if len(columns) == 1:
                # This is a sticky topic -> Skip it
                continue

            last_updated = columns[3].split(" ")[0] + " " + columns[3].split(" ")[1]

            return_topics.append(ForumTopic(id=int(topic_id), title=title, category_name=category_name, last_updated=last_updated, reply_count=int(columns[1]), view_count=int(columns[2])))
        return return_topics
    except Exception as e:
        raise exceptions.ScrapeError(str(e))


def youtube_link_to_scratch(link: str):
    """
    Converts a YouTube url (in multiple formats) like https://youtu.be/1JTgg4WVAX8?si=fIEskaEaOIRZyTAz
    to a link like https://scratch.mit.edu/discuss/youtube/1JTgg4WVAX8
    """
    url_parse = urlparse(link)
    query_parse = parse_qs(url_parse.query)
    if 'v' in query_parse:
        video_id = query_parse['v'][0]
    else:
        video_id = url_parse.path.split('/')[-1]
    return f"https://scratch.mit.edu/discuss/youtube/{video_id}"
