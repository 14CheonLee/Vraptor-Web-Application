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
    let socket_power = io.connect(location.protocol + "//" + document.domain + ":" + location.port + "/power");

    let current_fan_status = null;
    let chartlist = [];
    let nodepowlist = [];
    let myChart;

    for (let i = 0; i < 4; i++) {
        myChart = makechart("myChart" + i);
        chartlist[i] = myChart;
    }


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

    // Power socket
    socket_power.on("connect", function() {
        socket_power.emit("message", {data: "[Socket_Power] Connected ..."});
    });

    socket_power.on("response", function(msg) {
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
        console.log($("#fan_default_temperature").val());
        socket_fan.emit("set_fan_mode", {fan_auto_switch: 1 - current_fan_status, default_temperature: $("#fan_default_temperature").val()});
    });

    socket_fan.on("get_status_fan_speed", function(msg) {
        console.log(msg);
    });

    socket_fan.on("get_status_fan_mode", function(msg) {
        console.log(msg);
        
        if (msg["status"] === "ok") {
            current_fan_status = ["output_data"]["command_result"];

            if (current_fan_status === 0) {
                document.getElementById('current_status').innerHTML = "오토에요";
            } else {
                document.getElementById('current_status').innerHTML = "수동임";
            }
        } else {
            document.getElementById('current_status').innerHTML = "오류";
        }
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
        for (let i = 0 ; i < 4; i++) {
            chartlist[i].data.datasets[0].data[0] = msg["sensor"]["chassis_data"]["fan_data"][i]["speed"];
            chartlist[i].data.datasets[0].data[1] = 1000 - msg["sensor"]["chassis_data"]["fan_data"][i]["speed"];
            chartlist[i].update();
        }

        document.getElementById('node_1_temp').innerHTML = msg["sensor"]["chassis_data"]["temperature"];

        for (let i = 0; i < 2; i++) {
            nodepowlist[i] = msg["sensor"]["server_data"]["node_data"][i]["power_status"];

            if (nodepowlist[i] === true){
                document.getElementById('node_pow'+i).innerHTML = "전원 켜져있음";
            }
            else {
                document.getElementById('node_pow'+i).innerHTML = "전원 꺼져있음";
            }
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
    $(".node_pow_reset").click(function() {
        // 0 : reset | 1 : off | 2 : on
        let node_id = this.id;
        let node_number = node_id.split('_')[1];
        socket_power.emit("set_power_status", {node_number: node_number, power_status: 0});
    });

    $(".node_pow_off").click(function() {
        // 0 : reset | 1: off | 2 : on
        let node_id = this.id;
        let node_number = node_id.split('_')[1];
        socket_power.emit("set_power_status", {node_number: node_number, power_status: 1});
    });

    $(".node_pow_on").click(function() {
        // 0 : reset | 1: off | 2 : on
        let node_id = this.id;
        let node_number = node_id.split('_')[1];
        socket_power.emit("set_power_status", {node_number: node_number, power_status: 2});
    });

    socket_power.on("get_status_of_power_status", function(msg) {
        console.log(msg);
    });

    $(".monitor").click(function() {
        let node_id = this.id;
        let node_number = node_id.split('_')[1];

		socket_console.emit("monitor", {node_number: node_number});
    });

    $(".secure").click(function() {
        let node_id = this.id;
        let node_number = node_id.split('_')[1];

		socket_console.emit("secure", {node_number: node_number});
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

	socket_console.on("monitor_console", function(message) {
		let node_number = message["node_number"];
		let is_use = message["is_use"];

		if (is_use === true) {
            alert("Somebody use the console in Secure - Node Number : " + node_number);		
		}
		else {
            alert("Success to change monitoring mode - Node Number : " + node_number);	
		}

	});

    socket_console.on("secure_console", function(message) {
        let node_num = message["node_number"];
        let is_use = message["is_use"];

        // If somebody uses console
        if (is_use === true) {
            alert("Somebody uses the console in Secure already - Node Number : " + node_num);
        }
		else {
			//alert("Success blocking others console - Node Number : " + node_number);
			socket_console.emit("check", {node_number: node_num});
		}
        /**
        * @TODO:
        * else -> Open the terminal console
        */
    });

	socket_console.on("check", function(message) {
		let is_secure = message["is_secure"];
		let console = message["console"];
		let node_number = console["node_number"];

		if (is_secure === true) {
			alert("Success blocking others console - Node Number : " + node_number);	
		}
		else {
			alert("Somebody operate secure service - Node Number : " + node_number);		
		}
				
	});

});

function makechart(chart_id) {
    let ctx = document.getElementById(chart_id).getContext('2d');

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
                filter: function(tooltipItem, data) {
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

    return myChart;
}
