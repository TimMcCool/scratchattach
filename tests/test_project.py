import pprint
import sys
import warnings

def test_project():
    sys.path.insert(0, ".")
    import scratchattach as sa
    from util import session, credentials_available
    if not credentials_available():
        warnings.warn("Skipped test_project because there were no credentials available.")
        return
    sess = session()


    project = sess.connect_project(104)
    #tree = project.remix_tree_pretty()
    #assert len(tree) > 1000 # there is a lot of chars. Just assert that sth is generated

    project = sess.connect_project(1209355136)

    assert project
    assert project.title == "Sample project #1"
    assert project.author_name == "ScratchAttachV2"
    assert project.embed_url == "https://scratch.mit.edu/projects/1209355136/embed"
    assert project.is_shared()
    # create_remix
    # load_description
    # download
    # get_json
    # body
    # raw_json
    # raw_json_or_empty
    # creator_agent
    assert project.author().id == 147905216
    # studios
    comment = project.comments()[0]  # TODO: move this to a separate comment tester
    # comment_by_id
    # comment_replies
    # comment by id
    # (un)love
    # (un)favorite
    # pos_view
    # set_fields
    # turn on/off/toggle commenting
    # (un)share
    # set thumb
    # delete comment
    # report comment
    # post/reply comment
    # set body/json/upload json from
    # set title/instruction/notes
    # visibility

    assert comment.id == 489648029

    remix = project.remixes()[0]
    assert remix.id == 1209582809
    assert remix.title == "Sample remix"
    assert remix.author_name == "ScratchAttachV2"
    assert remix.embed_url == "https://scratch.mit.edu/projects/1209582809/embed"

    assert sess.connect_project(414601586).moderation_status() == "notsafe"
    assert sess.connect_project(1207314193).moderation_status() == "safe"
    assert sess.connect_project(
        1233).moderation_status() == "notreviewed"  # if this becomes reviewed, please update this
    # ^^ also this project is an infinite remix loop!

    assert sa.explore_projects()
    assert sa.search_projects(query="scratchattach")

if __name__ == '__main__':
    test_project()