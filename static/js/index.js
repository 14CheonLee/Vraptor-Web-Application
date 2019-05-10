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

function console_click(){
    $('.btn-example').click(function () {
        var $href = $(this).attr('href');
        layer_popup($href);
    });
}

function layer_popup(el) {

    var $el = $(el);        //레이어의 id를 $el 변수에 저장
    var isDim = $el.prev().hasClass('dimBg');   //dimmed 레이어를 감지하기 위한 boolean 변수

    isDim ? $('.dim-layer').fadeIn() : $el.fadeIn();

    var $elWidth = ~~($el.outerWidth()),
        $elHeight = ~~($el.outerHeight()),
        docWidth = $(document).width(),
        docHeight = $(document).height();

    // 화면의 중앙에 레이어를 띄운다.
    if ($elHeight < docHeight || $elWidth < docWidth) {
        $el.css({
            marginTop: -$elHeight / 2,
            marginLeft: -$elWidth / 2
        })
    } else {
        $el.css({ top: 0, left: 0 });
    }

    $el.find('a.btn-layerClose').click(function () {
        isDim ? $('.dim-layer').fadeOut() : $el.fadeOut(); // 닫기 버튼을 클릭하면 레이어가 닫힌다.
        return false;
    });

    $('.layer .dimBg').click(function () {
        $('.dim-layer').fadeOut();
        return false;
    });

}

$('.example-default-value').each(function() {
    var default_value = this.value;
    $(this).focus(function() {
        if(this.value == default_value) {
            this.value = '';
        }
    });
    $(this).blur(function() {
        if(this.value == '') {
            this.value = default_value;
        }
    });
});

var input = document.getElementById("example-textarea");
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();
   document.getElementById("#myBtn").click();
  }
});

function text() {
    alert("dddd");
}

/***************************************************************************/

function sensor_test() {
    var dummy_data = {
        "sensor": {
            "chassis_data": {
                "temperature": 30,
                "fan_data": [
                    {
                        "fan_number": 0,
                        "speed": 200
                    },
                    {

                        "fan_number": 1,

                        "speed": 200

                    },

                    {

                        "fan_number": 2,

                        "speed": 200

                    },

                    {

                        "fan_number": 3,

                        "speed": 200

                    },

                    {

                        "fan_number": 4,

                        "speed": 200

                    },

                    {

                        "fan_number": 5,

                        "speed": 200

                    }

                ],

                "fan_auto_switch": true

            },

            "server_data": {

                "node_data": [

                    {

                        "node_number": 0,

                        "power_status": true

                    },

                    {

                        "node_number": 1,

                        "power_status": true

                    },

                    {

                        "node_number": 2,

                        "power_status": true

                    },

                    {

                        "node_number": 3,

                        "power_status": true

                    },

                    {

                        "node_number": 4,

                        "power_status": true

                    },

                    {

                        "node_number": 5,

                        "power_status": true

                    },

                    {

                        "node_number": 6,

                        "power_status": true

                    },

                    {

                        "node_number": 7,

                        "power_status": true

                    },

                    {

                        "node_number": 8,

                        "power_status": true

                    },

                    {

                        "node_number": 9,

                        "power_status": true

                    },

                    {

                        "node_number": 10,

                        "power_status": true

                    },

                    {

                        "node_number": 11,

                        "power_status": true

                    },

                    {

                        "node_number": 12,

                        "power_status": true

                    },

                    {

                        "node_number": 13,

                        "power_status": true

                    },

                    {

                        "node_number": 14,

                        "power_status": true

                    },

                    {

                        "node_number": 15,

                        "power_status": true

                    },

                    {

                        "node_number": 16,

                        "power_status": true

                    },

                    {

                        "node_number": 17,

                        "power_status": true

                    },

                    {

                        "node_number": 18,

                        "power_status": true

                    },

                    {

                        "node_number": 19,

                        "power_status": true

                    },

                    {

                        "node_number": 20,

                        "power_status": true

                    },

                    {

                        "node_number": 21,

                        "power_status": true

                    },

                    {

                        "node_number": 22,

                        "power_status": true

                    },

                    {

                        "node_number": 23,

                        "power_status": true

                    },

                    {

                        "node_number": 24,

                        "power_status": true

                    },

                    {

                        "node_number": 25,

                        "power_status": true

                    },

                    {

                        "node_number": 26,

                        "power_status": true

                    },

                    {

                        "node_number": 27,

                        "power_status": true

                    },

                    {

                        "node_number": 28,

                        "power_status": true

                    },

                    {

                        "node_number": 29,

                        "power_status": true

                    },

                    {

                        "node_number": 30,

                        "power_status": true

                    },

                    {

                        "node_number": 31,

                        "power_status": true

                    }

                ]

            },

            "timestamp": "2019.04.01.01.34.10"

        }
    };

    document.getElementById('node1test').innerHTML = dummy_data["sensor"]["chassis_data"]["temperature"];
}
