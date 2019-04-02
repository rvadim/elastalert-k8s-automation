workflow "Base pipeline" {
  on = "push"
  resolves = ["test"]
}

action "test" {
  uses = "./actions/py37/"
  args = "tox"
}
