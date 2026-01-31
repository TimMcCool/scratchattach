import scratchattach as sa
import util


def test_classroom():
    sess = util.teacher_session()
    if not sess:
        return

    classes = sess.mystuff_classes()
    assert len(classes) > 0
    room = classes[0]
    room = sa.get_classroom("23448")
    names = room.student_names(offset=2, limit=62)
    print(len(names))
    print(names)


if __name__ == "__main__":
    test_classroom()
