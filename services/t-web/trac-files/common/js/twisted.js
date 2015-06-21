/**
 * Create a DOM node factory for the given document object.
 *
 * @rtype:  C{function} that takes C{String}, C{object} mapping C{String}
 *     to C{String}, C{Array} of C{String} or DOM nodes
 * @return: A factory taking 3 arguments: C{tagName}, C{attrs} and
 *     C{children}
 */
function DOMBuilder(doc) {
    return function _nodeFactory(tagName, attrs, children) {
        var node = doc.createElement(tagName);
        if (attrs !== undefined) {
            for (var key in attrs) {
                node.setAttribute(key, attrs[key]);
            }
        }

        if (children !== undefined) {
            for (var i = 0; i < children.length; ++i) {
                var child = children[i];
                if (typeof child === 'string') {
                    child = doc.createTextNode(child);
                }
                node.appendChild(child);
            }
        }

        return node;
    };
}


/**
 * Format a C{Date} instance as I{YYYY-mm-dd}.
 */
function formatDate(d) {
    var year = d.getFullYear();
    var month = d.getMonth() + 1;
    var day = d.getDate();
    return [
        year, '-',
        (month < 10 ? '0' : '') + month, '-',
        (day < 10 ? '0' : '') + day].join('');
}


/**
 * Remove all the children of a node.
 */
function removeNodeContent(node) {
    while (node.lastChild) {
        node.removeChild(node.lastChild);
    }
}


/**
 * Load news feed items, from the Twisted Matrix Labs blog, and insert them
 * into the "twisted-news" element, if it exists.
 */
function loadNewsFeeds() {
    var container = document.getElementById('twisted-news');
    // Bail out if there is no news element.
    if (!container) {
        return;
    }

    var feed = new google.feeds.Feed(
        'http://feeds.feedburner.com/TwistedMatrixLaboratories');
    feed.setNumEntries(5);
    feed.load(function(result) {
        if (!result.error) {
            removeNodeContent(container);
            var D = DOMBuilder(container.ownerDocument);
            for (var i = 0; i < result.feed.entries.length; i++) {
                var entry = result.feed.entries[i];
                var prettyDate = formatDate(new Date(entry.publishedDate));
                var entryNode = D('div', {'class': 'feed-entry'}, [
                    D('a', {'href': entry.link}, [entry.title]),
                    D('div', {'class': 'feed-updated'}, [
                        'by ',
                        D('strong', {}, [entry.author]),
                        ' on ',
                        D('strong', {}, [prettyDate])])
                    ]);
                container.appendChild(entryNode);
            }
        }
    });
}
google.load('feeds', '1');
google.setOnLoadCallback(function () {
    // Load Twisted Matrix Labs news feed.
    loadNewsFeeds();
    // Enable Bootstrap.js tabs.
    $('#frontpage-tabs a').attr('data-toggle', 'tab');
});
