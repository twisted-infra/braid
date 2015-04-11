function checkBranch(branch) {
    if (!branch) {
        alert("Must specify a branch");
        return false
    }
    return true
}

function forceBranch(branch, categories) {
    if (!checkBranch(branch)) {
        return
    }
    for (var i = 0; i < categories.length; i++) {
        var xhr = new XMLHttpRequest();
        var query = "?forcescheduler=force-" + escape(categories[i]) + "&branch=" + escape(branch)
        var path = "builders/_all/forceall"
        xhr.open("get", path + query, false)
        xhr.send()
    }
    window.location = "?branch=" + escape(branch)
}
