"""ForumTopic and ForumPost classes"""
from __future__ import annotations

from . import user
from ..utils.commons import headers
from ..utils import exceptions, commons
from ._base import BaseSiteComponent
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from ..utils.requests import Requests as requests

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

    def __init__(self, **entries):
        # Info on how the .update method has to fetch the data:
        self.update_function = requests.get
        self.update_API = f"https://scratch.mit.edu/discuss/feeds/topic/{entries['id']}/"

        # Set attributes every Project object needs to have:
        self._session = None
        self.id = 0
        self.reply_count = None
        self.view_count = None
        
        # Update attributes from entries dict:
        self.__dict__.update(entries)

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        # As there is no JSON API for getting forum topics anymore,
        # the data has to be retrieved from the XML feed.
        response = self.update_function(
            self.update_API,
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

        return self._update_from_dict(dict(
            title = title, category_name = category_name, last_updated = last_updated
        ))
        

    def _update_from_dict(self, data):
        self.__dict__.update(data)
        return True

    def posts(self, *, page=1, order="oldest"):
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
            soup = soup.find("div", class_="djangobb")

            try:
                pagination_div = soup.find('div', class_='pagination')
                num_pages = int(pagination_div.find_all('a', class_='page')[-1].text)
            except Exception:
                num_pages = 1

            try:
                # get topic category:
                topic_category = ""
                breadcrumb_ul = soup.find_all('ul')[1]  # Find the second ul element
                if breadcrumb_ul:
                    link = breadcrumb_ul.find_all('a')[1]  # Get the right anchor tag
                    topic_category = link.text.strip()  # Extract and strip text content
            except Exception as e:
                print(f"Warning: Couldn't scrape topic category for topic {self.id} - {e}")
                topic_category = ""
                
            # get corresponding posts:
            post_htmls = soup.find_all('div', class_='blockpost')
            for raw_post in post_htmls:
                post = ForumPost(id=int(raw_post['id'].replace("p", "")), topic_id=self.id, _session=self._session, topic_category=topic_category, topic_num_pages=num_pages)
                post._update_from_html(raw_post)

                posts.append(post)
        except Exception as e:
            raise exceptions.ScrapeError(str(e))

        return posts

    def first_post(self):
        """
        Returns:
            scratchattach.forum.ForumPost: An object representing the first topic post 
        """
        posts = self.posts(page=1)
        if len(posts) > 0:
            return posts[0]


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

    def __init__(self, **entries):

        # A forum post can't be updated the usual way as there is no API anymore
        self.update_function = None
        self.update_API = None

        # Set attributes every Project object needs to have:
        self._session = None
        self.id = 0
        self.topic_id = 0
        self.deleted = False

        # Update attributes from entries dict:
        self.__dict__.update(entries)

        # Headers and cookies:
        if self._session is None:
            self._headers = headers
            self._cookies = {}
        else:
            self._headers = self._session._headers
            self._cookies = self._session._cookies

        # Headers for operations that require accept and Content-Type fields:
        self._json_headers = dict(self._headers)
        self._json_headers["accept"] = "application/json"
        self._json_headers["Content-Type"] = "application/json"

    def update(self):
        """
        Updates the attributes of the ForumPost object.
        As there is no API for retrieving a single post anymore, this requires reloading the forum page.
        """
        page = 1
        posts = ForumTopic(id=self.topic_id, _session=self._session).posts(page=1)
        while posts != []:
            matching = list(filter(lambda x : int(x.id) == int(self.id), posts))
            if len(matching) > 0:
                this = matching[0]
                break
            page += 1
            posts = ForumTopic(id=self.topic_id, _session=self._session).posts(page=page)
        else:
            return False
        
        return self._update_from_dict(this.__dict__)

    def _update_from_dict(self, data):
        self.__dict__.update(data)
        return True

    def _update_from_html(self, soup_html):
        self.post_index = int(soup_html.find('span', class_='conr').text.strip('#'))
        self.id = int(soup_html['id'].replace("p", ""))
        self.posted = soup_html.find('a', href=True).text.strip()
        self.content = soup_html.find('div', class_='post_body_html').text.strip()
        self.html_content = str(soup_html.find('div', class_='post_body_html'))
        self.author_name = soup_html.find('dl').find('dt').find('a').text.strip()
        self.author_avatar_url = soup_html.find('dl').find('dt').find('a')['href']
        self.topic_name = soup_html.find('h3').text.strip()
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
    
    def edit(self, new_content):
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
