workflow "merge_and_cleanup" {
  resolves = ["When tests pass, merge and cleanup"]
  on = "check_run"
}

action "When tests pass, merge and cleanup" {
  uses = "alexwlchan/auto_merge_my_pull_requests@development"
  secrets = ["GITHUB_TOKEN"]
}
