$(document).ready(function() {
    var ticket = /\/ticket\/(\d+)/.exec(document.location)[1];
    var delete_link = '<a href="../admin/ticket/delete/'+ticket+'">Delete</a>';
    var ticket_buttons = $('#ticket .inlinebuttons')[0];
    if (ticket_buttons) {
        $(ticket_buttons).append(delete_link);
    } else {
        $('#ticket table.properties').after('<div class="description"><h3><span class="inlinebuttons">'+delete_link+'</span>&nbsp;</h3></div>');
    }
    $('#changelog .inlinebuttons').each(function() {
            var comment = $('input[@name=replyto]', this)[0];
            if (comment) {
                comment = comment.value;
                $(this).append('<a href="../admin/ticket/comments/'+ticket+'?cnum='+comment+'">Delete</a>');

                // doesnt work, form tokens
                //                $(this).append('<form method="post" action="../admin/ticket/comments/' + ticket + '"><input type="submit" name="delete_' + comment + '" value="Delete"/></form>');
            }
        });
    });
