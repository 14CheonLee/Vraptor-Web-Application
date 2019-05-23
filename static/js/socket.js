/**
 * Socket
 *
 * @TODO
 * Should Modify dummy data
 */
$(window).on("unload", function() {
     $.ajax({
         type: "GET",
         url: "/close_window",
         async: false,
         data: {node_number: 0}
     });
 });

$(document).ready(function() {
    let socket_fan = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/fan");
    let socket_sensor = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/sensor");
    let socket_console = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/console");

    let current_fan_status = null;

    let ctx = document.getElementById("myChart").getContext('2d');
    let myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ["Fanspeed", "None"],
            datasets: [{
                backgroundColor: [
                    "#2ecc71",
                    "#3498db"
                ],
                hiddenLegend: true,
                data: [0, 0]
            }]
        },
        options: {
            tooltips: {
                filter: function (tooltipItem, data) {
                    let label = data.labels[tooltipItem.index];
                    if (label === "None") {
                        return false;
                    } else {
                        return true;
                    }
                }
            }
        }
    });


    /**
     * Checking Connection
     */
    // Fan socket
    socket_fan.on("connect", function() {
        socket_fan.emit("message", {data: "[Socket_Fan] Connected ..."});
    });

    socket_fan.on("response", function(msg) {
        console.log(msg);
    });

    // Sensor socket
    socket_sensor.on("connect", function() {
        socket_sensor.emit("message", {data: "[Socket_Sensor] Connected ..."});
    });

    socket_sensor.on("response", function(msg) {
        console.log(msg);
    });

    // Console socket
    socket_console.on("connect", function() {
        socket_console.emit("message", {data: "[Socket_Console] Connected ..."});
    });

    socket_console.on("response", function(msg) {
        console.log(msg);
    });

    /**
     * Test
     */
    // (Test) If click the button
    $("#fan_btn").click(function() {
        socket_fan.emit("message", {data: "Clicked fan button"});
    });

    $("#sensor_btn").click(function() {
        socket_sensor.emit("message", {data: "Clicked sensor button"});
    });

    /**
     * Fan
     */
    $("#set_fan_speed_btn").click(function() {
        /**
         * @TODO
         * Should modify data
         */
        socket_fan.emit("set_fan_speed", {fan_number: 3, speed: 200});
    });

    $("#set_fan_mode_btn").click(function() {
        socket_fan.emit("set_fan_mode", {fan_auto_switch: !current_fan_status});
    });

    socket_fan.on("get_status_fan_speed", function(msg) {
        console.log(msg);
    });

    socket_fan.on("get_status_fan_mode", function(msg) {
        if (msg["status"] === "ok"){
            current_fan_status = msg["data"]["fan_auto_switch"];

            if (current_fan_status === true) {
                document.getElementById('current_status').innerHTML = "오토에요";
            } else {
                document.getElementById('current_status').innerHTML = "수동임";
            }
        } else {
            document.getElementById('current_status').innerHTML = "오류";
        }
        console.log(current_fan_status);
    });

    /**
     * Sensor
     */
    $("#get_all_data_btn").click(function() {
        /**
         * @TODO
         * Should modify data
         */
        socket_sensor.emit("get_all_data");
    });

    socket_sensor.on("get_all_sensor_data", function(msg) {
        myChart.data.datasets[0].data[0] = msg["sensor"]["chassis_data"]["fan_data"][0]["speed"];
        myChart.data.datasets[0].data[1] = 1000 - msg["sensor"]["chassis_data"]["fan_data"][0]["speed"];
        myChart.update();

        document.getElementById('node_1_temp').innerHTML = msg["sensor"]["chassis_data"]["temperature"];

        let node1_pow = msg["sensor"]["server_data"]["node_data"][0]["power_status"];

        if (node1_pow === true){
            document.getElementById('node1_pow').innerHTML = "전원 켜져있음";
        }
        else {
            document.getElementById('node1_pow').innerHTML = "전원 꺼져있음";
        }

        console.log(msg);
    });

    /**
     * Power
     */
    /**
     * @TODO
     * Should modify this name
     */
    $("#node1_pow_reset").click(function() {
        socket_sensor.emit("message", {data: "Clicked node1 reset button"});
    });

    /**
     * Console
     * @TODO
     * Should modify node_number
     */
    $(".console_choice").click(function() {
        var node1 = this.id;
        var realnode = node1.split('_')[1];

        socket_console.emit("check", {node_number: realnode});
    });

    $("#console_close").click(function() {
        socket_console.emit("close", {node_number: 0});
    });

    $("#console_input_id").keydown(function(key) {
        if (key.keyCode === 13) {
            console.log($("#console_input_id").val());

            socket_console.emit("send", {node_number: 0, cmd: $("#console_input_id").val()});
            $('#console_input_id').val('');
        }
    });

    socket_console.on("receive", function(data) {
        let node_number = data["node_number"];
        let message = data["message"];

        $('#example').append(message);
        $("#example").scrollTop($("#example")[0].scrollHeight);
    });

    socket_console.on("check_console", function(message) {
        let node_number = message["node_number"];
        let is_use = message["is_use"];

        // If somebody uses console
        if (is_use === true) {
            alert("Somebody uses the console - Node Number : " + node_number);
        }
        /**
        * @TODO:
        * else -> Open the terminal console
        */
    });
});
