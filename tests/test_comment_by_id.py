import scratchattach as sa


def test_comment_by_id():
    usr = sa.get_user("griffpatch")
    comment = usr.comment_by_id(398143091)
    print(comment)

if __name__ == "__main__":
    test_comment_by_id()
