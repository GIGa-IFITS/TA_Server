// Script to run on mainindex.html
var treeFrameCollapseSize = "9,*,0";
var messagesFrameCollapseSize = "*,8";
var reportHeaderFrameCollapseSize = "9,*";

/**
 * Modifies frame to show/hide tree depending on expanded parameter.
 * @param {boolean} expanded True if tree frame should be expanded, false otherwise.
 */
function showTreeFrame(expanded) {
    var collapseSize = "9,*,0";
    var defaultSize = "20%,*,0";
    if (parent.centercontent.cols != undefined) {
        parent.centercontent.cols = "";

        /*
            When a user resizes a frame, then attempts to minimize/maximize frame,
            size behavior is unexpected.  Setting a timeout before resizing works around this issue.
        */
        setTimeout(
            function () {
                parent.centercontent.cols = expanded ? defaultSize : collapseSize;
            },
            50);
    }
}

/**
 * Gets the boolean value of whether tree frame is expanded.
 */
function getTreeFrameExpanded() {
    return parent.centercontent.cols !== treeFrameCollapseSize;
}

/**
 * Modifies frame to show/hide messages depending on expanded parameter.
 * @param {boolean} expanded True if messages frame should be expanded, false otherwise.
 */
function showMessagesFrame(expanded) {
    var collapseSize = "*,8";
    var defaultSize = "*,30%";
    var main_content = top.document.getElementById("maincontent");
    main_content.rows = "";

    /*
        When a user resizes a frame, then attempts to minimize/maximize frame,
        size behavior is unexpected.  Setting a timeout before resizing works around this issue.
    */
    setTimeout(
        function () {
            main_content.rows = expanded ? defaultSize : collapseSize;
        },
        50);
}

/**
 * Gets the boolean value of whether messages frame is expanded.
 */
function getMessagesFrameExpanded() {
    return top.document.getElementById("maincontent").rows !== messagesFrameCollapseSize;
}

/**
 * Modifies frame to show/hide report header depending on expanded parameter.
 * @param {boolean} expanded True if report header frame should be expanded, false otherwise.
 */
function showReportHeaderFrame(expanded) {
    var collapseSize = "9,*";
    var defaultSize = "52,*";
    parent.main.rows = expanded ? defaultSize : collapseSize;
}

/**
 * Gets the boolean value of whether report header frame is expanded.
 */
function getReportHeaderFrameExpanded() {
    return parent.main.rows !== reportHeaderFrameCollapseSize;
}

window.addEventListener('message', function (e) {
    var message = e.data;
    if (message.command === messageConstants.command.toggleView) {
        // Handles situation when user clicks on arrow to hide or show a frame
        if (message.section === undefined || message.state === undefined) {
            return;
        }

        if (message.section === "messages") {
            showMessagesFrame(message.state);
        } else if (message.section === "tree") {
            showTreeFrame(message.state);
        } else if (message.section === "reportHeader") {
            showReportHeaderFrame(message.state)
        } else if (message.section === "all") {

            var allExpanded =
                getMessagesFrameExpanded() ||
                getTreeFrameExpanded() ||
                getReportHeaderFrameExpanded();

            showMessagesFrame(!allExpanded);
            showTreeFrame(!allExpanded);
            showReportHeaderFrame(!allExpanded);
        }
    } else if (message.command === messageConstants.command.scenario) {
        // Updates center content frame
        var conversionMessageIdParameter = message.node === null ? "" : "?conversionMessageId=" + message.conversionMessageId;
        document.getElementById("scenario").src = message.node + "/statistics.html" + conversionMessageIdParameter;
        window.frames["messages"].postMessage({ "command": messageConstants.command.updateMessagesFrame, "node": message.node, "descendantNodes": message.descendantNodes }, "*");
    } else if (message.command === messageConstants.command.treeNavigate) {
        // User has clicked on an object in the messages box and now we must click on appropriate object in the tree
        // The reason we can't use "nav" is because the selected tree object wouldn't reflect the scenario currently being shown
        // Depending on web browser, contentWindow may be undefined
        treeNavClick(message);
    } else if (message.command === messageConstants.command.messagesFilterChange) {
        this.frames["maincontent"].children["messages"].contentWindow.postMessage(message, "*");
    }
});