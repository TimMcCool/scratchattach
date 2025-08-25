def test_get():
  import scratchattach as sa
  project = sa.get_project(104)
  assert project
  assert project.title == "Weekend"
