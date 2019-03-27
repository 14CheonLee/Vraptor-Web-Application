window.onload = function () {
    $('.nodes_temp').hide();
    $('.nodes_status').hide();

    $('.node_1_on').hide();
    $('.node_1_off').hide();
};

function change_to_temp() {
    $(document).ready(function () {
        $('.nodes_temp').show();
        $('.nodes_status').hide();
        $('.nodes').hide();
    });
}

function change_to_status() {
    $(document).ready(function () {
        $('.nodes_temp').hide();
        $('.nodes_status').show();
        $('.nodes').hide();
    });
}

function status_on() {
    $(document).ready(function () {
        $('.node_1').hide();
        $('.node_1_on').show();
        $('.node_1_off').hide();
    });
}

function status_off() {
    $(document).ready(function () {
        $('.node_1').hide();
        $('.node_1_on').hide();
        $('.node_1_off').show();
    });
}