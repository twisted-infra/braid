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


$(document).ready(function () {
    // Enable Bootstrap.js tabs.
    $('#frontpage-tabs a').attr('data-toggle', 'tab');
});
