def test_get():
    import scratchattach as sa
    project = sa.get_project(1209355136)

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
    #comment_replies
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

    assert sa.get_project(414601586).moderation_status() == "notsafe"
    assert sa.get_project(1207314193).moderation_status() == "safe"
    assert sa.get_project(1233).moderation_status() == "notreviewed"  # if this becomes reviewed, please update this
    # ^^ also this project is an infinite remix loop!

    assert sa.explore_projects()
    assert sa.search_projects(query="scratchattach")
